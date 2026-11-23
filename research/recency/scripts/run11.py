import sys; sys.path.insert(0,'.')
from common import *
d,A,dsd,dsv=load_all(); y,_=year_month(d); N=len(d)
ds=A['ds']
def sets(cols):
    C=np.stack(cols,1).copy()
    for j in range(1,C.shape[1]):
        for l in range(j): C[:,j]=np.where(C[:,j]==C[:,l],-1,C[:,j])
    return C
def rate(C,t,mask):
    v=C>=0; m=v.sum(1); h=((C==t[:,None])&v).any(1); q=mask&(m>0)&(np.arange(len(t))>=6)
    return m[q].sum(),h[q].sum(),m,h
own=sets([lag(ds,k) for k in (2,3,4,5)])
cross=sets([A['gb'],A['fd'],lag(A['gb'],1),lag(A['gl'],1)])
both=sets([lag(ds,k) for k in (2,3,4,5)]+[A['gb'],A['fd'],lag(A['gb'],1),lag(A['gl'],1)])
rng=np.random.default_rng(9)
for nm,C in (('own l2-5',own),('cross gb0 fd0 gb1 gl1',cross),('union 8',both)):
    print('==',nm)
    for Y in range(2013,2027):
        s,h,_,_=rate(C,ds,y==Y); print(' ',Y,'stake %d hits %d rate %.2f roi95 %+.2f'%(s,h,100*h/s,95*h/s-1),end=';')
    print()
    for a in (2013,2018,2022):
        s,h,_,_=rate(C,ds,y>=a); e=s/100; print(' %d+: stake %d hits %d rate %.3f%% roi95 %+.2f roi90 %+.2f z %.1f  days/yr %.0f'%(a,s,h,100*h/s,95*h/s-1,90*h/s-1,(h-e)/np.sqrt(e),s/ (C>=0).sum(1).mean()/(2027-a)))
    # within-year shuffle control (kills serial effect, keeps marginal) -- sources fixed for cross; own sources shuffled with the target
    rs=[]
    for _ in range(200):
        t=ds.copy()
        for yy in range(2013,2027):
            ii=np.where(y==yy)[0]; t[ii]=t[ii][rng.permutation(len(ii))]
        if nm.startswith('own'):
            C2=sets([lag(t,k) for k in (2,3,4,5)])
        else: C2=C
        s,h,_,_=rate(C2,t,y>=2013); rs.append(h/s)
    print('  within-year shuffle control rate: mean %.3f%% max %.3f%% (real %.3f%%)'%(100*np.mean(rs),100*np.max(rs),100*rate(C,ds,y>=2013)[1]/rate(C,ds,y>=2013)[0]))
