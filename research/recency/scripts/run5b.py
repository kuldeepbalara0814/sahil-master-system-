import sys; sys.path.insert(0,'.')
from common import *
d,A,dsd,dsv=load_all(); y,mon=year_month(d); N=len(d); G=['fd','gb','gl','ds']
# one-pass matrix: target game t, source game s, line lag l (s later than t within same line not allowed: only earlier in time)
def pair(t,s,l,a,b):
    # target row i, source row i-l ; require time(src)<time(tgt): l>0 or order[s]<order[t]
    i=np.arange(l,N); sel=(y[i]>=a)&(y[i]<=b); i=i[sel]
    xt=A[G[t]][i]; xs=A[G[s]][i-l]
    m=(xt==xs).sum(); n=len(i)
    # expectation: within-year-shuffle-style
    if t==s:
        e=0.0
        for yy in np.unique(y[i]):
            ii=i[y[i]==yy]; c=np.bincount(A[G[t]][ii],minlength=100); k=len(ii); e+=(c*(c-1)).sum()/(k-1)  # sum_n c(c-1)/(k-1) = k*P
    else:
        e=0.0
        for yy in np.unique(y[i]):
            ii=i[y[i]==yy]; ft=np.bincount(A[G[t]][ii],minlength=100)/len(ii); fs=np.bincount(A[G[s]][ii-l],minlength=100)/len(ii); e+=len(ii)*float((ft*fs).sum())
    return n,m,e
out={}
for era,(a,b) in (('13-26',(2013,2026)),('18-26',(2018,2026))):
    for t in range(4):
        row=[]
        for l in range(0,7):
            for s in range(4):
                if l==0 and s>=t: continue
                n,m,e=pair(t,s,l,a,b); row.append((G[s],l,n,m,e))
        out[(era,t)]=row
import json
lines=[]
for (era,t),row in out.items():
    lines.append('== target %s era %s : cell = rate%% (lift, z) by source game@linelag'%(G[t],era))
    for l in range(0,7):
        cells=[]
        for s,ll,n,m,e in row:
            if ll!=l: continue
            z=(m-e)/np.sqrt(e*(1-e/n)) if e>0 else 0
            cells.append('%s%d %.2f(%.2f,%+.1f)'%(s,l,100*m/n,m/e,z))
        lines.append('  '+'  '.join(cells))
open('../out/pair_matrix.txt','w').write('\n'.join(lines)); print('\n'.join(lines))
