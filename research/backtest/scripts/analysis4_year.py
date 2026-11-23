"""Within-year shuffle null: max-test + tables sorted by lift / set size. Usage: python analysis4_year.py"""
import os, glob, numpy as np, pandas as pd
from analysis import load, variants, table, CACHE, OUT
from analysis2 import max_test
real = pd.read_csv(os.path.join(OUT, "variants_real.csv")); real = real[real.pat.isin(["copy","family","dana","tokri"])]
res = []
for f in sorted(glob.glob(os.path.join(CACHE, "shufY_*_light.csv.gz"))):
    tg = os.path.basename(f).replace("_light.csv.gz", "")
    t = table(variants(load(tg, "light"), None)); t["tag"] = tg; res.append(t)
nt = pd.concat(res); nt.to_csv(os.path.join(OUT, "variants_yearshuffle_light.csv.gz"), index=False)
print("year-shuffle runs:", nt.tag.nunique())
mt = max_test(real, nt); mt.to_csv(os.path.join(OUT, "max_test_yearshuf.csv"), index=False); print(mt.to_string())
for pat, name in {"copy":"shape=all game=all","family":"shape=all size=all all","dana":"kind=all all core window=sd","tokri":"window=365d top6"}.items():
    g = nt[(nt.pat==pat)&(nt.variant==name)]; print(pat, name, "yearshuf lift mean %.3f z mean %.2f max %.2f"%(g.lift.mean(), g.z.mean(), g.z.max()))
g = nt[(nt.pat=="dana")&(nt.variant=="kind=farak all core window=sd")]; print("farak variant under yearshuf: lift", g.lift.round(3).tolist(), "z", g.z.round(2).tolist())
r = real[real.eligible].copy()
cols = ["pat","variant","n","avg_set","lift","lift_lo","lift_hi","z","roi_%"]
print("\nTOP lift (eligible, n>=100):"); print(r.sort_values("lift", ascending=False).head(15)[cols].to_string())
r["bucket"] = pd.cut(r.avg_set, [0,2.5,4.5,8,100]); print("\nbest z per set-size bucket:")
print(r.sort_values("z", ascending=False).groupby(["pat","bucket"], observed=True).head(1)[cols+["bucket"]].to_string())
