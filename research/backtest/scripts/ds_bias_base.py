"""Dana-farak farak-core: DS ke sthayi bias (1966-2013 ki frequency) se ummeed vs uniform ummeed vs asli hit. Usage: python ds_bias_base.py"""
import os, numpy as np, pandas as pd, csv
import harness as h
from analysis import load
rows = h.data.load(); V = np.array([r[1] for r in rows]); flat = V.ravel()
idx = {r[0].isoformat(): i for i, r in enumerate(rows)}
f = np.zeros(100); n = 0
for r in csv.DictReader(open(os.path.join(h.ROOT, "data", "game_ds.csv"))):
    if r["date"] < "2013-01-01" and r["ds"] != "": f[int(r["ds"])] += 1; n += 1
q = f / f.sum()
d = load("real", "light"); d = d[(d.pat == "dana") & (d.kind == "farak") & (d["sub"] == "core")]
out = []
for r in d.itertuples():
    p = r.id.split(":"); c2 = p[3].rsplit("-", 1); i2 = idx.get(c2[0])
    if i2 is None: continue
    b = i2 * 4 + int(c2[1]); S = [int(x) for x in str(r.nums).split()]
    m = int(r.cells)
    if len(flat) < b + 1 + m: continue
    pos = (b + 1 + np.arange(m)) % 4
    pn = 1.0
    for g in pos:
        pn *= 1 - (q[S].sum() if g == 3 else len(S) / 100.0)
    out.append((r.hit, r.p, 1 - pn, r.date[:4]))
x = pd.DataFrame(out, columns=["hit", "unif", "dsbias", "year"])
print("n", len(x), "hit %.4f  uniform %.4f  DS-bias-expected %.4f  (DS bias adds %.4f)" % (x.hit.mean(), x.unif.mean(), x.dsbias.mean(), x.dsbias.mean() - x.unif.mean()))
print("lift vs uniform %.3f, vs DS-bias %.3f" % (x.hit.mean() / x.unif.mean(), x.hit.mean() / x.dsbias.mean()))
