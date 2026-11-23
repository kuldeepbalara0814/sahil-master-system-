"""control_recent.csv se paired stats (farak vs matched recent-pair control, uniform). Usage: python control_stats.py"""
import pandas as pd,numpy as np
x=pd.read_csv('../out/control_recent.csv' if __import__('os').path.exists('../out/control_recent.csv') else 'out/control_recent.csv')
def st(g):
    d=g.hit-g.ctrl; n=len(g); se=d.std(ddof=1)/np.sqrt(n)
    s2=(g.hit-g.p); se2=s2.std(ddof=1)/np.sqrt(n)
    return pd.Series(dict(n=n,hit=g.hit.mean(),ctrl=g.ctrl.mean(),unif=g.p.mean(),diff=d.mean(),lo=d.mean()-1.96*se,hi=d.mean()+1.96*se,z_vs_ctrl=d.mean()/se,z_vs_unif=s2.mean()/se2,lift_unif=g.hit.mean()/g.p.mean(),lift_ctrl=g.ctrl.mean()/g.p.mean(),hit_over_ctrl=g.hit.mean()/g.ctrl.mean()))
print(st(x).round(4).to_string())
print(x.groupby('year').apply(st).round(3).to_string())
