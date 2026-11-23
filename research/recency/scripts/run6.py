import sys; sys.path.insert(0,'.')
from common import *
d,A,dsd,dsv=load_all(); y,mon=year_month(d); N=len(d); G=['fd','gb','gl','ds']
X=np.stack([A[g] for g in G],1).reshape(-1); Y=np.repeat(y,4); gid=np.tile(np.arange(4),N); T=len(X)
def panel(W,sel,era,uniform_null=None):
    xs=X if uniform_null is None else uniform_null
    res={}  # c -> [numberdays, hits]
    cnt=np.zeros(100,int); 
    # sliding counts
    out_nd=np.zeros(6);out_h=np.zeros(6)
    for p in range(W,T):
        if p==W:
            cnt=np.bincount(xs[:W],minlength=100)
        else:
            cnt[xs[p-W-1]]-=1; cnt[xs[p-1]]+=1
        if not (sel[p] and era[0]<=Y[p]<=era[1]): continue
        cc=np.minimum(cnt,5)
        nd=np.bincount(cc,minlength=6); out_nd+=nd
        out_h[min(cnt[xs[p]],5)]+=1
    return out_nd,out_h
rng=np.random.default_rng(3)
U=rng.integers(0,100,T)
print('W target era | rate% for c=0,1,2,3+  (numberdays n) ; z for c>=1 vs 1%')
for W in (4,8,12,24,40):
    for tn,tg in (('ds',3),('gl',2),('gb',1),('fd',0),('all',None)):
        sel=(gid==tg) if tg is not None else np.ones(T,bool)
        for en,era in (('13-26',(2013,2026)),('18-26',(2018,2026))):
            if tg is None or W in (8,12,24):
                nd,h=panel(W,sel,era)
                r=h/np.maximum(nd,1)*100
                c1=(h[1:].sum(),nd[1:].sum()); z=(c1[0]-c1[1]/100)/np.sqrt(c1[1]/100)
                c2=(h[2:].sum(),nd[2:].sum()); z2=(c2[0]-c2[1]/100)/np.sqrt(max(c2[1]/100,1e-9))
                print(W,tn,en,'|',' '.join('c%d %.2f(%d)'%(c,r[c],nd[c]) for c in range(4)),'c3+ %.2f(%d)'%(h[3:].sum()/max(nd[3:].sum(),1)*100,nd[3:].sum()),'| c>=1 %.3f z %.1f | c>=2 %.3f z %.1f'%(c1[0]/c1[1]*100,z,c2[0]/max(c2[1],1)*100,z2),flush=True)
# null control (uniform random series)
nd,h=panel(12,np.ones(T,bool),(2013,2026),U); print('NULL W12 all',np.round(h/nd*100,2))
