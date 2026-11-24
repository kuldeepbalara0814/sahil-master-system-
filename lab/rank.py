"""Number Rank: aaj ke saare pattern (map) number ke liye vote dete hain. Ek map = ek vote (ek number par).
Score = kitne alag map ne wo number diya + dost ke point (+2 agar aaj ke din (baar) ki tokri me hai).
Dost (24 Nov 2026): pichhli line ke har number ke 12 dost (5 hara, 4 peela, 3 narangi) teeno samay (poora, pichle 3 mahine, is mahina) me;
dost list me jitni baar wo number aaye utne point (har baar 1). Baar ki tokri ke number ko 2 point (pehle 1 the).
Har pattern type ki list: FB, GB, GL, DS (jis game ka location map ne bataya) aur ALL (sab mila ke). 'ALL IN ONE' me sab type.
Location-tay-nahi wale map (copy, dana, family jab ek se zyada jagah) sirf ALL list me vote dete hain.
"""
from collections import defaultdict

from . import baar, data, friends

GROUPS = [("all", "ALL IN ONE"), ("naksha", "Naksha 1"), ("naksha2", "Naksha 2 (Rashi)"), ("family", "Family"), ("copy", "Copy"), ("dana", "Dana-Farak"), ("steps", "Puzzle-Steps"), ("dost", "Dost")]
LOCS = ("FB", "GB", "GL", "DS")
BAAR_POINT = 2


def _rows(votes, tokri):
    """votes: {number: set(map label)} -> sorted rows."""
    out = []
    for n, maps in votes.items():
        b = 1 if n in tokri else 0
        out.append({"n": n, "score": len(maps) + BAAR_POINT * b, "votes": len(maps), "baar": b, "maps": sorted(maps)})
    out.sort(key=lambda r: (-r["score"], -r["votes"], r["n"]))
    return out


def dost_labels(rows, fr=None):
    """{number: [label,...]} - pichhli line ke har number ke 12 dost, teeno samay; har (number, samay) ki list se ek point."""
    fr = fr or friends.Friends(rows)
    out = defaultdict(list)
    for x in rows[-1][1]:
        for per in ("poora", "last3m", "month"):
            for f in friends.top_friends(fr.cnt[per], x, friends.RANK_K, friends.RANK_TIERS):
                out[f["n"]].append(f"Dost {x:02d} ({per})")
    return out


def build(report, rows, fr=None):
    play = data.play_date(rows)
    tk = baar.tokri(rows, play.weekday(), asof=play)
    tokri = set(tk["numbers"])
    keys = [k for k, _ in GROUPS]
    votes = {k: {loc: defaultdict(set) for loc in LOCS + ("ALL",)} for k in keys}
    maps = {k: 0 for k in keys}
    for p in report.get("patterns", []):
        key = p.get("key")
        if key not in votes:
            continue
        for idx, it in enumerate(p.get("items", []), 1):
            tg = it.get("targets") or []
            if not tg:
                continue
            label = f"Pattern {idx:02d}" + ("" if key == "naksha" else f" ({p.get('naam')})")
            for k in (key, "all"):
                maps[k] += 1
                for t in tg:
                    for n in t["numbers"]:
                        votes[k]["ALL"][n].add(label)
                        if t["game"] in LOCS:
                            votes[k][t["game"]][n].add(label)
    dl = dost_labels(rows, fr)                                   # dost: har number ke har list-hazri ka alag point; sirf ALL list (location tay nahi)
    for n, labs in dl.items():
        for lab in labs:
            for k in ("dost", "all"):
                votes[k]["ALL"][n].add(lab)
    maps["dost"] = len({lb for v in dl.values() for lb in v})      # kitni dost-list bani (pichhli line ke number x 3 samay); 'all' ki map-ginti pattern ki hi rehti hai
    groups = [{"key": k, "naam": nm, "maps": maps[k], "lists": {loc: _rows(votes[k][loc], tokri) for loc in LOCS + ("ALL",)}} for k, nm in GROUPS]
    return {"date": play.isoformat(), "weekday": baar.NAMES[play.weekday()], "scan_time": report.get("time"), "asof": report.get("asof"), "groups": groups}
