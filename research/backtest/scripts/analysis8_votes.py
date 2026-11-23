"""Vote count vs recency: kya votes ka asar 'number haal me aaya' se alag hai? Usage: python analysis8_votes.py [tag=inc_h60]"""
import os, sys, numpy as np, pandas as pd
import harness as h
from analysis import CACHE, OUT
tag = sys.argv[1] if len(sys.argv) > 1 else "inc_h60"
e = pd.read_csv(os.path.join(CACHE, f"{tag}_ens.csv.gz")); day = e[e.n == -1].set_index("t")["hit"]; v = e[e.n >= 0].copy()
rows = h.data.load(); V = np.array([r[1] for r in rows])
v["votes"] = v[["v_nak","v_nak2","v_fam","v_copy","v_dana","v_steps"]].sum(axis=1); v["base"] = v.t.map(day) / 100.0
def rc(t, n, d=12): return int((V[max(0, t-d):t] == n).sum())
v["rec12"] = [rc(t, n) for t, n in zip(v.t, v.n)]
v["recb"] = pd.cut(v.rec12, [-1, 0, 1, 10], labels=["0", "1", "2+"])
v["vb"] = pd.cut(v.votes, [-1, 3, 8, 14, 999], labels=["0-3", "4-8", "9-14", "15+"])
g = v.groupby("recb", observed=True).apply(lambda x: pd.Series(dict(n=len(x), hit=x.hit.mean(), rnd=x.base.mean(), lift=x.hit.sum()/x.base.sum())), include_groups=False); print("by recency (last 12 days count)"); print(g.round(4).to_string())
g = v.groupby(["recb", "vb"], observed=True).apply(lambda x: pd.Series(dict(n=len(x), hit=x.hit.mean(), rnd=x.base.mean(), lift=x.hit.sum()/x.base.sum())), include_groups=False); print("recency x votes"); print(g.round(4).to_string())
c = np.corrcoef(v.votes, v.rec12)[0, 1]; print("corr(votes, recent count) %.3f" % c)
g.reset_index().to_csv(os.path.join(OUT, f"votes_recency_{tag}.csv"), index=False)
