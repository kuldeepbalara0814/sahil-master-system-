"""Sahil Lab web server (Flask).

Chalane ke liye:  gunicorn lab_server:app --workers 1 --threads 4 --timeout 120 --bind 0.0.0.0:$PORT
Env:  GITHUB_TOKEN (likhne ke liye), ADMIN_PIN (likhne wale kaam ka PIN), GITHUB_REPO, GITHUB_BRANCH,
      LAB_SYNC=0 (sirf local files), LAB_DATA_DIR
"""
import datetime as dt
import hmac
import json
import os
import shutil
import threading
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
SYNC_ON = os.environ.get("LAB_SYNC", "1") != "0" and bool(os.environ.get("GITHUB_REPO") or os.environ.get("RENDER"))
DATA_DIR = os.environ.get("LAB_DATA_DIR") or (os.path.join("/tmp", "sahil_lab_data") if SYNC_ON else os.path.join(ROOT, "data"))
os.makedirs(DATA_DIR, exist_ok=True)
if DATA_DIR != os.path.join(ROOT, "data"):                      # shuru ki files repo se
    for f in os.listdir(os.path.join(ROOT, "data")):
        if f.endswith((".csv", ".json")) and not os.path.exists(os.path.join(DATA_DIR, f)):
            shutil.copy(os.path.join(ROOT, "data", f), os.path.join(DATA_DIR, f))
os.environ["LAB_DATA_FILE"] = os.path.join(DATA_DIR, "results.csv")

from flask import Flask, Response, jsonify, request, send_file, send_from_directory   # noqa: E402
from werkzeug.exceptions import HTTPException                              # noqa: E402

from lab import backtest, data, export_xlsx, friends, gh, idea, monitor, paper, picks, update            # noqa: E402

app = Flask(__name__, static_folder=os.path.join(ROOT, "lab_static"), static_url_path="/static")
ADMIN_PIN = os.environ.get("ADMIN_PIN", "")
SYNC = gh.Sync(DATA_DIR, os.environ.get("GITHUB_REPO", "kuldeepbalara0814/sahil-master-system-"),
               os.environ.get("GITHUB_BRANCH", "main"), os.environ.get("GITHUB_TOKEN", "")) if SYNC_ON else None
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
_lock = threading.RLock()
_cache = {"key": None, "rows": None, "friends": None}
_fail, MAX_FAILS, WINDOW = {}, 8, 600


def err(msg, code=400):
    return jsonify({"error": msg}), code


def jpath(name):
    return os.path.join(DATA_DIR, name)


def jload(name, default):
    try:
        with open(jpath(name), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def jsave(name, obj):
    update._save_json(jpath(name), obj)


def refresh():
    """GitHub se taaza files (agar sync on ho)."""
    if SYNC:
        try:
            SYNC.pull()
        except gh.SyncError as e:
            app.logger.warning("sync: %s", e)


def state():
    refresh()
    rows = data.load(jpath("results.csv"))
    key = (len(rows), rows[-1][0])
    with _lock:
        if _cache["key"] != key:
            _cache.update(key=key, rows=rows, friends=friends.Friends(rows))
        return _cache["rows"], _cache["friends"]


def persist(names, message):
    """GitHub par save. Sync on ho aur token na ho to error (warna restart par data gayab ho jaata)."""
    if SYNC:
        SYNC.push(names, message)        # token na ho to SyncError
        return True
    return False


def check_write():
    if not ADMIN_PIN:
        if SYNC_ON:
            return {"error": "Server par ADMIN_PIN set nahi hai, isliye likhna band hai."}, 503
        return None
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "?").split(",")[0].strip()
    now = time.time()
    _fail[ip] = [t for t in _fail.get(ip, []) if now - t < WINDOW]
    if len(_fail[ip]) >= MAX_FAILS:
        return {"error": "Bahut galat PIN. 10 minute baad try karo."}, 429
    if not hmac.compare_digest(request.headers.get("X-Admin-Pin", "").encode(), ADMIN_PIN.encode()):
        _fail[ip].append(now)
        return {"error": "PIN galat hai."}, 401
    return None


def guarded(fn):
    def wrap(*a, **k):
        denied = check_write()
        if denied:
            return jsonify(denied[0]), denied[1]
        return fn(*a, **k)
    wrap.__name__ = fn.__name__
    return wrap


def num(v):
    try:
        n = int(v)
    except (TypeError, ValueError):
        return None
    return n if 0 <= n <= 99 else None


# ---------------- pages / status ----------------
@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/healthz")
def healthz():
    return jsonify({"status": "ok"})


