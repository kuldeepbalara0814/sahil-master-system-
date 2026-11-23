"""Sahil Lab web server (Flask).

Chalane ke liye:  gunicorn lab_server:app --workers 1 --threads 4 --timeout 120 --bind 0.0.0.0:$PORT
Env:  GITHUB_TOKEN (likhne ke liye), ADMIN_PIN (likhne wale kaam ka PIN), GITHUB_REPO, GITHUB_BRANCH,
      LAB_SYNC=0 (sirf local files), LAB_DATA_DIR
"""
import calendar
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

from lab import active, backtest, baar, band, data, export_all, export_xlsx, friends, gapchain, gh, idea, monitor, paper, picks, rank, scan_view, scanner, update            # noqa: E402

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


_auto = {"t": 0.0, "running": False}


def expected_last(now):
    """Is waqt tak jiski poori line (DS samet, subah 5:30 ko khulta hai) aa chuki honi chahiye."""
    d = now.date() - dt.timedelta(days=1 if (now.hour, now.minute) >= (5, 45) else 2)
    while data.is_last_day(d):                        # mahine ke aakhri din chhuti, line nahi
        d -= dt.timedelta(days=1)
    return d


def _auto_run():
    try:
        with _lock:
            SYNC.pull(force=True)
            rep = update.run(fetch=True, stake=5, data_dir=DATA_DIR, pause=1.0)
            if rep["added"] or rep["settled"] or rep["new_bets"]:
                persist(gh.FILES, f"auto fetch {rep['last_date']}")
    except Exception:
        app.logger.exception("auto fetch fail")
    finally:
        _auto["running"] = False
        _cache["key"] = None


def maybe_auto_fetch(rows):
    """GitHub ka roz wala schedule der se chalta hai. Isliye jab koi app kholta hai aur naya din baaki ho to server khud le aata hai (20 min me ek baar)."""
    if not (SYNC and SYNC.can_write) or _auto["running"] or time.time() - _auto["t"] < 1200:
        return False
    if rows[-1][0] >= expected_last(dt.datetime.now(IST)):
        return False
    _auto["t"], _auto["running"] = time.time(), True
    threading.Thread(target=_auto_run, daemon=True).start()
    return True


@app.get("/api/status")
def status():
    rows, _ = state()
    fetching = maybe_auto_fetch(rows)
    flog = jload("fetch_log.json", [])
    return jsonify({"last_date": rows[-1][0].isoformat(), "days": len(rows), "play_date": data.play_date(rows).isoformat(),
                    "github": bool(SYNC), "can_write": bool(SYNC and SYNC.can_write) or not SYNC_ON, "pin_required": bool(ADMIN_PIN),
                    "last_fetch": flog[-1] if flog else None, "auto_fetching": fetching, "today_ist": dt.datetime.now(IST).date().isoformat()})


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


def _gap(rows):
    """?gaps=3,4,5&days=15&show=all  -> gapchain natija (gaps na ho to None)."""
    if request.args.get("gaps") is None:
        return None
    try:
        gaps = [int(x) for x in request.args["gaps"].split(",") if x.strip()]
        days = int(request.args.get("days", 15))
    except ValueError:
        raise ValueError("gaps/days sankhya hone chahiye")
    if not gaps:
        raise ValueError("Kam se kam ek gap chuno")
    return gapchain.find(rows, gaps, days, show=request.args.get("show", "all"))


@app.get("/api/baar/all")
def api_baar_all():
    """Saatho din ki tokri (Ravi se Shani) ek saath, kab-kab aaya samet."""
    rows, _ = state()
    try:
        days = int(request.args.get("days", 365))
    except ValueError:
        return err("days sankhya hona chahiye")
    if days not in (0, 365, 1095, 1825):
        return err("days 365, 1095, 1825 ya 0 (poora) hona chahiye")
    r = baar.all_days(rows, days)
    r["play_date"] = data.play_date(rows).isoformat()
    r["today_weekday"] = data.play_date(rows).weekday()
    return jsonify(r)


