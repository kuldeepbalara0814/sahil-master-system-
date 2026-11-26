"""Naksha ki yaad (patterns/010_meri_window/README.md): naksha ka chart aage ke 8 din tak '?' box dikhata hai, par card sirf agle din ka
andaza leta tha aur agle scan me purana naksha hat jata tha. Yahan har tarikh ke liye pichle 8 din ke scan ke '?' box jama karte hain.

Koi file nahi: har din ka scan us din tak ke data se dobara ginte hain (aage ka data nahi dekhte). Sirf Naksha 1 (2b Rashi nahi).
Imandari: 900 din ki jaanch me in andazon ka hit random jitna hi nikla (2.0% vs 1.95%). Software dikhata hai, faisla insaan ka."""
import datetime as dt

from . import data, scanner

DAYS = 8
GAMES = ("FB", "GB", "GL", "DS")
_cache = {}


def _future(last, n=DAYS):
    out, d = [], last
    while len(out) < n:
        d += dt.timedelta(days=1)
        if not data.is_last_day(d):
            out.append(d)
    return out


def _boxes(rows):
    """Is data tak ke naksha scan ke saare aage wale box: [(k, game, numbers, purani_line_ki_tarikh, naam, title, id)]."""
    key = (len(rows), rows[-1][0], tuple(rows[-1][1]))
    if key in _cache:
        return _cache[key]
    D, _, C = scanner._arrays(rows, "n")
    N, out = len(rows), []
    for it in scanner.scan_naksha(rows, rows[-1][0].isoformat())["items"]:
        _, L, so = it["id"].split(":")
        L, so = int(L), D.index(dt.date.fromisoformat(so))
        sc = N - L
        comp, _ = scanner._comps(scanner._links(C[sc:sc + L]), scanner._links(C[so:so + L]), 4 * L)
        fc, fo = C[sc:sc + L].reshape(-1), C[so:so + L].reshape(-1)
        cl = [(int(fo[g[0]]), int(fc[g[0]])) for g in comp]
        for k in range(DAYS):
            po = so + L + k
            if po >= N:
                break
            for g in range(4):
                for old, new in cl:
                    if C[po, g] == old:
                        out.append((k, GAMES[g], tuple(sorted({new, scanner.pal(new)})), D[po], it["name"], it["title"], it["id"]))
    if len(_cache) > 40:
        _cache.clear()
    _cache[key] = out
    return out


def for_date(rows, target, result=None):
    """target tarikh ke liye pichle DAYS scan ke box. rows me target ya uske baad ki line ho to wo scan me nahi li jati.
    result = {game: number} (aa chuke) -> hit nishan."""
    before = [r for r in rows if r[0] < target]
    seen = {}
    for back in range(DAYS):
        rs = before[:len(before) - back]
        if len(rs) < 400:
            break
        fut = _future(rs[-1][0])
        if target not in fut:
            continue
        k = fut.index(target)
        for kk, g, nums, src, name, title, pid in _boxes(rs):
            if kk != k:
                continue
            key = (g, nums, src)                                   # wahi purani line, wahi game, wahi jodi = wahi andaza (naam roz badalta hai)
            e = seen.get(key)
            if not e:
                seen[key] = {"game": g, "numbers": list(nums), "name": name, "title": title, "purana": src.isoformat(),
                             "pehle": k + 1, "scans": 1, "id": pid, "asof": rs[-1][0].isoformat()}
            else:
                e["pehle"] = max(e["pehle"], k + 1)
                e["scans"] += 1
    items = sorted(seen.values(), key=lambda e: (GAMES.index(e["game"]), -e["scans"], e["numbers"]))
    result = result or {}
    for e in items:
        e["hit"] = result.get(e["game"]) in e["numbers"]
    games = {g: sorted({n for e in items if e["game"] == g for n in e["numbers"]}) for g in GAMES}
    return {"date": target.isoformat(), "items": items, "games": games, "all": sorted({n for v in games.values() for n in v}),
            "result": {g: result[g] for g in GAMES if g in result}}


def view(rows, known=None):
    """-> {"aaj": agle khel din ke box, "kal": aakhri poori line ke din ke box + natija}. known = aadhi line/hath ke {date: {game: n}}."""
    play = data.play_date(rows)
    last_d, last_v = rows[-1][0], rows[-1][1]
    return {"aaj": for_date(rows, play, (known or {}).get(play.isoformat())),
            "kal": for_date(rows, last_d, dict(zip(GAMES, last_v)))}
