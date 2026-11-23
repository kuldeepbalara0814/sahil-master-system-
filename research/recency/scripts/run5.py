import sys; sys.path.insert(0,'.')
from common import *
d,A,dsd,dsv=load_all(); y,mon=year_month(d)
N=len(d); G=['fd','gb','gl','ds']
X=np.stack([A[g] for g in G],1).reshape(-1)      # time order
Y=np.repeat(y,4); gid=np.tile(np.arange(4),N)
# expected baseline per (tgt pos,src pos): sum_n f_year_tgt(n)*f_year_src(n)  (year freq per game)
fr={}
for gi,g in enumerate(G):
    for yy in np.unique(y):
        fr[(gi,yy)]=np.bincount(A[g][y==yy],minlength=100)/ (y==yy).sum()
def prof(sel_t, Ls, era=None):
    res=[]
    for L in Ls:
        p=np.arange(L,len(X)); p=p[sel_t[p]]
        if era is not None: p=p[(Y[p]>=era[0])&(Y[p]<=era[1])]
        m=(X[p]==X[p-L]).sum()
        e=sum(float((fr[(gid[q],Y[q])]*fr[(gid[q-L],Y[q-L])]).sum()) for q in p[::7])*7 if True else 0
        res.append((L,len(p),m,m/len(p),e/len(p)))
    return res
Ls=list(range(1,41))
out=open('../out/dist_profile.csv','w'); out.write('target,era,lag,n,matches,rate,exp\n')
for tn,tg in (('fd',0),('gb',1),('gl',2),('ds',3),('all',None)):
    sel=(gid==tg) if tg is not None else np.ones(len(X),bool)
    for en,era in (('2013-26',None),('2013-17',(2013,2017)),('2018-22',(2018,2022)),('2023-26',(2023,2026))):
        for L,n,m,r,e in prof(sel,Ls,era): out.write('%s,%s,%d,%d,%d,%.5f,%.5f\n'%(tn,en,L,n,m,r,e))
out.close()