@app.get("/api/baar")
def api_baar():
    """?weekday=0..6 (nahi diya to aaj khelne ki tarikh ka) &days=365|1095|0(poora). Is baar ki tokri (6 number + palat)."""
    rows, _ = state()
    play = data.play_date(rows)
    try:
        wd = int(request.args.get("weekday", play.weekday()))
        days = int(request.args.get("days", 365))
    except ValueError:
        return err("weekday aur days sankhya hone chahiye")
    if not 0 <= wd <= 6 or days not in (0, 365, 1095, 1825):
        return err("weekday 0-6 (Somvar=0) aur days 365, 1095, 1825 ya 0 (poora) hona chahiye")
    r = baar.tokri(rows, wd, days)
    r["play_date"] = play.isoformat()
    r["is_today"] = wd == play.weekday()
    return jsonify(r)


@app.get("/api/band")
def api_band():
    try:
        m = max(1, min(int(request.args.get("min", 15)), 400))
    except ValueError:
        return err("min sankhya hona chahiye")
    rows, _ = state()
    r = band.status(rows, m)
    r["history"] = band.history(rows, m)
    return jsonify(r)


# ---------------- pattern window (lamba mahine-jorna table + rang save) ----------------
def _months(start, n):
    out, y, m = [], start.year, start.month
    for _ in range(n):
        out.append((y, m))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


