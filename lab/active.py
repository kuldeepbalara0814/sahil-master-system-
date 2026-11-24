"""Active registry: jo pattern ek baar bana wo kabhi gayab nahi hota.

data/active_log.json = {"items": {id: {...}}, "scans": [...]}.
Sirf event wale pattern (copy, family, dana, ...) rakhe jaate hain. Naksha jaise (bina nateeje wale) nahi.
Koi naya pattern jiske items ka status aaj/pass/fail ho, apne aap shamil ho jaata hai.
"""
import datetime as dt

NOT_STORED = ("naksha", "naksha2", "ank")        # inka koi pass/fail nahi
STATUSES = ("aaj", "pass", "fail")
MAX_ITEMS = 4000
KEEP_SCANS = 60
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
FIELDS = ("name", "title", "lines", "strength", "ambiguous", "target")


def now_ist():
    return dt.datetime.now(IST)


def new_log():
    return {"items": {}, "scans": []}


def _pat(p, it):
    x = it.get("pattern") or {}
    return {"id": x.get("id", p.get("id")), "key": x.get("key", p.get("key")), "naam": x.get("naam", p.get("naam"))}


def merge(log, report, now=None, source="auto"):
    """Report ke items log me daalo (purane kabhi na hatao). log wapas karta hai."""
    now = now or now_ist()
    day = now.date().isoformat()
    log.setdefault("items", {})
    log.setdefault("scans", [])
    items = log["items"]
    seen = log.setdefault("seen", {})                          # har item (naksha samet) pehli baar kab dikha -> "NAYA" nishan
    first_run = not seen
    for p in report.get("patterns", []):
        for it in p.get("items", []):
            if it.get("id"):
                if it["id"] not in seen:
                    seen[it["id"]] = "0000-00-00" if first_run else day   # pehle scan me sab purana maano
                it["new"] = seen[it["id"]] == day
    if len(seen) > 30000:
        for k in sorted(seen, key=seen.get)[:len(seen) - 30000]:
            del seen[k]
    for p in report.get("patterns", []):
        for it in p.get("items", []):
            kind = it.get("kind", p.get("key"))
            if kind in NOT_STORED or p.get("key") in NOT_STORED or it.get("status") not in STATUSES or not it.get("id"):
                continue
            old = items.get(it["id"])
            if old is None:
                old = items[it["id"]] = {"id": it["id"], "first_seen": day, "resolved_on": None, "status": "aaj"}
            old["pattern"] = _pat(p, it)
            old["last_seen"] = day
            if old["resolved_on"] is None:                     # nateeja aa gaya to wahi rahega
                for k in FIELDS:
                    if k in it:
                        old[k] = it[k]
                old["status"] = it["status"]
                if it["status"] in ("pass", "fail"):
                    old["resolved_on"] = it.get("end") or day
            else:
                for k in ("name", "title", "strength", "ambiguous"):
                    if k not in old and k in it:
                        old[k] = it[k]
    if len(items) > MAX_ITEMS:                                 # sabse purane resolved pehle hatao
        done = sorted((v for v in items.values() if v.get("resolved_on")), key=lambda v: (v["resolved_on"], v["first_seen"]))
        for v in done[:len(items) - MAX_ITEMS]:
            del items[v["id"]]
    log["scans"].append({"time": now.strftime("%Y-%m-%dT%H:%M:%S"), "source": "manual" if source == "manual" else "auto", "asof": report.get("asof")})
    log["scans"] = log["scans"][-KEEP_SCANS:]
    return log


def _out(v):
    o = {k: v.get(k) for k in ("id", "pattern", "name", "title", "lines", "status", "strength", "ambiguous", "target", "first_seen", "last_seen", "resolved_on")}
    o["lines"] = o["lines"] or []
    return o


def view(log, days=3, today=None, report=None):
    """Active window ke liye data."""
    try:
        days = int(days)
    except (TypeError, ValueError):
        days = 3
    days = max(1, min(3, days))
    today = today or now_ist().date()
    iso = today.isoformat()
    items = list((log.get("items") or {}).values())
    scans = log.get("scans") or []
    td = [s for s in scans if str(s.get("time", "")).startswith(iso)]
    cut = (today - dt.timedelta(days=days)).isoformat()
    cut30 = (today - dt.timedelta(days=30)).isoformat()
    now = sorted((v for v in items if v.get("status") == "aaj"), key=lambda v: (v.get("first_seen") or "", v["id"]), reverse=True)
    rpass = sorted((v for v in items if v.get("status") == "pass" and (v.get("resolved_on") or "") >= cut),
                   key=lambda v: v.get("resolved_on") or "", reverse=True)
    rfail = sum(1 for v in items if v.get("status") == "fail" and (v.get("resolved_on") or "") >= cut)
    summ = {p["id"]: p.get("summary", "") for p in (report or {}).get("patterns", [])}
    names = {}
    for p in (report or {}).get("patterns", []):
        names[p["id"]] = p
    agg = {}
    for v in items:
        if v.get("status") in ("pass", "fail") and (v.get("resolved_on") or "") >= cut30:
            pp = v.get("pattern") or {}
            a = agg.setdefault(pp.get("id"), {"id": pp.get("id"), "key": pp.get("key"), "naam": pp.get("naam"), "pass": 0, "fail": 0})
            a[v["status"]] += 1
    for pid, p in names.items():                                # jis pattern ka kuch resolve nahi hua wo bhi dikhe
        if pid not in agg and p.get("key") not in NOT_STORED:
            agg[pid] = {"id": pid, "key": p.get("key"), "naam": p.get("naam"), "pass": 0, "fail": 0}
    board = []
    for pid in sorted(agg, key=str):
        a = agg[pid]
        n = a["pass"] + a["fail"]
        a["rate"] = round(a["pass"] / n, 3) if n else None
        a["window"] = "pichle 30 din"
        a["summary"] = summ.get(pid, "")
        board.append(a)
    return {"asof": (report or {}).get("asof") or (scans[-1].get("asof") if scans else None), "days": days,
            "scans": {"last": scans[-1] if scans else None, "today": td,
                      "auto_today": sum(1 for s in td if s.get("source") == "auto"), "manual_today": sum(1 for s in td if s.get("source") == "manual")},
            "now": [_out(v) for v in now],
            "recent_pass": [dict(_out(v), passed_on=v.get("resolved_on")) for v in rpass],
            "recent_fail": rfail, "board": board}
