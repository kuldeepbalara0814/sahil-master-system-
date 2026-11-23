import sys,csv; sys.path.insert(0,'.')
from rules import *
d,A,dsd,dsv=load_all(); y,mon=year_month(d)
O=build(A); rows=[]
per=[('all',2013,2026),('13-17',2013,2017),('18-22',2018,2022),('23-26',2023,2026),('22-26',2022,2026)]
for T in GAMES:
    R,S=O[T]; t=A[T]; F=np.full((len(t),100),0.01)
    for name,(C,ok) in R.items():
        fire,m,hit,p0=evaluate(C,t,F)
        fire&=(np.arange(len(t))>=5)
        r=dict(target=T,rule=name)
        for pn,a,b in per:
            s=summarize(fire,m,hit,p0,(y>=a)&(y<=b))
            for k in ('days','rate_per_no','exp_adj','lift','roi95','roi90','z'): r[pn+'_'+k]=s[k]
        s=summarize(fire,m,hit,p0)
        ci=month_boot(fire,m,hit,p0,mon)
        r['all_roi95_lo'],r['all_roi95_hi']=ci[0]; r['all_lift_lo'],r['all_lift_hi']=ci[1]
        ci=month_boot(fire,m,hit,p0,mon,sel=(y>=2022))
        r['2226_roi95_lo'],r['2226_roi95_hi']=ci[0]
        # per-year rate slope
        yy=[];rt=[];w=[]
        for Y in range(2013,2027):
            q=summarize(fire,m,hit,p0,y==Y)
            if q['stake']>0: yy.append(Y);rt.append(q['hits']/q['stake']/ (q['exp_adj'] if q['exp_adj']>0 else 1));w.append(q['stake'])
        r['slope_lift_per_yr']=np.polyfit(yy,rt,1,w=np.sqrt(w))[0] if len(yy)>3 else np.nan
        r['days_per_yr_22_26']=r['22-26_days']/4.9
        rows.append(r)
keys=list(rows[0].keys())
with open('../out/rules_2013_26.csv','w') as f:
    w=csv.DictWriter(f,keys); w.writeheader()
    for r in rows: w.writerow({k:(round(v,4) if isinstance(v,float) else v) for k,v in r.items()})
print(len(rows))
