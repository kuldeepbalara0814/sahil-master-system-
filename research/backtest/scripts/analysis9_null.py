"""Heavy shuffle null (inc*_h60) vs real: default lift/z aur max-test (naksha/naksha2/steps/ALL). Usage: python analysis9_null.py"""
import os, glob, gzip, shutil, pandas as pd, numpy as np
from analysis import load, variants, table, CACHE, OUT
from analysis2 import max_test, DEFAULTS
real = pd.read_csv(os.path.join(OUT, "variants_inc_h60.csv")); real = real[real.pat.isin(["naksha","naksha2","steps"])]
res = []
for f in sorted(glob.glob(os.path.join(CACHE, "inc[rc]o[wl]*_h60_heavy.csv"))):
    tg = os.path.basename(f).replace("_h60_heavy.csv", ""); 
    if not os.path.exists(os.path.join(CACHE, f"{tg}_h60_done.txt")) or len(open(os.path.join(CACHE, f"{tg}_h60_done.txt")).read().split()) < 237: continue
    with open(f, "rb") as a, gzip.open(os.path.join(CACHE, f"{tg}_h60_heavy.csv.gz"), "wb") as b: shutil.copyfileobj(a, b)
    t = table(variants(None, load(f"{tg}_h60", "heavy"))); t["tag"] = tg; res.append(t)
nt = pd.concat(res); nt.to_csv(os.path.join(OUT, "variants_shuf_heavy.csv.gz"), index=False); print("null runs", nt.tag.unique())
print(max_test(real, nt).to_string())
for pat, name in DEFAULTS.items():
    g = nt[(nt.pat == pat) & (nt.variant == name)]
    if len(g): print(pat, name, "null lifts", g.lift.round(3).tolist(), "z", g.z.round(2).tolist())
