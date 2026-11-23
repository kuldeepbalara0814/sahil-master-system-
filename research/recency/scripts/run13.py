import sys,datetime; sys.path.insert(0,'.')
from common import *
d,A,dsd,dsv=load_all(); x=dsv; n=len(x); yd=np.array([int(s[:4]) for s in dsd])
LM=20
S=np.full((n,LM),-1)
for L in range(1,LM+1): S[L:,L-1]=x[:-L]
ok=np.arange(n)>=LM
tr=(yd<=2012)&ok; te=(yd>=2013)&ok
def dedupe(C):
    C=C.copy()
    for j in range(1,C.shape[1]):
        for l in range(j): C[:,j]=np.where(C[:,j]==C[:,l],-1,C[:,j])
    return C
def ev(C,mask):
    v=C>=0; m=v.sum(1); h=((C==x[:,None])&v).any(1)
    s=m[mask].sum(); k=h[mask].sum(); return s,k
def row(name,C):
    out=[name]
    for mk in (tr,te):
        s,k=ev(C,mk); out+=[s/mk.sum(),100*k/s,95*k/s-1,90*k/s-1,(k-s/100)/np.sqrt(s/100)]
    return out
def pr(r):
    print('%-26s size %.1f | train %.2f%% roi95 %+.2f z%.1f | TEST 13-26 %.2f%% roi95 %+.2f roi90 %+.2f z%.1f'%(r[0],r[1],r[2],r[3],r[5],r[7],r[8],r[9],r[10]))
res=[]
print('### A1 contiguous lag ranges (all pre-declared), exact numbers')
for a in (2,3,4):
    for b in range(a,10):
        if b-a+1>6: continue
        C=dedupe(S[:,a-1:b]); r=row('lags %d-%d'%(a,b),C); pr(r); res.append(r)
print('### A2 palat variants'); 
for a,b in ((2,3),(2,5),(2,6)):
    C0=S[:,a-1:b]; C=dedupe(np.concatenate([C0,np.where(C0>=0,palat(np.where(C0<0,0,C0)),-1)],1)); pr(row('lags %d-%d +palat'%(a,b),C))
print('### A3 top-k lags chosen on 1966-2012 train hits (lags 1-20)')
lh=np.array([(S[tr][:,L]==x[tr]).sum() for L in range(LM)]); print(' train lag rates%%:',' '.join('%d:%.2f'%(L+1,100*lh[L]/tr.sum()) for L in range(LM)))
order=np.argsort(-lh)
for k in range(1,9):
    C=dedupe(S[:,order[:k]]); pr(row('top-%d lags %s'%(k,sorted(order[:k]+1)),C))
print('### A4 rolling-origin yearly walk-forward 2013-26 (past = 1966..Y-1)')
def roll(choose,name):
    tot=np.zeros(2); per=[]
    for Y in range(2013,2027):
        past=(yd<Y)&ok; cur=(yd==Y)&ok
        C=choose(past); s,k=ev(C,cur); tot+=[s,k]; per.append((Y,100*k/max(s,1)))
    print('%-34s test stake %d hits %d rate %.3f%% roi95 %+.2f roi90 %+.2f z %.1f'%(name,tot[0],tot[1],100*tot[1]/tot[0],95*tot[1]/tot[0]-1,90*tot[1]/tot[0]-1,(tot[1]-tot[0]/100)/np.sqrt(tot[0]/100)))
for k in (2,3,4,5,6):
    def ch(past,k=k):
        h=np.array([(S[past][:,L]==x[past]).sum() for L in range(LM)]); return dedupe(S[:,np.argsort(-h)[:k]])
    roll(ch,'rolling top-%d lags'%k)
# pool model
def pool_choose(past,k,W=12,minw=0.0):
    rate=np.array([(S[past][:,L]==x[past]).mean() for L in range(W)]); w=rate/0.01-1
    sc=np.zeros((n,W))
    for j in range(W):
        for L in range(W): sc[:,j]+=w[L]*(S[:,L]==S[:,j])
    first=np.ones((n,W),bool)
    for j in range(1,W):
        for l in range(j): first[:,j]&=S[:,l]!=S[:,j]
    sc=np.where(first&(S[:,:W]>=0),sc,-9)
    idx=np.argsort(-sc,1,kind='stable')[:,:k]; Cs=np.take_along_axis(S[:,:W],idx,1); scs=np.take_along_axis(sc,idx,1)
    return np.where(scs>minw,Cs,-1),w
print('### A5 recycling-pool model (weights from past lag profile, lags 1-12, top-k by score)')
for k in (2,3,4,5,6):
    C,w=pool_choose(tr,k); pr(row('pool top-%d (train w)'%k,C))
print('  weights (train):',np.round(w,2))
for k in (3,4,5):
    roll(lambda past,k=k:pool_choose(past,k)[0],'rolling pool top-%d'%k)