@app.get("/api/status")
def status():
    rows, _ = state()
    flog = jload("fetch_log.json", [])
    return jsonify({"last_date": rows[-1][0].isoformat(), "days": len(rows), "play_date": data.play_date(rows).isoformat(),
                    "github": bool(SYNC), "can_write": bool(SYNC and SYNC.can_write) or not SYNC_ON, "pin_required": bool(ADMIN_PIN),
                    "last_fetch": flog[-1] if flog else None, "today_ist": dt.datetime.now(IST).date().isoformat()})


# ---------------- dost ----------------
@app.get("/api/friends/<int:x>")
def api_friends(x):
    if not 0 <= x <= 99:
        return err("0 se 99 ka number")
    _, fr = state()
    return jsonify(fr.table(x))


@app.get("/api/drift")
def api_drift():
    refresh()                                   # GitHub se taaza drift_log
    log = jload("drift_log.json", [])
    return jsonify(log[-14:][::-1])


@app.get("/api/overview/<period>")
def api_overview(period):
    """Har number ka sabse bada dost (poora / pichle 3 mahine / is mahina) - ek nazar me."""
    if period not in ("poora", "last3m", "month"):
        return err("period galat")
    _, fr = state()
    out = []
    for x in range(100):
        t = friends.top_friends(fr.cnt[period], x, 3)
        out.append({"number": x, "top": [{"n": f["n"], "together": f["together"]} for f in t], "seen": int(fr.cnt[period][2][x])})
    return jsonify(out)


# ---------------- record (range + Excel) ----------------
def _range():
    try:
        a = dt.date.fromisoformat(request.args["from"]) if request.args.get("from") else None
        b = dt.date.fromisoformat(request.args["to"]) if request.args.get("to") else None
    except ValueError:
        return None, None, "Tarikh galat (YYYY-MM-DD)"
    if a and b and a > b:
        return None, None, "'Se' tarikh 'Tak' se badi hai"
    return a, b, None


@app.get("/api/record")
def api_record():
    a, b, e = _range()
    if e:
        return err(e)
    rows, _ = state()
    sel = export_xlsx.select(rows, a, b)
    return jsonify({"first": rows[0][0].isoformat(), "last": rows[-1][0].isoformat(), "count": len(sel),
                    "rows": [[d.isoformat(), *v] for d, v, _ in sel]})


