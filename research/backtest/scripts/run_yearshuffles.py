"""Within-year row shuffle (saal ke andar din badal do; DS/saal ka bias bacha rehta hai, pattern/serial toot jata hai). Light patterns, ek process.
Cache: ../cache/shufY_<seed>_light.csv.gz  Usage: python run_yearshuffles.py [N=4]  (seeds 31..)"""
import os, sys, time, numpy as np
import harness as h
N = int(sys.argv[1]) if len(sys.argv) > 1 else 4
orig = h.data.load
def make_year(seed):
    rows = orig(); rng = np.random.default_rng(seed)
    V = np.array([r[1] for r in rows]); yrs = np.array([r[0].year for r in rows])
    idx = np.arange(len(rows))
    for y in np.unique(yrs):
        ii = idx[yrs == y]; idx[ii] = rng.permutation(ii)
    V = V[idx]
    return [(r[0], [int(x) for x in V[i]], "shuf") for i, r in enumerate(rows)]
for s in range(31, 31 + N):
    f = os.path.join(h.CACHE, f"shufY_{s}_light.csv.gz")
    if os.path.exists(f): continue
    t0 = time.time()
    h.make_data = lambda shuffle=None, seed=0, s=s: make_year(s)
    h.init("row", s)
    rows = []
    for t in h.valid_ts(h.G["full"]): rows += h.light_day(t)
    h.write(f, h.COLS, rows)
    open(os.path.join(h.OUT, "progress_shuffles.txt"), "a").write(f"shufY_{s} done {time.time()-t0:.0f}s\n")
