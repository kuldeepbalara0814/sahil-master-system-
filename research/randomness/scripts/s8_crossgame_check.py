"""8) Cross-game same-day equal-number excess: pooled z over 6 pairs, by year, by data source, permutation of days (circular shift keeps serial structure), 3-way equal."""
import csv, numpy as np, common as c, os
rows = list(csv.DictReader(open(os.path.join(c.ROOT, "data", "results.csv"))))
g = {k: [] for k in ("fd", "gb", "gl", "ds")}; D = []; src = []
for r in rows:
    try: v = [int(r[k]) for k in g]
    except: continue
    for k, x in zip(g, v): g[k].append(x)
    D.append(r["date"]); src.append(r["source"])
A = {k: np.array(v) for k, v in g.items()}; yr = np.array([int(d[:4]) for d in D]); n = len(D); src = np.array(src)
print("n rows with all 4", n)
keys = list(A); out = []; rg = c.rng(88)
pairs = [(a, b) for i, a in enumerate(keys) for b in keys[i + 1:]]
tot = 0; totE = 0
for a, b in pairs:
    eq = A[a] == A[b]; o = int(eq.sum()); e = n * float((np.bincount(A[a], minlength=100) / n * np.bincount(A[b], minlength=100) / n).sum())
    # circular-shift null (keeps each game's own serial structure), shifts >= 30
    sims = np.array([int((A[a] == np.roll(A[b], s)).sum()) for s in rg.integers(30, n - 30, 400)])
    out.append([a, b, "same-day equal number", o, e, float(sims.mean()), float(sims.std()), (o - sims.mean()) / sims.std(), c.mc_p(o, sims, "upper")]); tot += o; totE += sims.mean()
    byyr = [int(eq[yr == y].sum()) for y in np.unique(yr)]
    out.append([a, b, "per-year equal counts (2013..2026)", " ".join(map(str, byyr)), "", "", "", "", ""])
    bysrc = {s: (int(eq[src == s].sum()), int((src == s).sum())) for s in np.unique(src)}
    out.append([a, b, "by source (equal,rows)", str(bysrc), "", "", "", "", ""])
out.append(["ALL", "6 pairs", "pooled same-day equal number", tot, "", totE, np.sqrt(totE), (tot - totE) / np.sqrt(totE), ""])
# 3-way and 4-way equal
for t in (("fd", "gb", "gl"), ("fd", "gb", "ds"), ("fd", "gl", "ds"), ("gb", "gl", "ds")):
    o = int(((A[t[0]] == A[t[1]]) & (A[t[1]] == A[t[2]])).sum()); out.append(["+".join(t), "", "3-way equal same day (iid expect ~%.2f)" % (n / 1e4), o, "", "", "", "", ""])
# same-day class/rashi/tens/unit equality
MAPS = {"class": c.CLS, "rashi": c.RASHI_IDX, "tens": np.arange(100) // 10, "unit": np.arange(100) % 10}
for a, b in pairs:
    for nm, mp in MAPS.items():
        xa, xb = mp[A[a]], mp[A[b]]; o = int((xa == xb).sum())
        sims = np.array([int((xa == np.roll(xb, s)).sum()) for s in rg.integers(30, n - 30, 200)])
        out.append([a, b, "same-day " + nm + " equal", o, "", float(sims.mean()), float(sims.std()), (o - sims.mean()) / sims.std(), c.mc_p(o, sims, "upper")])
c.save_csv("s8_crossgame_check.csv", ["a", "b", "test", "obs", "iid_expect", "shift_null_mean", "shift_null_sd", "z", "p"], out)
for r in out: print([str(x)[:70] for x in r])
