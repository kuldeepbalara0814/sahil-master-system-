import sys; sys.path.insert(0,'.')
from common import *
d,A,dsd,dsv=load_all(); x=dsv; yd=np.array([int(s[:4]) for s in dsd])
C=np.stack([np.concatenate([np.full(L,-1),x[:-L]]) for L in (2,3,4,5)],1)
for j in range(1,4):
    for l in range(j): C[:,j]=np.where(C[:,j]==C[:,l],-1,C[:,j])
v=C>=0; m=v.sum(1); h=((C==x[:,None])&v).any(1); q=np.arange(len(x))>=6
pl=np.where(h,95-m,-m).astype(float)
def run(sel,name):
    p=pl[sel&q]; hh=h[sel&q]
    mx=0;c=0
    for a in hh:
        c=0 if a else c+1; mx=max(mx,c)
    cs=np.cumsum(p); dd=(np.maximum.accumulate(np.maximum(cs,0))-cs).max()
    rng=np.random.default_rng(1); w=[];fin=[]
    for _ in range(3000):
        s=rng.choice(p,1000); c=np.cumsum(s); w.append((np.maximum.accumulate(np.maximum(c,0))-c).max()); fin.append(c[-1])
    print(name,'days',len(p),'mean/day %.2f'%p.mean(),'longest no-hit run',mx,'hist maxDD %.0f'%dd,'1000-day iid: worst DD median %.0f p95 %.0f; P(loss after 1000d) %.2f; end p5 %.0f median %.0f'%(np.median(w),np.percentile(w,95),(np.array(fin)<0).mean(),np.percentile(fin,5),np.median(fin)))
run(yd>=1980,'1980-2026'); run(yd>=2013,'2013-2026'); run(yd>=2022,'2022-2026')
