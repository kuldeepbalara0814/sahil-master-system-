"""Baar (weekday) ki tokri: us weekday par jo 6 number sabse zyada aaye + unke palat. Aaj ki jodi par highlight (hint) ke liye.

Sirf hint hai: jaanch me ye chance badhata nahi dikha (random jaisa). Faisla insaan ka.
"""
import datetime as dt
from collections import Counter

from . import data

NAMES = ["Somvar", "Mangalvar", "Budhvar", "Guruvar", "Shukravar", "Shanivar", "Ravivar"]


def pal(n):
    return (n % 10) * 10 + n // 10


GAMES = ("FB", "GB", "GL", "DS")
ORDER = [6, 0, 1, 2, 3, 4, 5]                      # Ravi se Shani (aap ne Sunday se Monday kaha)


def tokri(rows, weekday, days=365, asof=None, k=6, where=False):
    """asof se pehle ke `days` din (0 = poora record) me us weekday ke 6 sabse zyada aaye number (line ki tarikh ka weekday)."""
    asof = asof or data.play_date(rows)
    a = asof - dt.timedelta(days=days) if days else rows[0][0]
    cnt = Counter()
    n_days = 0
    seen = {}
    for d, v, _ in rows:
        if a <= d < asof and d.weekday() == weekday:
            n_days += 1
            cnt.update(v)
            if where:
                for g, x in enumerate(v):
                    seen.setdefault(x, []).append(f"{d:%d %b %y} {GAMES[g]}")
    ranked = sorted(cnt.items(), key=lambda x: (-x[1], x[0]))
    top = ranked[:k]
    cut = top[-1][1] if len(top) == k else None
    ties = [n for n, c in ranked[k:] if cut is not None and c == cut]
    nums = sorted({n for n, _ in top} | {pal(n) for n, _ in top})
    return {"weekday": weekday, "weekday_name": NAMES[weekday], "days": days, "from": a.isoformat(), "to": (asof - dt.timedelta(days=1)).isoformat(),
            "cases": n_days, "top": [{"n": n, "count": c, "palat": pal(n), **({"when": seen.get(n, [])} if where else {})} for n, c in top],
            "ties": ties, "numbers": nums, "asof": asof.isoformat(), "strength": sum(c for _, c in top)}


def all_days(rows, days=365, asof=None):
    """Saatho baar (Ravi se Shani) ki tokri, kab-kab aaya samet, aur kaun sa baar sabse mazboot (6 number ke baar ka jod)."""
    items = [tokri(rows, wd, days, asof, where=True) for wd in ORDER]
    rank = sorted(range(len(items)), key=lambda i: (-items[i]["strength"], i))
    for r, i in enumerate(rank, 1):
        items[i]["rank"] = r
    return {"days": days, "items": items, "order": [items[i]["weekday"] for i in rank]}
