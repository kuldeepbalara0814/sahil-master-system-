"""Baar (weekday) ki tokri: us weekday par jo 6 number sabse zyada aaye + unke palat. Aaj ki jodi par highlight (hint) ke liye.

Sirf hint hai: jaanch me ye chance badhata nahi dikha (random jaisa). Faisla insaan ka.
"""
import datetime as dt
from collections import Counter

from . import data

NAMES = ["Somvar", "Mangalvar", "Budhvar", "Guruvar", "Shukravar", "Shanivar", "Ravivar"]


def pal(n):
    return (n % 10) * 10 + n // 10


def tokri(rows, weekday, days=365, asof=None, k=6):
    """asof se pehle ke `days` din (0 = poora record) me us weekday ke 6 sabse zyada aaye number (line ki tarikh ka weekday)."""
    asof = asof or data.play_date(rows)
    a = asof - dt.timedelta(days=days) if days else rows[0][0]
    cnt = Counter()
    n_days = 0
    for d, v, _ in rows:
        if a <= d < asof and d.weekday() == weekday:
            n_days += 1
            cnt.update(v)
    ranked = sorted(cnt.items(), key=lambda x: (-x[1], x[0]))
    top = ranked[:k]
    cut = top[-1][1] if len(top) == k else None
    ties = [n for n, c in ranked[k:] if cut is not None and c == cut]
    nums = sorted({n for n, _ in top} | {pal(n) for n, _ in top})
    return {"weekday": weekday, "weekday_name": NAMES[weekday], "days": days, "from": a.isoformat(), "to": (asof - dt.timedelta(days=1)).isoformat(),
            "cases": n_days, "top": [{"n": n, "count": c, "palat": pal(n)} for n, c in top], "ties": ties, "numbers": nums, "asof": asof.isoformat()}
