import sys,csv; sys.path.insert(0,'.')
from common import *
d,A,dsd,dsv=load_all(); x=dsv; n=len(x); yd=np.array([int(s[:4]) for s in dsd])
rng=np.random.default_rng(11)
def base_sets(x):
    C=np.stack([np.concatenate([np.full(L,-1),x[:-L]]) for L in (2,3,4,5)],1)
    for j in range(1,4):
        for l in range(j): C[:,j]=np.where(C[:,j]==C[:,l],-1,C[:,j])
    v=C>=0; m=v.sum(1); h=((C==x[:,None])&v).any(1); m[:6]=0
    return m,h
m,h=base_sets(x); mb=m[m>0].mean(); print('avg set size',round(mb,2))
print('### E source robustness (2013-26)')
r2=list(csv.reader(open('../out/ds_site2_2013_2026.csv')))[1:]
s2={a:int(b) for a,b in r2}; s1={dsd[i]:int(x[i]) for i in range(n) if yd[i]>=2013}
com=[k for k in s1 if k in s2]; dif=[k for k in com if s1[k]!=s2[k]]
print(' ours %d days, site2 %d days, common %d, value mismatches %d, ours-only %d, site2-only %d'%(len(s1),len(s2),len(com),len(dif),len(set(s1)-set(s2)),len(set(s2)-set(s1))))
print(' mismatch examples',[(k,s1[k],s2[k]) for k in dif[:8]])
dates2=sorted(s2); x2=np.array([s2[k] for k in dates2]); m2,h2=base_sets(x2); y2=np.array([int(k[:4]) for k in dates2])
for nm,(mm,hh,yy) in (('ours',(m,h,yd)),('site2',(m2,h2,y2))):
    for a in (2013,2018,2022):
        q=(yy>=a)&(mm>0); s=mm[q].sum(); k=hh[q].sum(); print(' %s %d+: stake %d hits %d rate %.3f%% roi95 %+.2f roi90 %+.2f z %.1f'%(nm,a,s,k,100*k/s,95*k/s-1,90*k/s-1,(k-s/100)/np.sqrt(s/100)))
# site2 own-history lags (1966-2012 file is site2 too)
print('### C sequential monitoring / power')
p1=0.0137; 
def qd(p): return 1-(1-p)**mb
for lab,p0 in (('break-even 95x',1/95),('break-even 90x',1/90),('random 1.00%',0.01)):
    q0,q1=qd(p0),qd(p1)
    # fixed-sample: one-sided binomial test alpha .05, power
    out=[]
    for N in (90,180,365,730,1095,1825):
        # critical hits via normal approx w/ continuity via simulation
        sim0=rng.binomial(N,q0,200000); crit=np.percentile(sim0,95)
        sim1=rng.binomial(N,q1,200000); out.append('N=%d pow %.2f'%(N,(sim1>crit).mean()))
    print(' H0 %s (q0 %.4f vs q1 %.4f): '%(lab,q0,q1),' | '.join(out))
    # days for 80% power
    for N in range(30,6000,10):
        sim0=rng.binomial(N,q0,40000); crit=np.percentile(sim0,95); sim1=rng.binomial(N,q1,40000)
        if (sim1>crit).mean()>=0.8: print('   -> days needed for 80%% power (alpha .05): ~%d (%.1f years)'%(N,N/350)); break
    # SPRT alpha=beta=.05
    A_=np.log(0.95/0.05); lw=np.log(q1/q0); ll=np.log((1-q1)/(1-q0))
    def sprt(q,reps=4000,cap=20000):
        T=[];dec=[]
        for _ in range(reps):
            s=0;t=0
            hit=rng.random(cap)<q
            inc=np.where(hit,lw,ll); cs=np.cumsum(inc); i=np.argmax((cs>=A_)|(cs<=-A_))
            if abs(cs[i])>=A_: T.append(i+1);dec.append(cs[i]>0)
            else: T.append(cap);dec.append(-1)
        T=np.array(T);dec=np.array(dec); return np.median(T),np.percentile(T,90),(dec==1).mean(),(dec==0).mean()
    a=sprt(q1); b=sprt(q0)
    print('   SPRT(a=b=.05): if true=1.37%%: median %d d, p90 %d d, accept-edge %.2f | if true=H0: median %d d, p90 %d d, wrong(accept edge) %.2f'%(a[0],a[1],a[2],b[0],b[1],b[2]))
