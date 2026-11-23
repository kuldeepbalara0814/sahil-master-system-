import sys,csv; sys.path.insert(0,'.')
from common import *
d,A,dsd,dsv=load_all(); y,_=year_month(d)
# source column check
src=np.array([r[5] for r in load(R+'/data/results.csv')])
print('source counts',{s:int((src==s).sum()) for s in set(src)})
for s in set(src):
    q=src==s
    print(s,'same-day ds==gb/fd/gl %.2f %.2f %.2f'%tuple(100*(A['ds'][q]==A[g][q]).mean() for g in ('gb','fd','gl')),'n',q.sum())
print('identical 4-game rows', int(((A['fd'][1:]==A['fd'][:-1])&(A['gb'][1:]==A['gb'][:-1])&(A['gl'][1:]==A['gl'][:-1])).sum()))
# DS 1966+ own-lag by decade
yd=np.array([int(s[:4]) for s in dsd]); x=dsv
print('DS own-lag match rate %% by decade (exp = leave-one-out within decade)')
dec=[(1966,1979),(1980,1989),(1990,1999),(2000,2009),(2010,2019),(2020,2026)]
for a,b in dec:
    q=(yd>=a)&(yd<=b); xx=x[q]; n=len(xx); c=np.bincount(xx,minlength=100); e=(c*(c-1)).sum()/(n*(n-1))
    cells=[]
    for L in (1,2,3,4,5,6,7,10):
        m=(xx[L:]==xx[:-L]).mean(); cells.append('L%d %.2f'%(L,100*m))
    # bets: {x-2,x-3}, {x-2..x-5}
    def roi(Ls):
        h=0;st=0
        for i in range(max(Ls),n):
            s=set(xx[i-L] for L in Ls); st+=len(s); h+=xx[i] in s
        return h/st,95*h/st-1,(h-st*e)/np.sqrt(st*e)
    r2=roi((2,3)); r4=roi((2,3,4,5))
    print('%d-%d n=%d exp %.2f | '%(a,b,n,100*e)+' '.join(cells)+' | {2,3}: rate %.2f roi %+.2f z %.1f | {2-5}: rate %.2f roi %+.2f z %.1f'%(100*r2[0],r2[1],r2[2],100*r4[0],r4[1],r4[2]))
