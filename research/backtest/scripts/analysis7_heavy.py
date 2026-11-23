"""Heavy sample (inc_h60 ya diya tag) ka analysis: naksha/naksha2/steps defaults + variants + ensemble vote-calibration. Usage: python analysis7_heavy.py [tag=inc_h60]"""
import os, sys, gzip, shutil, pandas as pd
from analysis import load, variants, table, CACHE, OUT
from analysis2 import ensemble, DEFAULTS
tag = sys.argv[1] if len(sys.argv) > 1 else "inc_h60"
for part in ("heavy", "ens"):
    src, dst = os.path.join(CACHE, f"{tag}_{part}.csv"), os.path.join(CACHE, f"{tag}_{part}.csv.gz")
    if os.path.exists(src):
        with open(src, "rb") as a, gzip.open(dst, "wb") as b: shutil.copyfileobj(a, b)
hv = load(tag, "heavy")
print("rows", len(hv), "days", hv.t.nunique(), hv.groupby("pat").size().to_dict())
t = table(variants(None, hv)); t.to_csv(os.path.join(OUT, f"variants_{tag}.csv"), index=False)
cols = ["pat","variant","n","avg_set","hit_rate","random_rate","lift","lift_lo","lift_hi","z","roi_%","eligible"]
for pat, name in DEFAULTS.items():
    r = t[(t.pat == pat) & (t.variant == name)]
    if len(r): print(r[cols].to_string(header=False))
print("\nTOP z eligible"); print(t[t.eligible].sort_values("z", ascending=False).head(12)[cols].to_string())
print("\nBOTTOM z eligible"); print(t[t.eligible].sort_values("z").head(5)[cols].to_string())
print("\nall-eligible: n=%d  z>2: %d  z<-2: %d  mean lift %.3f" % (t.eligible.sum(), ((t.z>2)&t.eligible).sum(), ((t.z<-2)&t.eligible).sum(), t[t.eligible].lift.mean()))
e, nd = ensemble(tag); e.to_csv(os.path.join(OUT, f"ensemble_{tag}.csv"), index=False); print("\nensemble days", nd); print(e.to_string())
