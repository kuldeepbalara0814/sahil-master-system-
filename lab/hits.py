"""Hit hue map (short list): jis map (pattern ke andaze) ka number aaya wo 3 din Active window me alag se.

- Har scan ke andaze (kal ke liye) 'pred_archive.json' me play_date ke hisaab se rakhte hain (aakhri 6 din).
- Result aaya (site se ya hath se 'manual_results.json') to us din ke andaze se milate hain: number kisi bhi map ke targets me hai to us map ka HIT likhte hain
  (location ka koi chakkar nahi: kisi bhi game me aaya to hit).
- hit_log.json: har map ka hit (map ka snapshot, tarikh, game, number). Active window iske 'pichle 1-3 din' dikhati hai.
Sirf wahi pattern jinke items me 'targets' [{game, numbers}] ho (naksha, naksha2, family, copy, dana, steps) apne aap aate hain.
"""
import datetime as dt

IST = dt.timezone(dt.timedelta(hours=5, minutes=30))


def _today():
    """Aaj ki tarikh IST me (server/Action UTC me chalte hain, 00:00-05:30 IST ke beech ek din ka farak aa jata tha)."""
    return dt.datetime.now(IST).date()


GAMES = ("FB", "GB", "GL", "DS")
KEEP_DAYS = 6
KEEP_HITS_DAYS = 45


def new_state():
    return {"archive": {}, "hits": {}, "done": {}}


def archive(state, rep):
    """Is scan ke andaze (play_date ke liye) rakho. Slim: id, name, title, lines, targets, pattern."""
    pd = rep.get("play_date")
    if not pd:
        return
    slim = []
    for p in rep.get("patterns", []):
        for it in p.get("items", []):
            tg = it.get("targets") or []
            if not tg:
                continue
            slim.append({"id": it["id"], "name": it.get("name"), "title": it.get("title"), "lines": it.get("lines", [])[:6], "targets": tg,
                         "pattern": it.get("pattern") or {"id": p.get("id"), "key": p.get("key"), "naam": p.get("naam")}})
    state.setdefault("archive", {})[pd] = {"asof": rep.get("asof"), "items": slim}
    for d in sorted(state["archive"])[:-KEEP_DAYS]:
        del state["archive"][d]


def _numbers(it):
    s = set()
    for t in it["targets"]:
        s |= set(int(x) for x in t["numbers"])
    return s


KEEP_DONE_DAYS = 60


def _trim_done(state, today=None):
    """'done' (kaun si tarikh:game ka hisaab ho chuka) bina hadd badhta tha: 60 din se purane hatao."""
    cut = ((today or _today()) - dt.timedelta(days=KEEP_DONE_DAYS)).isoformat()
    done = state.get("done", {})
    for k in [k for k in done if k.split(":")[0] < cut]:
        del done[k]


def evaluate(state, date, game, number, source="auto", today=None):
    """Ek result (date, game, number) ko us din ke andaze se milao. -> hit hue map ki list (naye)."""
    key = f"{date}:{game}"
    done = state.setdefault("done", {})
    if key in done:
        return []
    done[key] = {"n": int(number), "src": source}
    arc = state.get("archive", {}).get(date)
    if not arc:
        return []
    out = []
    hits = state.setdefault("hits", {})
    for it in arc["items"]:
        if int(number) in _numbers(it):
            h = hits.setdefault(it["id"], {"id": it["id"], "name": it["name"], "title": it["title"], "lines": it["lines"], "pattern": it["pattern"], "hits": []})
            h["hits"].append({"date": date, "game": game, "n": int(number), "src": source})
            h["last_hit"] = date
            out.append(it)
    cut = ((today or _today()) - dt.timedelta(days=KEEP_HITS_DAYS)).isoformat()
    for k in [k for k, v in hits.items() if v.get("last_hit", "") < cut]:
        del hits[k]
    return out


def unset(state, date, game):
    """Hath se dala result hatao: ginti (done) aur us se bane hit (sirf manual wale) saaf. Site wale (auto) result nahi hatta. -> True agar kuch hata."""
    key = f"{date}:{game}"
    d = state.get("done", {}).get(key)
    if not d or d.get("src") != "manual":
        return False
    del state["done"][key]
    hits = state.get("hits", {})
    for k in list(hits):
        h = hits[k]
        h["hits"] = [x for x in h["hits"] if not (x["date"] == date and x["game"] == game and x.get("src") == "manual")]
        if not h["hits"]:
            del hits[k]
        else:
            h["last_hit"] = max(x["date"] for x in h["hits"])
    return True


def settle(state, rows, manual=None, today=None):
    """Archive ke har din ke har game ka result (site ya hath se) mil gaya ho to evaluate karo. -> kul naye hit."""
    by = {d.isoformat(): v for d, v, _ in rows}
    n = 0
    _trim_done(state, today)
    for date in sorted(state.get("archive", {})):
        for gi, g in enumerate(GAMES):
            dn = state.get("done", {}).get(f"{date}:{g}")
            if dn and dn.get("src") == "manual" and date in by and dn["n"] != by[date][gi]:      # site ka asli result alag nikla: hath wala hata ke site wala ginte
                state.setdefault("mismatch", []).append({"date": date, "game": g, "manual": dn["n"], "site": by[date][gi]})
                unset(state, date, g)
                dn = None
            if dn:
                continue
            if date in by:
                n += len(evaluate(state, date, g, by[date][gi], "auto", today))
            elif manual and date in manual and g in manual[date]:
                n += len(evaluate(state, date, g, manual[date][g], "manual", today))
    return n


def view(state, days=3, today=None):
    days = max(1, min(int(days or 3), 3))
    cut = ((today or _today()) - dt.timedelta(days=days - 1)).isoformat()
    groups = {}
    for h in state.get("hits", {}).values():
        recent = [x for x in h["hits"] if x["date"] >= cut]
        if not recent:
            continue
        g = groups.setdefault(h["pattern"]["key"], {"key": h["pattern"]["key"], "naam": h["pattern"]["naam"], "items": []})
        g["items"].append({**h, "recent": recent})
    for g in groups.values():
        g["items"].sort(key=lambda x: (x["last_hit"], len(x["recent"])), reverse=True)
        g["count"] = len(g["items"])
    order = ["naksha", "steps", "family", "copy", "dana", "naksha2"]
    gl = sorted(groups.values(), key=lambda g: order.index(g["key"]) if g["key"] in order else 99)
    return {"days": days, "total": sum(g["count"] for g in gl), "groups": gl}
