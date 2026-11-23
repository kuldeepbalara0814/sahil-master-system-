"""Number Rank: aaj ke saare pattern (map) number ke liye vote dete hain. Ek map = ek vote (ek number par).
Score = kitne alag map ne wo number diya (+1 agar aaj ke din (baar) ki tokri me hai).
Har pattern type ki list: FB, GB, GL, DS (jis game ka location map ne bataya) aur ALL (sab mila ke). 'ALL IN ONE' me sab type.
Location-tay-nahi wale map (copy, dana, family jab ek se zyada jagah) sirf ALL list me vote dete hain.
"""
from collections import defaultdict

from . import baar, data

GROUPS = [("all", "ALL IN ONE"), ("naksha", "Naksha 1"), ("naksha2", "Naksha 2 (Rashi)"), ("family", "Family"), ("copy", "Copy"), ("dana", "Dana-Farak")]
LOCS = ("FB", "GB", "GL", "DS")


def _rows(votes, tokri):
    """votes: {number: set(map label)} -> sorted rows."""
    out = []
    for n, maps in votes.items():
        b = 1 if n in tokri else 0
        out.append({"n": n, "score": len(maps) + b, "votes": len(maps), "baar": b, "maps": sorted(maps)})
    out.sort(key=lambda r: (-r["score"], -r["votes"], r["n"]))
    return out


def build(report, rows):
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
    groups = [{"key": k, "naam": nm, "maps": maps[k], "lists": {loc: _rows(votes[k][loc], tokri) for loc in LOCS + ("ALL",)}} for k, nm in GROUPS]
    return {"date": play.isoformat(), "weekday": baar.NAMES[play.weekday()], "scan_time": report.get("time"), "asof": report.get("asof"), "groups": groups}