# CUSUM for decline 1.37 -> 1.05%
print(' CUSUM decline detection (reference q1=1.37%% -> alt 1.05%% breakeven 95x):')
qa,qb=qd(0.0137),qd(1/95); lw=np.log(qb/qa); ll=np.log((1-qb)/(1-qa))
def cusum(q,hth,reps=2000,cap=8000):
    T=[]
    for _ in range(reps):
        hit=rng.random(cap)<q; inc=np.where(hit,lw,ll); c=0;t=cap
        for i,v in enumerate(inc):
            c=max(0,c+v)
            if c>=hth: t=i+1;break
        T.append(t)
    return np.array(T)
for hth in (2.0,3.0,4.0):
    T0=cusum(qa,hth,400,8000); T1=cusum(qb,hth,400,8000)
    print('  h=%.1f: false-alarm if still 1.37%%: median time %d d, P(alarm within 365d) %.2f | detect real decline: median %d d, p90 %d d'%(hth,np.median(T0),(T0<=365).mean(),np.median(T1),np.percentile(T1,90)))
print('### D staking / drawdown simulation (flat stake per number, 95x and 90x)')
def maxdd(c): return (np.maximum.accumulate(np.maximum(c,0))-c).max()
for pay in (95,90):
    for p in (0.0137,0.012,1/pay,0.0095):
        q=qd(p); R=2000;Dn=1000
        hit=rng.random((R,Dn))<q; net=np.where(hit,pay-mb,-mb); c=np.cumsum(net,1)
        dd=np.array([maxdd(r) for r in c])
        # longest no-hit run
        lr=[]
        for r in hit:
            idx=np.flatnonzero(r); gaps=np.diff(np.concatenate([[-1],idx,[Dn]]))-1; lr.append(gaps.max())
        print(' %dx true p=%.2f%%: 1000d end p5 %.0f med %.0f p95 %.0f | P(end<0) %.2f | maxDD med %.0f p95 %.0f p99 %.0f | longest no-hit run med %d p95 %d'%(pay,100*p,np.percentile(c[:,-1],5),np.median(c[:,-1]),np.percentile(c[:,-1],95),(c[:,-1]<0).mean(),np.median(dd),np.percentile(dd,95),np.percentile(dd,99),np.median(lr),np.percentile(lr,95)))
print(' -- bankroll sim: bank starts 1.0, daily total stake = F*bank (compounding) or F*initial (flat); 1000 days, 3000 paths; ruin = bank<0.25 at any time')
pay=95; rh=pay/mb-1
def kelly(q): b=rh; return max(0,(b*q-(1-q))/b)
pest=0.0125; Fk=kelly(qd(pest)); print('  full Kelly fraction (assuming p=%.2f%%): F*=%.4f of bank per day'%(100*pest,Fk))
strats=[('flat 0.5%/day of start',0.005,False),('flat 1%/day of start',0.01,False),('0.25 Kelly',0.25*Fk,True),('0.5 Kelly',0.5*Fk,True),('1.0 Kelly',Fk,True),('2x Kelly',2*Fk,True)]
for p in (0.0137,0.0125,0.0105,0.0095):
    q=qd(p); R=3000;Dn=1000; hit=rng.random((R,Dn))<q
    print('  TRUE p=%.2f%%'%(100*p))
    for nm,F,comp in strats:
        ret=np.where(hit,rh,-1.0)*F
        if comp:
            path=np.cumprod(1+ret,1)
        else:
            path=1+np.cumsum(ret,1)
        peak=np.maximum.accumulate(path,1); ddr=((peak-path)/peak).max(1)
        print('    %-22s median final %.2fx p5 %.2fx | P(final<1) %.2f | maxDD median %.0f%% p95 %.0f%% | ruin(<0.25) %.3f'%(nm,np.median(path[:,-1]),np.percentile(path[:,-1],5),(path[:,-1]<1).mean(),100*np.median(ddr),100*np.percentile(ddr,95),(path.min(1)<0.25).mean()))
