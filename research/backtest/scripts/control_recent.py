"""Dana-farak control: farak core = pair ke number + palat (haal me aaye number). Kya koi bhi 'haal ke 2 number + palat' utna hi hit karta hai?
Har farak record ke liye wahi window, par set = box ke 16 cell me se 2 random number (farak ka rishta nahi) + unke palat. Usage: python control_recent.py"""
import os, sys, datetime as dt, numpy as np, pandas as pd
import harness as h
from analysis import load, OUT
rows = h.data.load(); V = np.array([r[1] for r in rows]); flat = V.ravel()
idx = {r[0].isoformat(): i for i, r in enumerate(rows)}
d = load("real", "light"); d = d[(d.pat == "dana") & (d.kind == "farak") & (d["sub"] == "core")]
rng = np.random.default_rng(5)
pal = lambda n: (n % 10) * 10 + n // 10
def isfar(a, b):
    for u in (a, pal(a)):
        for v in (b, pal(b)):
            if abs(u - v) in (1, 10) or u == v: return True
    return False
rec = []
for r in d.itertuples():
    p = r.id.split(":"); c1, c2 = p[2].rsplit("-", 1), p[3].rsplit("-", 1)
    i1, g1 = idx.get(c1[0]), int(c1[1]); i2, g2 = idx.get(c2[0]), int(c2[1])
    if i1 is None or i2 is None: continue
    a, b = i1 * 4 + g1, i2 * 4 + g2
    win = flat[b + 1: b + 1 + int(r.cells)]
    if len(win) < r.cells: continue
    box = flat[a: b + 1 + 8]  # c1 se thoda aage tak ke cell (pair + paas)
    box = flat[max(0, a - 4): b + 1]
    hs = []
    for _ in range(30):
        x, y = rng.choice(box, 2)
        if isfar(x, y): continue
        S = {x, pal(x), y, pal(y)}
        hs.append(int(np.isin(win, list(S)).any()))
    if hs:
        rec.append((r.hit, np.mean(hs), r.p, r.date[:4]))
x = pd.DataFrame(rec, columns=["hit", "ctrl", "p", "year"])
print("n", len(x), "farak hit %.4f" % x.hit.mean(), "recent-pair control %.4f" % x.ctrl.mean(), "uniform p %.4f" % x.p.mean())
print(x.groupby("year")[["hit", "ctrl", "p"]].mean().round(3).T.to_string())
x.to_csv(os.path.join(OUT, "control_recent.csv"), index=False)
