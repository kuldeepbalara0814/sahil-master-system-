"""Banner khabar: result aane ke baad kaun se current pattern NAYE active hue (patterns/013_auto_fetch_alerts/README.md).
Pichle scan me jo 'aaj' (active) nahi the aur ab hain wo naye. Naksha-Rashi (44 items) ginti me aata hai, naam se nahi (shor)."""
import datetime as dt

KEEP = 40
QUIET = ("naksha2",)          # sirf ginti, naam nahi
MAX_NAMES = 6


def active_items(rep):
    """{id: (pattern key, naam, item)} - status 'aaj' wale."""
    out = {}
    for p in (rep or {}).get("patterns", []):
        for it in p.get("items", []):
            if it.get("status") == "aaj" and it.get("id"):
                out[it["id"]] = (p.get("key"), p.get("naam"), it)
    return out


def _nums_games(it):
    tg = it.get("targets") or []
    return sorted({int(n) for t in tg for n in t["numbers"]}), sorted({t["game"] for t in tg})


def make(prev, new, label, now=None):
    """-> alert dict ya None (kuch naya active nahi hua)."""
    if not prev or not new:
        return None
    old = active_items(prev)
    cur = active_items(new)
    fresh = [(i, v) for i, v in cur.items() if i not in old]
    if not fresh:
        return None
    groups = {}
    for i, (key, naam, it) in fresh:
        g = groups.setdefault(key, {"key": key, "naam": naam, "count": 0, "items": []})
        g["count"] += 1
        if key not in QUIET and len(g["items"]) < MAX_NAMES:
            nums, games = _nums_games(it)
            g["items"].append({"id": i, "name": it.get("name"), "numbers": nums, "games": games})
    now = now or dt.datetime.now(dt.timezone(dt.timedelta(hours=5, minutes=30)))
    return {"id": now.isoformat(timespec="seconds"), "time": now.isoformat(timespec="seconds"), "label": label,
            "total": len(fresh), "groups": sorted(groups.values(), key=lambda g: (g["key"] in QUIET, g["key"]))}


def make_hits(hit_state, date, games, label, now=None):
    """Din ka result aaya: us tarikh/game par kis-kis map me laga. (Maps nahi badalte.) Kisi me na laga ho tab bhi khabar banti hai."""
    groups = {}
    for h in (hit_state or {}).get("hits", {}).values():
        for q in h.get("hits", []):
            if q.get("date") == date and q.get("game") in games:
                pat = h.get("pattern") or {}
                key = pat.get("key", "")
                g = groups.setdefault(key, {"key": key, "naam": (pat.get("naam") or key) + " me laga", "count": 0, "items": []})
                g["count"] += 1
                if key not in QUIET and len(g["items"]) < MAX_NAMES:
                    g["items"].append({"id": h["id"], "name": h.get("name"), "numbers": [q["n"]], "games": [q["game"]]})
    now = now or dt.datetime.now(dt.timezone(dt.timedelta(hours=5, minutes=30)))
    total = sum(g["count"] for g in groups.values())
    return {"id": now.isoformat(timespec="seconds"), "time": now.isoformat(timespec="seconds"),
            "label": label + ("" if total else " - kisi map me nahi laga"), "total": total,
            "groups": sorted(groups.values(), key=lambda g: (g["key"] in QUIET, g["key"]))}


def add(log, alert):
    """log = {"items": [...]} (naya pehle). Wahi label ke saath wahi ids dobara na jude."""
    items = log.setdefault("items", [])
    if alert:
        items.insert(0, alert)
        del items[KEEP:]
    return log
