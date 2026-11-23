from common import *
GAMES=['fd','gb','gl','ds']
def build(A):
    """returns dict target-> dict rulename -> (C, ok) over 2013+ rows (N=4908)"""
    N=len(A['fd']); out={}
    for ti,T in enumerate(GAMES):
        S={}
        earlier=GAMES[:ti]
        for g in earlier: S[g+'0']=A[g]
        for k in range(1,6): S[T+'_l%d'%k]=lag(A[T],k)
        for g in GAMES:
            if g!=T: S[g+'_l1']=lag(A[g],1)
        R={}
        for n,v in S.items(): R['S:'+n]=make_sets([v])
        same=[A[g] for g in earlier]
        if same: R['U:same']=make_sets(same); R['Up:same(+palat)']=make_sets(same,True)
        R['U:own_l23']=make_sets([S[T+'_l2'],S[T+'_l3']]); R['Up:own_l23(+palat)']=make_sets([S[T+'_l2'],S[T+'_l3']],True)
        R['U:own_l2345']=make_sets([S[T+'_l%d'%k] for k in (2,3,4,5)])
        R['U:own_l12']=make_sets([S[T+'_l1'],S[T+'_l2']])
        if same: R['U:same+own_l2']=make_sets(same[:3]+[S[T+'_l2']] if len(same)<3 else same+[S[T+'_l2']])
        R['U:others_l1']=make_sets([S[g+'_l1'] for g in GAMES if g!=T])
        pool1=same+[S[T+'_l%d'%k] for k in range(1,6)]
        pool2=pool1+[S[g+'_l1'] for g in GAMES if g!=T]
        for nm,pool in (('A2:same+own5',pool1),('A2:same+own5+oth1',pool2)):
            P=np.stack(pool,1); C=agree_sets(P,2); R[nm]=(C,(P>=0).all(1)|True)
            Cp=np.concatenate([C,np.where(C>=0,palat(np.where(C<0,0,C)),-1)],1)
            # dedupe palat
            for j in range(C.shape[1],Cp.shape[1]):
                for l in range(j): Cp[:,j]=np.where(Cp[:,j]==Cp[:,l],-1,Cp[:,j])
            R['Ap'+nm[1:]+'(+palat)']=(Cp,True)
        out[T]=(R,S)
    return out
