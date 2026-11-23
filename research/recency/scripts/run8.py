import sys; sys.path.insert(0,'.')
from run7 import *
K=int(sys.argv[1]) if len(sys.argv)>1 else 4
rows=[]
for tg in range(4):
    sel=gid==tg
    for yr in range(2018,2027):
        tr=sel&(Y<yr)&(pos>=LM); te=np.where(sel&(Y==yr)&(pos>=LM))[0]
        hits=M[tr].sum(0); order=np.argsort(-hits,kind='stable')[:K]
        C=S[te][:,order].copy()
        for j in range(1,K):
            for l in range(j): C[:,j]=np.where(C[:,j]==C[:,l],-1,C[:,j])
        valid=C>=0; m=valid.sum(1); hit=((C==X[te][:,None])&valid).any(1)
        W=S[te][:,:12]; distinct=np.array([len(set(r)) for r in W])
        for a,i in enumerate(te):
            rows.append((tg,yr,i//4,m[a],int(hit[a]),distinct[a]))
R=np.array(rows); tg,yr,li,m,hit,dist=R.T
dates=np.array(d)[li] if False else None
dd=np.array(load_all()[0])[li]
import datetime
dow=np.array([datetime.date(int(s[:4]),int(s[5:7]),int(s[8:10])).weekday() for s in dd]); dom=np.array([int(s[8:10]) for s in dd]); mo=np.array([int(s[5:7]) for s in dd])
# prev-day-same-game hit & hits in last 10 bets
prev=np.zeros(len(R));last10=np.zeros(len(R))
for g in range(4):
    idx=np.where(tg==g)[0]; h=hit[idx].astype(float)
    prev[idx[1:]]=h[:-1]; c=np.cumsum(np.concatenate([[0],h])); 
    for q in range(len(idx)): last10[idx[q]]=c[q]-c[max(0,q-10)]
conds={}
for g in range(4): conds['game=%s'%G[g]]=tg==g
for k in range(7): conds['dow=%d'%k]=dow==k
for a,b in ((1,7),(8,14),(15,21),(22,31)): conds['dom %d-%d'%(a,b)]=(dom>=a)&(dom<=b)
for k in range(1,13): conds['month=%d'%k]=mo==k
conds['prevhit']=prev==1; conds['prev_nohit']=prev==0; conds['last10>=2']=last10>=2; conds['last10==0']=last10==0
for v in (8,9,10,11): conds['distinct12<=%d'%v]=dist<=v
conds['m=4']=m==4; conds['m<=3']=m<=3
names=list(conds); 
def zs(h):
    out=[]
    for n in names:
        c=conds[n]; s1=m[c].sum(); s0=m[~c].sum()
        if s1<500 or s0<500: out.append(0); continue
        r1=h[c].sum()/s1; r0=h[~c].sum()/s0; p=h.sum()/m.sum()
        out.append((r1-r0)/np.sqrt(p*(1-p)*(1/s1+1/s0)))
    return np.array(out)
z0=zs(hit.astype(float)); rng=np.random.default_rng(5)
mx=np.array([np.abs(zs(rng.permutation(hit).astype(float))).max() for _ in range(1000)])
print('overall: stake %d hits %d rate %.3f%% roi95 %+.3f'%(m.sum(),hit.sum(),100*hit.sum()/m.sum(),95*hit.sum()/m.sum()-1))
print('conditions tested',len(names),' null max|z| 95th pct %.2f 99th %.2f'%(np.percentile(mx,95),np.percentile(mx,99)))
o=np.argsort(-np.abs(z0))[:10]
for i in o:
    c=conds[names[i]]; print('%-16s days %5d stake %6d rate %.3f%% (rest %.3f%%) z %+.2f  p_adj %.3f roi95 %+.2f'%(names[i],c.sum(),m[c].sum(),100*hit[c].sum()/m[c].sum(),100*hit[~c].sum()/m[~c].sum(),z0[i],(mx>=abs(z0[i])).mean(),95*hit[c].sum()/m[c].sum()-1))
print('by year (all games):'); 
for Y_ in range(2018,2027):
    c=yr==Y_; print(Y_,'days %d stake %d hits %d rate %.3f roi %+.2f'%(c.sum(),m[c].sum(),hit[c].sum(),100*hit[c].sum()/m[c].sum(),95*hit[c].sum()/m[c].sum()-1))
for g in range(4):
    c=tg==g; print(G[g],'stake %d hits %d rate %.3f roi %+.2f'%(m[c].sum(),hit[c].sum(),100*hit[c].sum()/m[c].sum(),95*hit[c].sum()/m[c].sum()-1))
# slope of yearly rate
ys=np.arange(2018,2027); rt=np.array([hit[yr==a].sum()/m[yr==a].sum() for a in ys]); print('yearly slope of rate per yr %.4f%%'%(100*np.polyfit(ys,rt,1)[0]))
# month bootstrap
mm=(yr*12+mo); um,inv=np.unique(mm,return_inverse=True); Sx=np.bincount(inv,weights=m); Hx=np.bincount(inv,weights=hit)
b=[]; 
for _ in range(2000):
    ix=rng.integers(0,len(um),len(um)); b.append(95*Hx[ix].sum()/Sx[ix].sum()-1)
print('month-block bootstrap roi95 CI',np.round(np.percentile(b,[2.5,50,97.5]),3))
dayc=len(set(li[yr>=2022]))/4.9; print('betting days/yr',dayc,'numbers/yr', m[yr>=2022].sum()/4.9)
