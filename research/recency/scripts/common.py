import numpy as np, csv, os
R=os.path.dirname(os.path.abspath(__file__))+'/../../..'
def load(path):
    rows=list(csv.reader(open(path)))[1:]
    return rows
def load_all():
    r=load(R+'/data/results.csv')
    dates=np.array([x[0] for x in r])
    A={k:np.array([int(x[i]) for x in r]) for k,i in (('fd',1),('gb',2),('gl',3),('ds',4))}
    d=load(R+'/data/game_ds.csv')
    dsd=np.array([x[0] for x in d]); dsv=np.array([int(x[1]) for x in d])
    return dates,A,dsd,dsv
def palat(n):
    n=np.asarray(n); return (n%10)*10+n//10
def year_month(dates):
    y=np.array([int(d[:4]) for d in dates]); m=np.array([int(d[:4])*12+int(d[5:7]) for d in dates])
    return y,m
def lag(x,k):
    o=np.full(len(x),-1); o[k:]=x[:-k] if k>0 else x; return o
def freq_year(t,y):
    """per-day baseline freq matrix: F[i,n]=freq of n in year of day i (target, in-year)"""
    ys=np.unique(y); F=np.zeros((len(t),100))
    for yy in ys:
        idx=np.where(y==yy)[0]; c=np.bincount(t[idx],minlength=100)/len(idx); F[idx]=c
    return F
def make_sets(cols, with_palat=False):
    """cols: list of arrays (-1 invalid). returns C (N,K) deduped padded -1 ; day valid only if all cols valid"""
    C=np.stack(cols,1).copy()
    ok=(C>=0).all(1)
    if with_palat: C=np.concatenate([C,palat(np.where(C<0,0,C))],1); C[~ok]=-1
    K=C.shape[1]
    for j in range(1,K):
        for l in range(j):
            C[:,j]=np.where(C[:,j]==C[:,l],-1,C[:,j])
    return C,ok
def agree_sets(P,minc=2,maxk=4):
    """P (N,k) source numbers (-1 invalid). set = distinct numbers appearing >=minc times among valid sources."""
    N,k=P.shape; C=np.full((N,k),-1)
    for j in range(k):
        cnt=((P==P[:,[j]])&(P[:,[j]]>=0)).sum(1)
        first=np.ones(N,bool)
        for l in range(j): first&=P[:,l]!=P[:,j]
        C[:,j]=np.where((cnt>=minc)&first,P[:,j],-1)
    return C
def evaluate(C,t,F,mask=None):
    """returns per-day arrays: fire, m, hit, p0(freq-adjusted expectation)"""
    valid=C>=0; m=valid.sum(1); fire=m>0
    if mask is not None: fire&=mask
    hit=((C==t[:,None])&valid).any(1)
    Cc=np.where(valid,C,0)
    p0=(F[np.arange(len(t))[:,None],Cc]*valid).sum(1)
    return fire,m,hit,p0
def summarize(fire,m,hit,p0,sel=None):
    f=fire if sel is None else fire&sel
    n=f.sum()
    if n==0: return dict(days=0,stake=0,hits=0,rate_per_no=np.nan,exp_unif=np.nan,exp_adj=np.nan,lift=np.nan,roi95=np.nan,roi90=np.nan,z=np.nan)
    stake=m[f].sum(); h=hit[f].sum(); e=p0[f].sum(); eu=stake/100
    var=(p0[f]*(1-p0[f])).sum()
    return dict(days=int(n),stake=int(stake),hits=int(h),rate_per_no=h/stake,exp_unif=eu/stake,exp_adj=e/stake,lift=h/e if e>0 else np.nan,
                roi95=95*h/stake-1,roi90=90*h/stake-1,z=(h-e)/np.sqrt(var) if var>0 else np.nan)
def month_boot(fire,m,hit,p0,mon,sel=None,B=1000,seed=1):
    f=fire if sel is None else fire&sel
    um,inv=np.unique(mon,return_inverse=True)
    S=np.bincount(inv,weights=np.where(f,m,0),minlength=len(um)); H=np.bincount(inv,weights=np.where(f,hit,0),minlength=len(um))
    E=np.bincount(inv,weights=np.where(f,p0,0),minlength=len(um))
    rng=np.random.default_rng(seed); n=len(um); out=[]
    ix=rng.integers(0,n,(B,n))
    s=S[ix].sum(1); h=H[ix].sum(1); e=E[ix].sum(1)
    ok=s>0
    roi=95*h[ok]/s[ok]-1; lift=h[ok]/np.maximum(e[ok],1e-9)
    return np.percentile(roi,[2.5,97.5]),np.percentile(lift,[2.5,97.5])