@app.get("/api/export/record.xlsx")
def api_export():
    a, b, e = _range()
    if e:
        return err(e)
    rows, _ = state()
    sel = export_xlsx.select(rows, a, b)
    if not sel:
        return err("Is range me koi din nahi")
    blob = export_xlsx.build(rows, a, b)
    name = f"SahilLab_Record_{sel[0][0].isoformat()}_to_{sel[-1][0].isoformat()}.xlsx"
    return Response(blob, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": f'attachment; filename="{name}"'})


# ---------------- lab (idea backtest) ----------------
_lab_cache = {}


@app.post("/api/lab/parse")
def lab_parse():
    text = str((request.get_json(silent=True) or {}).get("text", ""))[:400]
    return jsonify(idea.parse(text))


@app.post("/api/lab/test")
def lab_test():
    raw = (request.get_json(silent=True) or {}).get("spec") or {}
    try:
        spec = idea.clean(raw)
    except (ValueError, TypeError, KeyError) as e:
        return err(str(e))
    rows, _ = state()
    key = (json.dumps(spec, sort_keys=True), len(rows), rows[-1][0])
    with _lock:
        res = _lab_cache.get(key)
    if res is None:
        res = backtest.run(rows, spec)
        with _lock:
            if len(_lab_cache) > 40:
                _lab_cache.clear()
            _lab_cache[key] = res
    return jsonify({"spec": spec, "explain": idea.explain(spec), "result": res, "asof": rows[-1][0].isoformat()})


@app.get("/api/lab/ideas")
def lab_ideas():
    refresh()
    return jsonify(jload("ideas.json", []))


@app.post("/api/lab/save")
@guarded
def lab_save():
    b = request.get_json(silent=True) or {}
    try:
        spec = idea.clean(b.get("spec") or {})
    except (ValueError, TypeError, KeyError) as e:
        return err(str(e))
    ideas = jload("ideas.json", [])
    if len(ideas) >= 60:
        return err("60 se zyada idea save nahi ho sakte. Purane hata do.")
    name = str(b.get("name") or idea.explain(spec))[:80]
    ideas.insert(0, {"id": int(time.time() * 1000), "name": name, "text": str(b.get("text", ""))[:300], "spec": spec,
                     "saved": dt.datetime.now(IST).isoformat(timespec="minutes"), "summary": b.get("summary")})
    jsave("ideas.json", ideas)
    try:
        persist(["ideas.json"], "lab: idea save")
    except gh.SyncError as e:
        return err(str(e), 502)
    return jsonify({"ok": True, "count": len(ideas)})


@app.post("/api/lab/delete")
@guarded
def lab_delete():
    iid = (request.get_json(silent=True) or {}).get("id")
    ideas = [x for x in jload("ideas.json", []) if x.get("id") != iid]
    jsave("ideas.json", ideas)
    try:
        persist(["ideas.json"], "lab: idea delete")
    except gh.SyncError as e:
        return err(str(e), 502)
    return jsonify({"ok": True, "count": len(ideas)})


# ---------------- aaj ki list ----------------
@app.get("/api/today")
def api_today():
    rows, _ = state()
    known = [num(v) for v in request.args.get("known", "").split(",") if v.strip() != ""]
    if None in known or len(known) > 3:
        return err("aaj ke result (FD, GB, GL) 0-99 ke number me")
    plan = picks.daily_plan(rows, known)
    plan["known"] = known
    plan["last_line"] = {"date": rows[-1][0].isoformat(), "results": dict(zip(data.GAMES, rows[-1][1]))}
    return jsonify(plan)


# ---------------- paper trading ----------------
def ledger():
    return jload("paper_ledger.json", None) or paper.new_ledger()


@app.get("/api/paper")
def api_paper():
    rows, _ = state()
    L = ledger()
    paper.settle(L, rows)
    recent = sorted(L["bets"], key=lambda b: (b["date"], b["game"]), reverse=True)[:60]
    return jsonify({"capital": L["capital"], "strategies": paper.STRATEGIES, "summary": paper.summary_all(L), "recent": recent})


def _save_ledger(L, msg):
    jsave("paper_ledger.json", L)
    return persist(["paper_ledger.json"], msg)


@app.post("/api/paper/place")
@guarded
def paper_place():
    b = request.get_json(silent=True) or {}
    rows, _ = state()
    L = ledger()
    play = data.play_date(rows).isoformat()
    try:
        stake = int(b.get("stake", 5))
        added = 0
        if b.get("strategy") == "manual":
            ns = [num(v) for v in b.get("numbers", [])]
            if not ns or None in ns:
                return err("numbers 0-99 me do")
            for g in b.get("games", []):
                for n in ns:
                    added += paper.place(L, "manual", play, g, n, stake)
        elif b.get("strategy") == "auto":
            added = paper.auto_place(L, rows, stake)
        elif b.get("strategy") == "list10":
            known = [num(v) for v in b.get("known", [])]
            if None in known:
                return err("known galat")
            added = paper.place_sequential(L, rows, known, stake)
        else:
            return err("strategy galat")
    except ValueError as e:
        return err(str(e))
    try:
        saved = _save_ledger(L, f"paper: {added} bet {play}")
    except gh.SyncError as e:
        return err(str(e), 502)
    return jsonify({"added": added, "play_date": play, "saved_to_github": saved})


# ---------------- monitor ----------------
@app.get("/api/monitor")
def api_monitor():
    rows, _ = state()
    m = jload("monitor.json", None)
    if not m or m.get("asof") != rows[-1][0].isoformat():
        m = monitor.health(rows)
        jsave("monitor.json", m)
    return jsonify(m)


# ---------------- fetch / download ----------------
@app.post("/api/fetch")
@guarded
def api_fetch():
    stake = int((request.get_json(silent=True) or {}).get("stake", 5))
    try:
        paper.check_stake(stake)
        with _lock:
            if SYNC:
                SYNC.pull(force=True)
            rep = update.run(fetch=True, stake=stake, data_dir=DATA_DIR, pause=1.0)
            rep["saved_to_github"] = persist(gh.FILES, f"manual fetch {rep['last_date']}") if rep["added"] or rep["settled"] or rep["new_bets"] else False
    except (ValueError, gh.SyncError) as e:
        return err(str(e), 502)
    _cache["key"] = None
    return jsonify(rep)


@app.get("/api/download/results.csv")
def download():
    state()
    return send_file(jpath("results.csv"), mimetype="text/csv", as_attachment=True, download_name="results.csv")


@app.errorhandler(Exception)
def on_error(e):
    if isinstance(e, HTTPException):
        return err(e.description, e.code or 500)
    app.logger.exception("server error")
    return err("Server me galti aayi. Dobara try karo.", 500)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
