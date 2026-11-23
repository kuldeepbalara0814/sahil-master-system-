# walk-forward rule selection + permutation null (shuffle target within year)
import sys,time; sys.path.insert(0,'.')
from rules import *
d,A,dsd,dsv=load_all(); y,mon=year_month(d); N=len(d)
NP=int(sys.argv[1]) if len(sys.argv)>1 else 100
O=build(A); YRS=list(range(2013,2027)); yi=np.array([YRS.index(v) for v in y])
cand={}
for T in GAMES:
    R,S=O[T]
    for nm,(C,ok) in R.items():
        if (C>=0).sum(1).max()>4: continue
        cand[(T,nm)]=C
keys=list(cand)
def stats(t):
    """per rule per year: stake, hits"""
    St=np.zeros((len(keys),14)); Hi=np.zeros((len(keys),14))
    for k,(T,nm) in enumerate(keys):
        tt=t[T]; C=cand[(T,nm)]; valid=C>=0; m=valid.sum(1); hit=((C==tt[:,None])&valid).any(1)
        fire=m>0; fire[:5]=False
        St[k]=np.bincount(yi,weights=np.where(fire,m,0),minlength=14); Hi[k]=np.bincount(yi,weights=np.where(fire,hit,0),minlength=14)
    return St,Hi
def walk(St,Hi,crit='roi',start=5,minstake=500):
    """for each test year pick best rule per target using past; return per-target oos stake/hits and portfolio"""
    res={T:[0.0,0.0] for T in GAMES}; res['PORT']=[0.0,0.0]; res['years']=[]
    byyear=[]
    for yr in range(start,14):
        ps=St[:,:yr].sum(1); ph=Hi[:,:yr].sum(1)
        roi=np.where(ps>=minstake,95*ph/np.maximum(ps,1)-1,-9)
        if crit=='z': 
            e=ps/100; roi=np.where(ps>=minstake,(ph-e)/np.sqrt(np.maximum(e,1e-9)),-9)
        ys=0;yh=0
        for T in GAMES:
            idx=[k for k,(t,n) in enumerate(keys) if t==T]
            b=idx[int(np.argmax(roi[idx]))]
            ok=(roi[b]>0) if crit=='roi' else (roi[b]>2)
            if ok:
                res[T][0]+=St[b,yr]; res[T][1]+=Hi[b,yr]; ys+=St[b,yr]; yh+=Hi[b,yr]
        res['PORT'][0]+=ys; res['PORT'][1]+=yh
    return res
t0={g:A[g] for g in GAMES}
St,Hi=stats(t0); np.savez('../out/stats_real.npz',St=St,Hi=Hi,keys=np.array([a+'|'+b for a,b in keys]))
real={c:walk(St,Hi,c) for c in ('roi','z')}
def roi(r): return 95*r[1]/r[0]-1 if r[0]>0 else np.nan
for c in real: print(c,{k:(int(v[0]),int(v[1]),round(roi(v),3)) for k,v in real[c].items() if k!='years'})
rng=np.random.default_rng(7); null={c:{k:[] for k in ('fd','gb','gl','ds','PORT')} for c in ('roi','z')}
t1=time.time()
for p in range(NP):
    ts={}
    for g in GAMES:
        ts[g]=rng.integers(0,100,N)
    # rules use real sources; only target shuffled -> need per-target
    St2=np.zeros_like(St);Hi2=np.zeros_like(Hi)
    for k,(T,nm) in enumerate(keys):
        tt=ts[T]; C=cand[(T,nm)]; valid=C>=0; m=valid.sum(1); hit=((C==tt[:,None])&valid).any(1); fire=m>0; fire[:5]=False
        St2[k]=np.bincount(yi,weights=np.where(fire,m,0),minlength=14); Hi2[k]=np.bincount(yi,weights=np.where(fire,hit,0),minlength=14)
    for c in null:
        r=walk(St2,Hi2,c)
        for k in null[c]: null[c][k].append(roi(r[k]) if r[k][0]>0 else -1.0)
    if p%10==9:
        print(p+1,round(time.time()-t1),flush=True)
        import pickle; pickle.dump((real,null),open('../out/walk_null.pkl','wb'))
import pickle; pickle.dump((real,null),open('../out/walk_null.pkl','wb'))
for c in null:
    for k in null[c]:
        a=np.array(null[c][k]); r=roi(real[c][k]); print(c,k,'real OOS roi %.3f stake %d'%(r,real[c][k][0]),'null mean %.3f p95 %.3f  p(null>=real) %.3f'%(a.mean(),np.percentile(a,95),(a>=r).mean()))
