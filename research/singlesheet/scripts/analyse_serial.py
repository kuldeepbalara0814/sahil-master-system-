"""Compare DS month: real vs within-year shuffle (p1) and vs repeat-preserving null (p1s); eras + held-out. usage: analyse_serial.py [GAME]"""
import sys, os, numpy as np
from common import OUT
from stats import *
game = sys.argv[1] if len(sys.argv) > 1 else "DS"
def L(fn):
    z = np.load(os.path.join(OUT, fn), allow_pickle=True); return z["S"], list(z["cfgs"])
S1, cf = L(f"p1_{game}_month.npz"); S2, cf2 = L(f"p1s_{game}_month.npz")
assert cf == cf2
for nm, S in (("within-year shuffle", S1), ("repeat-preserving null", S2)):
    r = zscan(S); el = r["n"] >= 200; mx, pf = fwer(r, el)
    print(f"== {nm}: R={S.shape[0]-1} elig={el.sum()} maxz={mx:.2f} FWER p={pf:.3f}  frac z>2 real={(r['z'][el]>2).mean():.3f} null={(r['zs'][:,el]>2).mean():.3f}  mean z real={r['z'][el].mean():.2f}")
    top = np.argsort(-np.where(el, r["z"], -9))[:5]
    for i in top: print("  ", cf[i], "n", int(r["n"][i]), "lift", round(r["lift"][i], 3), "z", round(r["z"][i], 2), "p", round(r["p"][i], 3))
# eras for the top configs under shuffle null, scored vs serial null
r1 = zscan(S1); el = r1["n"] >= 200
top = np.argsort(-np.where(el, r1["z"], -9))[:5]
print("== eras: top-5 shuffle-null configs, z vs shuffle / z vs serial / lift")
for e, a, b in ERAS_DS:
    ra, rb = zscan(S1, a, b), zscan(S2, a, b)
    print(e, [(round(ra["z"][i], 1), round(rb["z"][i], 1), round(ra["lift"][i], 2)) for i in top])
print("== held-out: pick top-20 cfgs (by z) on 1966-1999, evaluate 2000-2026")
for nm, S in (("shuffle", S1), ("serial", S2)):
    ra = zscan(S, 1966, 1999); rb = zscan(S, 2000, 2026)
    e = ra["n"] >= 100
    sel = np.argsort(-np.where(e, ra["z"], -9))[:20]
    print(nm, "train z mean", round(ra["z"][sel].mean(), 2), "test z mean", round(rb["z"][sel].mean(), 2), "test lift mean", round(np.nanmean(rb["lift"][sel]), 3), "frac test z>1.64", round((rb["z"][sel] > 1.64).mean(), 2), "cfgs", sel[:3].tolist())
# real-data z of same selected cfgs vs serial-null distribution max over test
