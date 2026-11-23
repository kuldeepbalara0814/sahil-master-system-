import sys; sys.path.insert(0,'.')
from common import *
d,A,dsd,dsv=load_all(); y,mon=year_month(d); N=len(d); G=['fd','gb','gl','ds']
X=np.stack([A[g] for g in G],1).reshape(-1); Y=np.repeat(y,4); gid=np.tile(np.arange(4),N); T=len(X)
LM=40
pos=np.arange(T)
# slot matrix: S[p,L-1]=X[p-L]
S=np.full((T,LM),-1)
for L in range(1,LM+1): S[L:,L-1]=X[:-L]
M=(S==X[:,None])              # match per slot
def wf(tg,k,start=2018,crit='rate',lags=range(1,LM+1),dedupe=True,drop_multi=False):
    sel=gid==tg
    tot=np.zeros(3); peryear=[]
    lagidx=np.array(list(lags))-1
    for yr in range(start,2027):
        tr=sel&(Y<yr)&(pos>=LM); te=sel&(Y==yr)&(pos>=LM)
        hits=M[tr][:,lagidx].sum(0); n=tr.sum()
        order=lagidx[np.argsort(-hits,kind='stable')][:k]
        # bet: numbers in chosen slots, dedupe
        C=S[te][:,order].copy()
        if dedupe:
            for j in range(1,C.shape[1]):
                for l in range(j): C[:,j]=np.where(C[:,j]==C[:,l],-1,C[:,j])
        if drop_multi:   # drop numbers appearing >=2 times in last 12
            W=S[te][:,:12]
            cnt=(W[:,:,None]==C[:,None,:]).sum(1)
            C=np.where(cnt>=2,-1,C)
        valid=C>=0; m=valid.sum(1); hit=((C==X[te][:,None])&valid).any(1)
        tot+=[m.sum(),hit.sum(),(m*1.0).sum()/100]; peryear.append((yr,int(m.sum()),int(hit.sum()),list(order+1)))
    return tot,peryear
if __name__=='__main__':
    for tg in (3,2,1,0):
        print('=== target',G[tg],'walk-forward 2018-26 top-k lag-slots (interleaved lag) selected by past hits')
        for k in (1,2,3,4,6,8,12):
            tot,py=wf(tg,k)
            st,h,e=tot; r=h/st
            print(' k=%2d stake %6d hits %4d rate %.3f%% roi95 %+.2f  z %+.1f | last5y(22-26) roi %+.2f'%(k,st,h,r*100,95*r-1,(h-e)/np.sqrt(e),(lambda q:95*sum(a[2] for a in q)/sum(a[1] for a in q)-1)([a for a in py if a[0]>=2022])))
        tot,py=wf(tg,4)
        print('  k=4 slots per year:',[(a[0],a[3]) for a in py][::2])