print('### B bias interaction & avoid rules on base lags 2-5 (train/test + removed/added bets rate)')
fr=np.bincount(x[yd<=2012],minlength=100)/ (yd<=2012).sum()
print(' train freq top5',[(int(i),round(100*fr[i],2)) for i in np.argsort(-fr)[:5]],'bottom5',[(int(i),round(100*fr[i],2)) for i in np.argsort(fr)[:5]])
dbl=np.array([i%11==0 for i in range(100)]); print(' doubles freq train %.3f%% test %.3f%% (1%% expected)'%(100*fr[dbl].mean(),100*(np.bincount(x[yd>=2013],minlength=100)/(yd>=2013).sum())[dbl].mean()))
low10=np.argsort(fr)[:10]; top=np.argsort(-fr)
base=dedupe(S[:,1:5])
def removed_stats(newC,name,baseC=base):
    r=row(name,newC); pr(r)
    rem=np.where((baseC>=0)&~(baseC[:,:,None]==newC[:,None,:]).any(2),baseC,-1)  # removed bets
    for mk,lab in ((tr,'train'),(te,'test')):
        s,k=ev(rem,mk)
        if s>0: print('      removed bets %s: stake %d rate %.2f%%'%(lab,s,100*k/s))
    add=np.where((newC>=0)&~(newC[:,:,None]==baseC[:,None,:]).any(2),newC,-1)
    for mk,lab in ((tr,'train'),(te,'test')):
        s,k=ev(add,mk)
        if s>0: print('      added bets %s: stake %d rate %.2f%%'%(lab,s,100*k/s))
pr(row('base lags 2-5',base))
removed_stats(np.where(base==S[:,[0]],-1,base),'drop if == lag1')
for W in (8,12):
    cnt=np.stack([(S[:,:W]==base[:,[j]]).sum(1) for j in range(4)],1)
    removed_stats(np.where(cnt>=2,-1,base),'drop if seen>=2 in last %d'%W)
removed_stats(np.where(np.isin(base,np.where(dbl)[0]),-1,base),'drop doubles')
removed_stats(np.where(np.isin(base,low10),-1,base),'drop 10 least freq (train)')
removed_stats(np.where(base==5,-1,base),'drop 05')
for k in (1,3):
    extra=np.tile(top[:k],(n,1)); removed_stats(dedupe(np.concatenate([base,extra],1)),'add top-%d freq (%s)'%(k,list(top[:k])))
print(' standalone rate of top-1 number (41) train %.2f%% test %.2f%%'%(100*(x[tr]==top[0]).mean(),100*(x[te]==top[0]).mean()))
# the "bias candidates": hit rate of candidate by category
for lab,cat in (('double',dbl),('low10',np.isin(np.arange(100),low10)),('top10',np.isin(np.arange(100),top[:10]))):
    for mk,ln in ((tr,'train'),(te,'test')):
        v=(base>=0)&cat[np.where(base<0,0,base)]; hit=(base==x[:,None])&v
        print('   candidates in cat %-6s %s: bets %d rate %.2f%%'%(lab,ln,v[mk].sum(),100*hit[mk].sum()/max(v[mk].sum(),1)))
print('### F weekday/dom/month (base lags 2-5): choose on train 1966-2012 with permutation max, test 2013-26')
v=base>=0; m=v.sum(1); h=((base==x[:,None])&v).any(1)
dow=np.array([datetime.date(int(s[:4]),int(s[5:7]),int(s[8:10])).weekday() for s in dsd]); dom=np.array([int(s[8:10]) for s in dsd]); mo=np.array([int(s[5:7]) for s in dsd])
conds={}
for k in range(7): conds['dow=%d'%k]=dow==k
for a,b in ((1,7),(8,14),(15,21),(22,31)): conds['dom%d-%d'%(a,b)]=(dom>=a)&(dom<=b)
for k in range(1,13): conds['mon=%d'%k]=mo==k
conds['lag1 hit(prev day hit)']=np.concatenate([[False],h[:-1]])
names=list(conds)
def zs(hh,mask):
    out=[]
    for nm in names:
        c=conds[nm]&mask; r=~conds[nm]&mask; s1=m[c].sum(); s0=m[r].sum(); p=hh[mask].sum()/m[mask].sum()
        out.append((hh[c].sum()/s1-hh[r].sum()/s0)/np.sqrt(p*(1-p)*(1/s1+1/s0)))
    return np.array(out)
z0=zs(h.astype(float),tr); rng=np.random.default_rng(4); idx=np.where(tr)[0]; mx=[]
for _ in range(500):
    hh=h.astype(float).copy(); hh[idx]=hh[rng.permutation(idx)]; mx.append(np.abs(zs(hh,tr)).max())
mx=np.array(mx); zt=zs(h.astype(float),te); print(' tests %d, null p95 max|z| %.2f'%(len(names),np.percentile(mx,95)))
for i in np.argsort(-np.abs(z0))[:5]: print('  %-14s train z %+.2f p_adj %.2f | test z %+.2f'%(names[i],z0[i],(mx>=abs(z0[i])).mean(),zt[i]))
print(' test max|z| over all conds: %.2f'%np.abs(zt).max())
