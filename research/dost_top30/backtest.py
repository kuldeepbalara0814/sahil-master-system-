"""Dost + Baar se Top-30 tokri ka backtest (24 Nov 2026, user ka niyam).
Har din D: sirf D tak ka data. x = pichhli line ke 4 number; har x ke 12 dost (5/4/3) teeno samay (poora, pichle 3 mahine, is mahina), har hazri 1 point;
Baar ki tokri (us weekday ke 6 number + palat) 2 point. Top 30 -> agle din ke FB/GB/GL/DS me kitni baar hit. Random 30 se tulna.
Chalane ka tarika: python research/dost_top30/backtest.py"""
import datetime as dt
import random
import sys
from collections import defaultdict
import numpy as np
sys.path.insert(0, ".")
from lab import baar, data, friends

rows = data.load()
N = len(rows)


def contrib(i):
    C = np.zeros((100, 100), dtype=np.int32); kk = np.zeros(100, dtype=np.int64); seen = np.zeros(100, dtype=np.int64)
    d, R, _ = rows[i]; d2, R2, _ = rows[i + 1]
    if not data.adjacent(d, d2):
        return None
    for g in range(4):
        x = R[g]; w = tuple(R[g + 1:]) + tuple(R2)
        seen[x] += 1; kk[x] += len(w)
        for y in set(w):
            if y != x:
                C[x, y] += 1
    return C, kk, seen


def add(a, b):
    return a[0] + b[0], a[1] + b[1], a[2] + b[2]


def zero():
    return np.zeros((100, 100), dtype=np.int32), np.zeros(100, dtype=np.int64), np.zeros(100, dtype=np.int64)


tot = zero(); months = defaultdict(zero)
WARM = 400
rng = random.Random(7)
res = defaultdict(lambda: defaultdict(lambda: [0, 0]))            # variant -> year -> [hit, trials]
dist_dost = []
for i in range(N - 1):
    if i >= 1:
        c = contrib(i - 1)                                         # transition (i-1 -> i): ab tak ka data
        if c:
            tot = add(tot, c); k = (rows[i - 1][0].year, rows[i - 1][0].month); months[k] = add(months[k], c)
    if i < WARM or not data.adjacent(rows[i][0], rows[i + 1][0]):
        continue
    last = rows[i][0]; ym = (last.year, last.month)
    def mk(back):
        y, m = ym[0], ym[1] - back
        while m <= 0:
            m += 12; y -= 1
        return (y, m)
    m0 = months.get(mk(0), zero())
    m3 = add(add(months.get(mk(0), zero()), months.get(mk(1), zero())), months.get(mk(2), zero()))
    cnts = {"poora": tot, "last3m": m3, "month": m0}
    dost = defaultdict(int)
    for x in rows[i][1]:
        for per, cn in cnts.items():
            for f in friends.top_friends(cn, x, friends.RANK_K, friends.RANK_TIERS):
                dost[f["n"]] += 1
    play = rows[i + 1][0]
    tk = set(baar.tokri(rows[max(0, i - 420):i + 1], play.weekday(), asof=play)["numbers"])
    def top(score):
        return {n for n, _ in sorted(((n, s) for n, s in score.items()), key=lambda t: (-t[1], t[0]))[:30]}
    sc_a = {n: dost.get(n, 0) + (2 if n in tk else 0) for n in set(dost) | tk}
    sc_b = dict(dost)
    sets = {"A dost+baar": top(sc_a), "B sirf dost": top(sc_b), "C baar (12)": tk,
            "R random 30": set(rng.sample(range(100), 30)), "R12 random 12": set(rng.sample(range(100), 12))}
    for name, st in sets.items():
        for g in range(4):
            h = rows[i + 1][1][g] in st
            for key in (play.year, "ALL", "2020+" if play.year >= 2020 else "2014-19"):
                r = res[name][key]; r[0] += h; r[1] += 1
    dist_dost.append(len(dost))

print("din:", res["R random 30"]["ALL"][1] // 4, " | dost wale alag number/din ~", round(sum(dist_dost) / len(dist_dost), 1))
for name in res:
    p = len(sets[name]) if False else None
    row = []
    for key in ("ALL", "2014-19", "2020+"):
        h, t = res[name][key]
        row.append(f"{key}: {100*h/t:.2f}% ({t})")
    print(f"{name:16s}", " | ".join(row))
base = {"A dost+baar": 30, "B sirf dost": 30, "C baar (12)": 12, "R random 30": 30, "R12 random 12": 12}
print("\nROI (Rs1/jodi, 1 game, 95x):")
for name in res:
    h, t = res[name]["ALL"]; k = base[name]
    print(f"{name:16s} hit {100*h/t:.2f}%  ROI {100*(95*h/t - k)/k:+.1f}%  (random {k}% hit -> {100*(95*k/100 - k)/k:+.1f}%)")
print("\nsaal-wise (A dost+baar hit% vs R random 30):")
for y in sorted(k for k in res["A dost+baar"] if isinstance(k, int)):
    a = res["A dost+baar"][y]; r = res["R random 30"][y]
    print(y, f"{100*a[0]/a[1]:.1f}% vs {100*r[0]/r[1]:.1f}%  ({a[1]})")
