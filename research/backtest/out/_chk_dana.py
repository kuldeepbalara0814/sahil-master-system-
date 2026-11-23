import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))+"/../scripts")
sys.path.insert(0,"/tmp/claude-0/-root-myproject/d4afdbac-f07c-47bf-ad35-3dfa8ff63430/scratchpad/sms")
import numpy as np, pandas as pd
from analysis import load
from lab import data
rows=data.load(); V=np.array([r[1] for r in rows])
f=np.bincount(V.ravel(),minlength=100)/V.size
print("marginal freq min/max x100:",f.min()*100,f.max()*100)
d=load("real","light"); d=d[d.pat=="dana"]
print(d.kind.value_counts().head(), d["sub"].value_counts().head(8))
d=d[(d["sub"]=="core")]
for k in ["farak","gap","same"]:
    x=d[d.kind==k].copy()
    sf=np.array([f[[int(v) for v in s.split()]].sum() for s in x.nums])
    x["pe"]=1-(1-sf)**x.cells
    print(k,len(x),"avg_s %.2f"%x.s.mean(),"hit %.4f"%x.hit.mean(),"p_unif %.4f"%x.p.mean(),"p_emp %.4f"%x.pe.mean(), x.wlen.value_counts().to_dict())
    for y,g in x.groupby("year") if "year" in x else []:
        pass
    x["half"]=(x.date>="2020-07-01")
    print(x.groupby("half").agg(h=("hit","mean"),p=("p","mean"),pe=("pe","mean"),n=("hit","size")).round(4).to_string())
