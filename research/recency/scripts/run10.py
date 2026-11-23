import sys,datetime; sys.path.insert(0,'.')
from common import *
d,A,dsd,dsv=load_all(); x=dsv; n=len(x); yd=np.array([int(s[:4]) for s in dsd])
# profile DS own lag 1..40 for 1980-2026 (leave-one-out baseline) and 2013-26
for a,b in ((1980,2026),(2013,2026)):
    q=np.where((yd>=a)&(yd<=b))[0]; xx=x[q]; N=len(xx); c=np.bincount(xx,minlength=100); e=(c*(c-1)).sum()/(N*(N-1))
    r=[(xx[L:]==xx[:-L]).mean()*100 for L in range(1,41)]
    print('DS own-lag %d-%d exp %.2f:'%(a,b,100*e),' '.join('%d:%.2f'%(L+1,v) for L,v in enumerate(r[:20])),'| 21-40 mean %.2f'%np.mean(r[20:]))
    print('   lags 2-6 mean %.2f, 7-12 mean %.2f, 13-40 mean %.2f'%(np.mean(r[1:6]),np.mean(r[6:12]),np.mean(r[12:])))
# bet set {x-2..x-5}
S=np.stack([np.concatenate([np.full(L,-1),x[:-L]]) for L in (2,3,4,5)],1)
C=S.copy()
for j in range(1,4):
    for l in range(j): C[:,j]=np.where(C[:,j]==C[:,l],-1,C[:,j])
valid=C>=0; m=valid.sum(1); hit=((C==x[:,None])&valid).any(1); m[:5]=0
dow=np.array([datetime.date(int(s[:4]),int(s[5:7]),int(s[8:10])).weekday() for s in dsd]); dom=np.array([int(s[8:10]) for s in dsd]); mo=np.array([int(s[5:7]) for s in dsd])
prev=np.concatenate([[0],hit[:-1]]).astype(int)
dist8=np.array([len(set(x[max(0,i-8):i])) for i in range(n)])
rep1=(np.concatenate([[-1],x[:-1]])==np.concatenate([[-1,-1],x[:-2]])) # x[t-1]==x[t-2]
conds={}
for k in range(7): conds['dow=%d'%k]=dow==k
for a,b in ((1,7),(8,14),(15,21),(22,31)): conds['dom%d-%d'%(a,b)]=(dom>=a)&(dom<=b)
for k in range(1,13): conds['mon=%d'%k]=mo==k
conds['prevhit']=prev==1; conds['prev2hit']=(prev==1)&(np.concatenate([[0,0],hit[:-2]])==1)
for v in (5,6,7): conds['dist8<=%d'%v]=dist8<=v
conds['dist8==8']=dist8==8
conds['x[t-1]==x[t-2]']=rep1
conds['m<4']=m<4
names=list(conds)
tr=(yd<=1999)&(m>0); te=(yd>=2000)&(m>0)
def zs(h,mask):
    out=[]
    for nm in names:
        c=conds[nm]&mask; r=(~conds[nm])&mask; s1=m[c].sum(); s0=m[r].sum()
        if s1<800 or s0<800: out.append(0);continue
        p=h[mask].sum()/m[mask].sum(); r1=h[c].sum()/s1; r0=h[r].sum()/s0
        out.append((r1-r0)/np.sqrt(p*(1-p)*(1/s1+1/s0)))
    return np.array(out)
z0=zs(hit.astype(float),tr); rng=np.random.default_rng(2)
idx=np.where(tr)[0]; mx=[]
for _ in range(500):
    h=hit.astype(float).copy(); h[idx]=h[rng.permutation(idx)]; mx.append(np.abs(zs(h,tr)).max())
mx=np.array(mx); print('train 1966-99 base rate %.3f%%, null max|z| p95 %.2f; tested %d'%(100*hit[tr].sum()/m[tr].sum(),np.percentile(mx,95),len(names)))
zt=zs(hit.astype(float),te)
for i in np.argsort(-np.abs(z0))[:8]:
    c=conds[names[i]]
    print('%-16s train z %+.2f (p_adj %.2f) | test 2000-26: rate in %.3f vs out %.3f  z %+.2f; roi95 in %+.2f'%(names[i],z0[i],(mx>=abs(z0[i])).mean(),100*hit[c&te].sum()/m[c&te].sum(),100*hit[~c&te].sum()/m[~c&te].sum(),zt[i],95*hit[c&te].sum()/m[c&te].sum()-1))
# by decade rate of base bet
for a,b in ((1966,1979),(1980,1989),(1990,1999),(2000,2009),(2010,2019),(2020,2026)):
    q=(yd>=a)&(yd<=b)&(m>0); print(a,b,'rate %.3f roi %+.3f'%(100*hit[q].sum()/m[q].sum(),95*hit[q].sum()/m[q].sum()-1),'days/yr',q.sum()/(b-a+1))
q=(yd>=2022)&(m>0); st=m[q].sum(); h=hit[q].sum(); print('2022-26: stake',st,'hits',h,'rate %.3f roi %+.2f'%(100*h/st,95*h/st-1))
# month bootstrap for 2013-26 and 2000-26
for a in (2000,2013,2022):
    q=(yd>=a)&(m>0); mm=np.array([int(s[:4])*12+int(s[5:7]) for s in dsd])[q]; um,inv=np.unique(mm,return_inverse=True)
    Sx=np.bincount(inv,weights=m[q]); Hx=np.bincount(inv,weights=hit[q]); b=[95*Hx[ix].sum()/Sx[ix].sum()-1 for ix in (rng.integers(0,len(um),(2000,len(um))))]
    print('%d+ bootstrap roi95 CI'%a,np.round(np.percentile(b,[2.5,50,97.5]),3))
