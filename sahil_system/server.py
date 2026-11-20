"""Sahil System web server (Flask).

Chalane ke liye:  gunicorn --chdir sahil_system server:app --workers 1 --threads 4
Zaroori env (Render par):  GITHUB_TOKEN, ADMIN_PIN
"""
import datetime
import hmac
import os
import re
import threading
import time

from flask import Flask, jsonify, request, send_from_directory
from werkzeug.exceptions import HTTPException

import api
import backtest
import store

HERE = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=os.path.join(HERE, "static"), static_url_path="/static")

ADMIN_PIN = os.environ.get("ADMIN_PIN", "")
FORMULAS = set("23456789")
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))


def today_ist():
    """Render server UTC me chalta hai; weekday/date India (IST) ke hisab se chahiye."""
    return datetime.datetime.now(IST).date()

_fail = {}                 # ip -> [galat PIN ka waqt]
_fail_lock = threading.Lock()
MAX_FAILS, WINDOW = 8, 600  # 10 minute me 8 galat PIN par rok


def err(msg, code=400):
    return jsonify({"error": msg}), code


def reply(result):
    """(dict, status) ya Response ko Flask response banao."""
    if isinstance(result, tuple) and isinstance(result[0], dict):
        return jsonify(result[0]), result[1]
    return result


def _locked_out(ip):
    now = time.time()
    with _fail_lock:
        _fail[ip] = [t for t in _fail.get(ip, []) if now - t < WINDOW]
        return len(_fail[ip]) >= MAX_FAILS


def _note_fail(ip):
    with _fail_lock:
        _fail.setdefault(ip, []).append(time.time())


def check_write_access():
    """None = allowed, warna ({"error": ...}, status)."""
    if not ADMIN_PIN:
        if store.enabled():
            return {"error": "Server par ADMIN_PIN set nahi hai, isliye likhna band hai."}, 503
        return None  # local dev mode
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "?").split(",")[0].strip()
    if _locked_out(ip):
        return {"error": "Bahut galat PIN. 10 minute baad try karo."}, 429
    given = request.headers.get("X-Admin-Pin", "")
    if not hmac.compare_digest(given.encode(), ADMIN_PIN.encode()):
        _note_fail(ip)
        return {"error": "PIN galat hai."}, 401
    return None


def valid_date(s):
    try:
        return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", s or "")) and bool(datetime.date.fromisoformat(s))
    except ValueError:
        return False


def num(v):
    """0-99 ka int, warna None. (0 matlab 00)"""
    if isinstance(v, bool):
        return None
    try:
        n = int(v)
    except (TypeError, ValueError):
        return None
    return n if 0 <= n <= 99 else None


def four(body):
    vals = [num(body.get(k)) for k in ("fd", "gb", "gl", "ds")]
    return None if None in vals else vals


def run_read(cmd, args=None):
    try:
        store.pull()
        return jsonify(api.COMMANDS[cmd](args or {}))
    except store.StoreError as e:
        return err(str(e), 502)


def run_write(cmd, args, message):
    denied = check_write_access()
    if denied:
        return denied
    try:
        return store.write_op(lambda: api.COMMANDS[cmd](args), message), 200
    except store.StoreError as e:
        return {"error": str(e)}, 502


# ───────────── pages ─────────────

@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/healthz")
def healthz():
    return jsonify({"status": "ok"})


@app.get("/api/sahil/config")
def config():
    return jsonify({"pinRequired": bool(ADMIN_PIN), "github": store.enabled(), "today": str(today_ist())})


@app.post("/api/sahil/auth")
def auth():
    return reply(check_write_access() or ({"ok": True}, 200))


# ───────────── records ─────────────

@app.get("/api/sahil/records")
def records():
    return run_read("records_list")


@app.post("/api/sahil/records")
def records_add():
    body = request.get_json(silent=True) or {}
    vals = four(body)
    if not valid_date(body.get("date")) or vals is None:
        return err("Date (YYYY-MM-DD) aur FD GB GL DS (0-99) sahi dalo.")
    args = dict(date=body["date"], fd=vals[0], gb=vals[1], gl=vals[2], ds=vals[3])
    payload, code = run_write("records_add", args, f"data: add record {body['date']}")
    if code == 200 and payload.get("conflict"):
        return err(payload["message"], 409)
    return reply((payload, code))


@app.put("/api/sahil/records/<date>")
def records_update(date):
    body = request.get_json(silent=True) or {}
    vals = four(body)
    if not valid_date(date) or vals is None:
        return err("Date aur FD GB GL DS (0-99) sahi dalo.")
    args = dict(date=date, fd=vals[0], gb=vals[1], gl=vals[2], ds=vals[3])
    payload, code = run_write("records_update", args, f"data: update record {date}")
    if code == 200 and payload.get("notFound"):
        return err(payload["message"], 404)
    return reply((payload, code))


# ───────────── pending (ek-ek karke result) ─────────────

@app.get("/api/sahil/pending")
def pending():
    return run_read("pending_get")


@app.post("/api/sahil/pending")
def pending_save():
    body = request.get_json(silent=True) or {}
    value = num(body.get("value"))
    if not valid_date(body.get("date")) or body.get("field") not in ("fd", "gb", "gl", "ds") or value is None:
        return err("date, field (fd/gb/gl/ds) aur value (0-99) sahi dalo.")
    args = dict(date=body["date"], field=body["field"], value=value)
    return reply(run_write("pending_save", args, f"data: pending {body['date']} {body['field']}"))


# ───────────── prediction ─────────────

@app.post("/api/sahil/predict")
def predict():
    body = request.get_json(silent=True) or {}
    vals = four(body)
    formula = body.get("formula", ["2", "5", "6"])
    game_date = body.get("gameDate") or str(today_ist())
    if vals is None or not valid_date(game_date):
        return err("FD GB GL DS (0-99) aur gameDate sahi dalo.")
    if not isinstance(formula, list) or not set(formula) <= FORMULAS:
        return err("formula me sirf 2 se 9 tak ke number.")
    args = dict(fd=vals[0], gb=vals[1], gl=vals[2], ds=vals[3], formula=formula, gameDate=game_date)
    return reply(run_write("predict", args, f"data: prediction {game_date}"))


@app.get("/api/sahil/predictions")
def predictions():
    return run_read("predictions_list")


@app.post("/api/sahil/predictions/check")
def predictions_check():
    body = request.get_json(silent=True) or {}
    vals = four(body)
    if not valid_date(body.get("date")) or vals is None:
        return err("date aur FD GB GL DS (0-99) sahi dalo.")
    args = dict(date=body["date"], fd=vals[0], gb=vals[1], gl=vals[2], ds=vals[3])
    return reply(run_write("predictions_check", args, f"data: check prediction {body['date']}"))


@app.get("/api/sahil/stats")
def stats():
    return run_read("stats")


@app.get("/api/sahil/backtest/all")
def backtest_all():
    try:
        store.pull()
        return jsonify(backtest.report())
    except store.StoreError as e:
        return err(str(e), 502)


@app.get("/api/sahil/backtest")
def backtest_view():
    formula = [c for c in request.args.get("formula", "256") if c in FORMULAS]
    try:
        store.pull()
        return jsonify(backtest.run(formula))
    except store.StoreError as e:
        return err(str(e), 502)


@app.errorhandler(Exception)
def on_error(e):
    if isinstance(e, HTTPException):
        return err(e.description, e.code or 500)
    app.logger.exception("server error")
    return err("Server me galti aayi. Dobara try karo.", 500)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
