"""Part 2: same-gap links. P then Q after g rows, twice in same month (4 distinct cells r1<r1+g<r2<r2+g);
then P again at r3 (> r2+g; same month, or up to end of next month) -> Q expected at r3+g.
usage: part2.py GAME NSHUF ; out/p2_<GAME>.npz  S[run,cfg,year,4]
"""
import sys, time
import numpy as np
from common import *

GBANDS = {"g1-10": range(1, 11), "g1-3": range(1, 4), "g4-6": range(4, 7), "g7-10": range(7, 11)}
CFGS = [(lk, sc, ms, gb) for lk in ("palat", "rashi") for sc in ("same", "next") for ms in (1, 2) for gb in GBANDS]
NY = 2026 - Y0 + 1

def run_once(nums, year, blocks):
    N = len(nums); yi = year - Y0
    nb = blocks.max() + 1
    bstart = np.searchsorted(blocks, np.arange(nb)); bend = np.append(bstart[1:], N) - 1
    S = np.zeros((len(CFGS), NY, 4))
    for lk in ("palat", "rashi"):
        lab, prob, size = arrays(nums, lk)
        for sc in ("same", "next"):
            preds = {}                                   # (r3,g,Q) -> support
            for b in range(nb):
                rs, re = bstart[b], bend[b]
                lim = re if sc == "same" else bend[min(b + 1, nb - 1)]
                rows = np.arange(rs, re + 1)
                for g in range(1, 11):
                    r1s = rows[rows + g <= re]
                    if len(r1s) < 2: continue
                    P = lab[r1s]; Qv = lab[r1s + g]
                    M = (P[:, None] == P[None, :]) & (Qv[:, None] == Qv[None, :])
                    # r2 > r1 + g
                    M &= r1s[None, :] > (r1s[:, None] + g)
                    a, c = np.nonzero(M)
                    for x, y in zip(a, c):
                        r2 = r1s[y]; p = P[x]; q = Qv[x]
                        lo = r2 + g + 1
                        if lo > lim: continue
                        cand = np.arange(lo, lim + 1)
                        cand = cand[(lab[cand] == p) & (cand + g < N)]
                        for r3 in cand:
                            k = (int(r3), g, int(q))
                            preds[k] = preds.get(k, 0) + 1
            if not preds: continue
            keys = np.array(list(preds.keys())); sup = np.array(list(preds.values()))
            r3, g, q = keys[:, 0], keys[:, 1], keys[:, 2]
            hit = lab[r3 + g] == q; ex = prob[q]; sz = size[q]; yy = yi[r3]
            for ci, (lk2, sc2, ms, gb) in enumerate(CFGS):
                if lk2 != lk or sc2 != sc: continue
                m = (sup >= ms) & np.isin(g, list(GBANDS[gb]))
                np.add.at(S[ci, :, 0], yy[m], 1); np.add.at(S[ci, :, 1], yy[m], hit[m])
                np.add.at(S[ci, :, 2], yy[m], ex[m]); np.add.at(S[ci, :, 3], yy[m], sz[m])
    return S

if __name__ == "__main__":
    game, nshuf = sys.argv[1], int(sys.argv[2])
    nums, year, ym = load(game); blocks = blocks_month(ym)
    rng = np.random.default_rng(777); SS = []; t0 = time.time()
    for r in range(nshuf + 1):
        x = nums if r == 0 else shuffle_year(nums, year, rng)
        SS.append(run_once(x, year, blocks).astype(np.float32))
        if r % 10 == 0: print(game, r, round(time.time() - t0, 1), flush=True)
    np.savez_compressed(os.path.join(OUT, f"p2_{game}.npz"), S=np.array(SS), cfgs=np.array([str(c) for c in CFGS]), years=np.arange(Y0, 2027))
