"""Analyse part 1 -> out/p1_summary_<game>_<scheme>.csv + printed headline. usage: analyse1.py GAME SCHEME"""
import sys, csv, os
import numpy as np
from common import OUT
from stats import *

def load(game, scheme):
    z = np.load(os.path.join(OUT, f"p1_{game}_{scheme}.npz"), allow_pickle=True)
    return z["S"], z["D"], list(z["cfgs"]), list(z["dcfgs"])

def table(game, scheme, a=1966, b=2026):
    S, D, cfgs, dcfgs = load(game, scheme)
    r = zscan(S, a, b)
    return S, D, cfgs, dcfgs, r

def rows(cfgs, r, minn=50):
    out = []
    for i, c in enumerate(cfgs):
        if r["n"][i] < minn: continue
        out.append(dict(cfg=c, n=int(r["n"][i]), hits=int(r["hit"][i]), exp=round(r["exp"][i], 1), lift=round(r["lift"][i], 3),
                        lo=round(r["lift_lo"][i], 3), hi=round(r["lift_hi"][i], 3), z=round(r["z"][i], 2), p=round(r["p"][i], 4), size=round(r["size"][i], 2)))
    return out

if __name__ == "__main__":
    game, scheme = sys.argv[1], sys.argv[2]
    S, D, cfgs, dcfgs, r = table(game, scheme)
    R = S.shape[0] - 1
    rs = rows(cfgs, r)
    with open(os.path.join(OUT, f"p1_summary_{game}_{scheme}.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rs[0].keys())); w.writeheader(); w.writerows(rs)
    elig = r["n"] >= 200
    mx, pf = fwer(r, elig)
    print(game, scheme, "shuffles", R, "cfgs", len(cfgs), "eligible", elig.sum(), "maxz", round(mx, 2), "FWER p", pf)
    print("fraction cfg z>2 real:", round((r["z"][elig] > 2).mean(), 3), " shuffles:", round((r["zs"][:, elig] > 2).mean(), 3))
    for x in sorted(rs, key=lambda x: -x["z"])[:8]: print(x)
