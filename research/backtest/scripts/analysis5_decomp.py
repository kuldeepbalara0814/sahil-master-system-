"""Farak core lift ka cell-wise tukda: kis game/din-offset ke cell me hit aata hai; series-only numbers; saal-wise. Usage: python analysis5_decomp.py"""
import os, numpy as np, pandas as pd
import harness as h
from analysis import load, OUT
rows = h.data.load(); flat = np.array([r[1] for r in rows]).ravel()
idx = {r[0].isoformat(): i for i, r in enumerate(rows)}
d = load("real", "light"); d = d[(d.pat == "dana") & (d.kind == "farak")][["id","sub","nums","cells","date","hit","p","s"]]
core = d[d["sub"]=="core"].set_index("id"); cs = d[d["sub"]=="core+series"].set_index("id")
cat = {}   # key -> [exp, hit, month-cluster dict]
def add(key, e, hh, m):
    c = cat.setdefault(key, [0.0, 0.0, {}]); c[0] += e; c[1] += hh; c[2][m] = c[2].get(m, 0.0) + hh - e
for rid, r in core.iterrows():
    p = rid.split(":"); c2 = p[3].rsplit("-", 1); i2 = idx.get(c2[0])
    if i2 is None: continue
    b = i2*4 + int(c2[1]); m = int(r.cells)
    if len(flat) < b+1+m: continue
    S = np.array([int(x) for x in str(r.nums).split()]); w = flat[b+1:b+1+m]
    ser = None
    if rid in cs.index:
        S2 = set(int(x) for x in str(cs.loc[rid,"nums"]).split()); ser = np.array(sorted(S2 - set(S.tolist())))
    k = np.arange(m); g = (b+1+k) % 4; dayoff = (int(c2[1])+1+k)//4
    hit = np.isin(w, S).astype(float); e = len(S)/100.0
    mo = r.date[:7]
    for gg in range(4): add(("game", gg), e*(g==gg).sum(), hit[g==gg].sum(), mo)
    for lab, lo, hi in (("d0",0,0),("d1",1,1),("d2",2,2),("d3-5",3,5),("d6-10",6,10),("d11+",11,999)):
        mk = (dayoff>=lo)&(dayoff<=hi); add(("day", lab), e*mk.sum(), hit[mk].sum(), mo)
    if ser is not None and len(ser):
        hs = np.isin(w, ser).astype(float); add(("series_only", "all"), len(ser)/100.0*m, hs.sum(), mo)
    add(("core_cells","all"), e*m, hit.sum(), mo)
    add(("year", r.date[:4]), e*m, hit.sum(), mo)
out = []
for k, (E, H, cl) in sorted(cat.items(), key=lambda x: str(x[0])):
    se = np.sqrt(sum(v*v for v in cl.values()))
    out.append((k[0], k[1], round(E,1), int(H), round(H/E,3), round((H-E)/se,2)))
df = pd.DataFrame(out, columns=["split","key","exp_cellhits","cellhits","lift","z_clustered"]); print(df.to_string()); df.to_csv(os.path.join(OUT,"farak_decomp.csv"), index=False)