@app.get("/api/pattern/sheet")
def api_pattern_sheet():
    """?from=YYYY-MM&months=3[&gaps=3,4&days=15] -> har calendar din ki ek row (mahine upar-niche jude)."""
    rows, _ = state()
    try:
        if request.args.get("from"):
            y, m = [int(x) for x in request.args["from"].split("-")[:2]]
            start = dt.date(y, m, 1)
        else:
            start = None
        n = max(1, min(int(request.args.get("months", 3)), 12))
        gap = _gap(rows)
    except (ValueError, TypeError) as e:
        return err(str(e) or "from/months galat")
    if start is None:                                         # pichle n mahine (aakhri line ka mahina samet)
        ly, lm = rows[-1][0].year, rows[-1][0].month
        k = ly * 12 + lm - 1 - (n - 1)
        start = dt.date(k // 12, k % 12 + 1, 1)
    by = {d: v for d, v, _ in rows}
    out = []
    for y, m in _months(start, n):
        for day in range(1, calendar.monthrange(y, m)[1] + 1):
            d = dt.date(y, m, day)
            out.append([d.isoformat(), by.get(d)])
    res = {"from": start.strftime("%Y-%m"), "months": n, "last": rows[-1][0].isoformat(), "days": out}
    if gap:
        res["gap"] = {k: gap[k] for k in ("start", "end", "gaps", "legend", "chains")}
        res["marks"] = gapchain.marks(gap)
    return jsonify(res)


@app.get("/api/pattern/boards")
def api_boards():
    return jsonify(jload("boards.json", []))


@app.post("/api/pattern/save")
@guarded
def api_board_save():
    b = request.get_json(silent=True) or {}
    cells = b.get("cells") or {}
    if not isinstance(cells, dict) or len(cells) > 4000:
        return err("Rang wale cell galat ya bahut zyada")
    clean = {}
    for k, c in cells.items():
        try:
            d, g = str(k).split("|")
            dt.date.fromisoformat(d)
            assert int(g) in range(4) and len(str(c)) == 6 and int(str(c), 16) >= 0
        except (ValueError, AssertionError):
            return err("Cell ya rang galat: " + str(k)[:20])
        clean[f"{d}|{int(g)}"] = str(c).upper()
    boards = jload("boards.json", [])
    name = str(b.get("name") or "Mera pattern")[:60]
    bid = b.get("id")
    item = {"id": bid or int(time.time() * 1000), "name": name, "from": str(b.get("from", ""))[:7], "months": int(b.get("months", 3)),
            "cells": clean, "saved": dt.datetime.now(IST).isoformat(timespec="minutes")}
    if bid and any(x.get("id") == bid for x in boards):
        boards = [item if x.get("id") == bid else x for x in boards]
    else:
        if len(boards) >= 40:
            return err("40 se zyada pattern save nahi ho sakte. Purane hata do.")
        boards.insert(0, item)
    jsave("boards.json", boards)
    try:
        persist(["boards.json"], "pattern: save")
    except gh.SyncError as e:
        return err(str(e), 502)
    return jsonify({"ok": True, "id": item["id"], "count": len(boards)})


@app.get("/api/pattern/xlsx")
def api_board_xlsx():
    """Save kiye hue board ka Excel: ?id=<board id>"""
    rows, _ = state()
    bid = request.args.get("id", "")
    b = next((x for x in jload("boards.json", []) if str(x.get("id")) == bid), None)
    if not b:
        return err("Ye pattern save kiya hua nahi mila", 404)
    name = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in str(b.get("name", "Pattern")))[:60] or "Pattern"
    return Response(export_all.board_xlsx(rows, b), mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": f'attachment; filename="{name}.xlsx"'})


@app.post("/api/pattern/delete")
@guarded
def api_board_delete():
    bid = (request.get_json(silent=True) or {}).get("id")
    boards = [x for x in jload("boards.json", []) if x.get("id") != bid]
    jsave("boards.json", boards)
    try:
        persist(["boards.json"], "pattern: delete")
    except gh.SyncError as e:
        return err(str(e), 502)
    return jsonify({"ok": True, "count": len(boards)})


# ---------------- pattern scan (sikhaye hue pattern roz apne aap) ----------------
def save_scan(rep, source="auto", push=False):
    """Scan save karo + active_log me milao. push=True (manual) to GitHub par bhi (galti response na roke)."""
    names = ["patterns_today.json"]
    try:                                                       # merge pehle: wo items par "new" nishan lagata hai
        jsave("active_log.json", active.merge(jload("active_log.json", None) or active.new_log(), rep, source=source))
        names.append("active_log.json")
    except Exception:
        app.logger.exception("active log merge fail")
    jsave("patterns_today.json", rep)
    if push:
        try:
            persist(names, "pattern scan (manual)")
        except Exception as e:
            app.logger.warning("scan persist: %s", e)


def scan_today(rows):
    """Aaj ka scan (saved agar taaza ho, warna abhi chalao; ye 'auto' gina jaata hai)."""
    rep = jload("patterns_today.json", None)
    if not rep or rep.get("asof") != rows[-1][0].isoformat() or rep.get("schema") != scanner.SCHEMA:
        rep = scanner.run(rows)
        save_scan(rep, "auto")
    return rep


def active_payload(rep):
    log = jload("active_log.json", None) or active.new_log()
    out = active.view(log, request.args.get("days", 3), report=rep)
    out["patterns"] = [dict({"id": p["id"], "key": p["key"], "naam": p["naam"], "summary": p.get("summary", "")}, **({"errors": [e["error"] for e in rep["errors"] if e["pattern"] == p["naam"]]} if any(e["pattern"] == p["naam"] for e in rep["errors"]) else {}))
                       for p in rep["patterns"]]
    out["errors"] = rep["errors"]
    return out


@app.get("/api/active")
def api_active():
    rows, _ = state()
    rep = scan_today(rows)
    return jsonify(active_payload(rep))


@app.post("/api/active/scan")
def api_active_scan():
    """Manual scan: chalao, active log me milao, GitHub par save, wahi jawab."""
    rows, _ = state()
    try:
        rep = scanner.run(rows)
    except Exception as e:
        app.logger.exception("active scan fail")
        return err(f"Script chali hi nahi: {type(e).__name__}: {str(e)[:200]}", 500)
    save_scan(rep, "manual", push=True)
    return jsonify(active_payload(rep))


@app.get("/api/scanner")
def api_scanner():
    rows, _ = state()
    return jsonify(scan_today(rows))


@app.post("/api/scanner/run")
def api_scanner_run():
    """Manual: script abhi chalao. Galti aaye to 'errors' me dikhegi."""
    rows, _ = state()
    try:
        rep = scanner.run(rows)
    except Exception as e:
        app.logger.exception("scanner run fail")
        return err(f"Script chali hi nahi: {type(e).__name__}: {str(e)[:200]}", 500)
    save_scan(rep, "manual", push=True)
    return jsonify(rep)


PATTERN_DIRS = {"001": "001_copy_pattern", "002": "002_mapping_pattern", "002b": "002_mapping_pattern", "003": "003_family_pattern", "004": "004_baar_tokri"}


def _readme(pid):
    try:
        with open(os.path.join(ROOT, "patterns", PATTERN_DIRS.get(pid, "x"), "README.md"), encoding="utf-8") as f:
            return f.read()
    except OSError:
        return "(README abhi is server par nahi mila)"


@app.get("/api/patterns/index")
def api_patterns_index():
    """Pattern ki index: naam, kya hai, README (kaise bana), kitne abhi chal rahe hain."""
    rows, _ = state()
    rep = scan_today(rows)
    out = []
    for p in rep["patterns"]:
        txt = _readme(p["id"])
        out.append({"id": p["id"], "key": p["key"], "naam": p["naam"], "about": p["about"], "pushti": p.get("pushti", False), "readme": txt,
                    "count": len(p["items"]), "aaj": sum(1 for i in p["items"] if i["status"] == "aaj")})
    out.append({"id": "004", "key": "baar", "naam": "Baar Tokri", "pushti": False, "count": 0, "aaj": 0, "readme": _readme("004"),
                "about": "Har weekday ke sabse zyada aaye 6 number + palat. Aaj ki jodi me jo us baar ki tokri me hon unko highlight (sirf hint)."})
    return jsonify(out)


@app.get("/api/scanner/months")
def api_scanner_months():
    """Ek pattern ke jitne bhi chal rahe hain: har ek ki alag copy (mahine ki sheet), alag rang. scope=recent (abhi chalte) ya month (poore mahine ke)."""
    rows, _ = state()
    key = request.args.get("key", "family")
    scope = request.args.get("scope", "recent")
    rep = scan_today(rows)
    pat = [p for p in rep["patterns"] if p["key"] == key]
    if not pat:
        return err("Pattern nahi mila")
    items = {i["id"]: i for i in pat[0]["items"]}
    total = len(items)
    try:
        if scope == "month":
            ids, total = scanner.ids_for_month(rows, key, rows[-1][0].year, rows[-1][0].month)
        else:
            ids = list(items)[:24]
            total = len(items)
    except ValueError as e:
        return err(str(e))
    by = {d: v for d, v, _ in rows}
    copies, months = [], {}
    for n, pid in enumerate(ids):
        try:
            v = scan_view.view(rows, pid)
        except (ValueError, IndexError):
            continue
        cells = []
        for r in v["blocks"][0]["rows"]:
            for g in range(4):
                if r["kind"][g]:
                    cells.append({"date": r["date"], "g": g, "kind": r["kind"][g], "text": r["txt"][g] or ""})
        yms = sorted({c["date"][:7] for c in cells})
        for ym in yms:
            if ym not in months:
                y, m = int(ym[:4]), int(ym[5:])
                months[ym] = {"label": f"{calendar.month_abbr[m]} {y}", "days": [[(dt.date(y, m, d)).isoformat(), by.get(dt.date(y, m, d))]
                                                                                for d in range(1, calendar.monthrange(y, m)[1] + 1)]}
        it = items.get(pid)
        copies.append({"id": pid, "name": v["title"].split(":")[0], "title": v["title"], "remark": "\n".join(it["lines"]) if it else v["note"],
                       "status": it["status"] if it else "", "color": scanner.COPY_COLORS[n % len(scanner.COPY_COLORS)], "ym": yms, "cells": cells})
    return jsonify({"key": key, "scope": scope, "total": total, "shown": len(copies), "capped": total > len(copies), "months": months, "copies": copies})


@app.get("/api/rank")
def api_rank():
    """Number Rank: aaj ke saare map ke vote, score ke hisab se (HANDOFF item 22)."""
    rows, _ = state()
    return jsonify(rank.build(scan_today(rows), rows))


@app.get("/api/review")
def api_review_get():
    """Aaj ke batch me kaun se pattern 'dekh liye'. Roz naya din = naya batch (kal ke dekhe hue aaj ginti me nahi)."""
    day = active.now_ist().date().isoformat()
    log = jload("review_log.json", {}) or {}
    return jsonify({"date": day, "ids": log.get("days", {}).get(day, [])})


@app.post("/api/review")
def api_review_set():
    b = request.get_json(silent=True) or {}
    ids = [str(i)[:120] for i in (b.get("ids") or [])][:2000]
    day = active.now_ist().date().isoformat()
    log = jload("review_log.json", {}) or {}
    days = log.setdefault("days", {})
    cur = set(days.get(day, []))
    cur = (cur | set(ids)) if b.get("done", True) else (cur - set(ids))
    days[day] = sorted(cur)
    for old in sorted(days)[:-45]:                       # sirf pichle 45 din
        del days[old]
    jsave("review_log.json", log)
    try:
        persist(["review_log.json"], "pattern review")
    except Exception as e:
        app.logger.warning("review persist: %s", e)
    return jsonify({"date": day, "ids": days[day]})


@app.get("/api/scanner/plays")
def api_scanner_plays():
    return jsonify(jload("play_log.json", {}))


@app.post("/api/scanner/play")
@guarded
def api_scanner_play():
    """Aap ne kis pattern par kis game me kaun se number khele (manual note). plays={'FB':{'numbers':[..],'stake':10}}; khaali plays = hata do."""
    b = request.get_json(silent=True) or {}
    pid = str(b.get("id", ""))[:80]
    plays = b.get("plays") or {}
    if not pid or not isinstance(plays, dict):
        return err("Pattern id aur plays chahiye")
    clean = {}
    for g, v in plays.items():
        if g not in ("FB", "GB", "GL", "DS"):
            return err("Game galat: " + str(g)[:10])
        try:
            nums = sorted({int(x) for x in (v.get("numbers") or [])})
            stake = int(v.get("stake", 10))
        except (TypeError, ValueError, AttributeError):
            return err("Number ya stake galat")
        if any(not 0 <= x <= 99 for x in nums) or not 5 <= stake <= 500 or stake % 5:
            return err("Number 0-99 aur stake 5 ke multiple me (5 se 500) chahiye")
        if nums:
            clean[g] = {"numbers": nums, "stake": stake}
    log = jload("play_log.json", {})
    if clean:
        if len(log) >= 400 and pid not in log:
            return err("Bahut zyada purane note hain")
        log[pid] = {"plays": clean, "note": str(b.get("note", ""))[:200], "saved": dt.datetime.now(IST).isoformat(timespec="minutes")}
    else:
        log.pop(pid, None)
    jsave("play_log.json", log)
    try:
        persist(["play_log.json"], "pattern play note")
    except gh.SyncError as e:
        return err(str(e), 502)
    return jsonify({"ok": True, "count": len(log)})


@app.get("/api/scanner/view")
def api_scanner_view():
    rows, _ = state()
    try:
        return jsonify(scan_view.view(rows, request.args.get("id", "")))
    except (ValueError, IndexError) as e:
        return err(str(e) or "Pattern nahi mila")


@app.get("/api/scanner/month_view")
def api_scanner_month_view():
    """Family pattern ka poora mahina, har rashi alag rang."""
    rows, _ = state()
    try:
        return jsonify(scan_view.family_month(rows, request.args.get("id", "")))
    except (ValueError, IndexError) as e:
        return err(str(e) or "Pattern nahi mila")


@app.get("/api/scanner/xlsx")
def api_scanner_xlsx():
    rows, _ = state()
    try:
        pid = request.args.get("id", "")
        blob, title = scan_view.family_month_xlsx(rows, pid) if pid.startswith("family:") else scan_view.xlsx(rows, pid)
    except (ValueError, IndexError) as e:
        return err(str(e) or "Pattern nahi mila")
    name = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in title)[:60] + ".xlsx"
    return Response(blob, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": f'attachment; filename="{name}"'})


@app.get("/api/scanner/bulk")
def api_scanner_bulk():
    """Ek pattern ke aaj ke saare items ek file me: ?key=naksha&fmt=pdf|jpg|xlsx&status=all|aaj&limit=120"""
    rows, _ = state()
    try:
        limit = int(request.args.get("limit", 120))
        blob, mime, name = export_all.build(rows, scan_today(rows), request.args.get("key", ""), request.args.get("fmt", "pdf"),
                                            request.args.get("status", "all"), limit)
    except (ValueError, IndexError) as e:
        return err(str(e) or "Bulk download nahi ban paya")
    return Response(blob, mimetype=mime, headers={"Content-Disposition": f'attachment; filename="{name}"'})


@app.post("/api/scanner/to_board")
def api_scanner_to_board():
    """Pattern ko Pattern paint window ke board me badlo (kuch save nahi hota)."""
    rows, _ = state()
    pid = str((request.get_json(silent=True) or {}).get("id", ""))
    try:
        name = ""
        for p in scan_today(rows)["patterns"]:
            for it in p["items"]:
                if it["id"] == pid:
                    name = it.get("name", "")
        return jsonify({"boards": export_all.to_board(rows, pid, name)})
    except (ValueError, IndexError, KeyError) as e:
        return err(str(e) or "Pattern nahi mila")


@app.get("/api/gaps")
def api_gaps():
    rows, _ = state()
    try:
        res = _gap(rows) or gapchain.find(rows)
    except ValueError as e:
        return err(str(e))
    res["marks"] = gapchain.marks(res)
    return jsonify(res)


@app.get("/api/export/record.xlsx")
def api_export():
    a, b, e = _range()
    if e:
        return err(e)
    rows, _ = state()
    sel = export_xlsx.select(rows, a, b)
    if not sel:
        return err("Is range me koi din nahi")
    try:
        gap = _gap(rows)
    except ValueError as e:
        return err(str(e))
    blob = export_xlsx.build(rows, a, b, gap)
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
    rows, fr = state()
    known = [num(v) for v in request.args.get("known", "").split(",") if v.strip() != ""]
    if None in known or len(known) > 3:
        return err("aaj ke result (FD, GB, GL) 0-99 ke number me")
    plan = picks.daily_plan(rows, known)
    plan["known"] = known
    plan["last_line"] = {"date": rows[-1][0].isoformat(), "results": dict(zip(data.GAMES, rows[-1][1]))}
    # dost jodi: kal ke (aur aaj ke aaye) result ke top-3 dost, teeno samay me
    srcs = [("kal", g, n) for g, n in zip(data.GAMES, rows[-1][1])] + [("aaj", data.GAMES[i], n) for i, n in enumerate(known)]
    plan["dost"] = [{"when": w, "game": g, "number": n,
                     "top": {per: [{"n": f["n"], "together": f["together"]} for f in friends.top_friends(fr.cnt[per], n, 3)] for per in fr.cnt}}
                    for w, g, n in srcs]
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
        if rep["errors"] and not rep["added"] and SYNC and rep["last_date"] < expected_last(dt.datetime.now(IST)).isoformat():
            code, body = SYNC.dispatch()                 # site se seedha nahi aaya: GitHub Action se mangao
            rep["errors"].append("Server se seedha fetch nahi hua, isliye GitHub Action chalane ki koshish: " +
                                 ("chal gaya, 1-2 minute baad dobara dekho" if code == 204 else f"nahi chala (code {code}) {body}"))
    except (ValueError, gh.SyncError) as e:
        return err(str(e), 502)
    except Exception as e:
        app.logger.exception("manual fetch fail")
        return err(f"Fetch me galti: {type(e).__name__}: {str(e)[:200]}", 500)
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
