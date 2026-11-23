"""danaD (live dana map) persistence: map jo kal/pichle 3 din hit hua, kya aaj zyada hit karta hai? real vs year-shuffle vs row-shuffle. Usage: python analysis6_persist.py"""
import os, glob, pandas as pd
from analysis import load, OUT, CACHE
from analysis2 import persistence
res = []
tags = ["real"] + [os.path.basename(f).replace("_light.csv.gz","") for f in sorted(glob.glob(os.path.join(CACHE,"shufY_*_light.csv.gz")))] + ["shufL_row11","shufL_col14"]
for tg in tags:
    d = load(tg, "light"); d = d[d.pat == "danaD"]
    r = pd.DataFrame(persistence(d, "danaD")); r["tag"] = tg; res.append(r); del d
x = pd.concat(res); x.to_csv(os.path.join(OUT, "persistence_danaD.csv"), index=False)
print(x.to_string())
