import numpy as np
z=np.load('../out/stats_real.npz'); St,Hi,keys=z['St'],z['Hi'],list(z['keys'])
GAMES=['fd','gb','gl','ds']
for crit in ('roi','z'):
    print('==',crit); tot=[0,0]
    for yr in range(5,14):
        ps=St[:,:yr].sum(1); ph=Hi[:,:yr].sum(1)
        sc=np.where(ps>=500,95*ph/np.maximum(ps,1)-1,-9) if crit=='roi' else np.where(ps>=500,(ph-ps/100)/np.sqrt(np.maximum(ps/100,1e-9)),-9)
        line=[];ys=yh=0
        for T in GAMES:
            idx=[k for k,kk in enumerate(keys) if kk.startswith(T+'|')]
            b=idx[int(np.argmax(sc[idx]))]
            if sc[b]>(0 if crit=='roi' else 2):
                line.append('%s:%s(%.2f)->%d/%d'%(T,keys[b].split('|')[1],sc[b],Hi[b,yr],St[b,yr])); ys+=St[b,yr]; yh+=Hi[b,yr]
        tot[0]+=ys;tot[1]+=yh
        print(2013+yr,'stake %d hits %d roi %+.2f'%(ys,yh,95*yh/max(ys,1)-1),' '.join(line))
    print('total',tot,95*tot[1]/tot[0]-1)
