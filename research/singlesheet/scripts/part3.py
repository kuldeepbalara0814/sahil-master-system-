"""Part 3: month-to-month 'shape copy'. Target month M, known rows 0..T-1; candidate = any earlier month E (b'<=b-3) with
score = #equal links (same (i,j) positions linked inside E and inside M, rows<T). Prediction for row T of M:
labels of M rows i<T for which E has a link (i,T). Hit if lab[M,T] in predicted set. Exact expectation = prob mass of the set.
modes: top1 / top3 / all(score>=S) / rand1 (random candidate, control for ranking).
usage: part3.py GAME NSHUF -> out/p3_<GAME>.npz
"""
import sys, time
import numpy as np
from common import *

TS = (8, 12, 16, 20); SS_ = (1, 2, 3); MODES = ("top1", "top3", "all", "rand1")
CFGS = [(lk, T, S, m) for lk in ("palat", "rashi") for T in TS for S in SS_ for m in MODES]
NY = 2026 - Y0 + 1
W = 31

def run_once(nums, year, blocks, rng):
    N = len(nums); yi = year - Y0
    nb = blocks.max() + 1
    bstart = np.searchsorted(blocks, np.arange(nb)); bend = np.append(bstart[1:], N) - 1
    S = np.zeros((len(CFGS), NY, 4))
    cnt = bend - bstart + 1
    iu, ju = np.triu_indices(W, 1)
    for lk in ("palat", "rashi"):
        lab, prob, size = arrays(nums, lk)
        LM = np.full((nb, W), -1, dtype=np.int64)
        for b in range(nb):
            n = min(cnt[b], W); LM[b, :n] = lab[bstart[b]:bstart[b] + n]
        val = LM >= 0
        Link = (LM[:, :, None] == LM[:, None, :]) & val[:, :, None] & val[:, None, :]      # nb,W,W
        F = Link[:, iu, ju].astype(np.float32)
        for T in TS:
            msk = ju < T
            Fm = F[:, msk]
            sc = Fm @ Fm.T                                                             # nb x nb
            for b in range(3, nb):
                if cnt[b] <= T: continue
                cand = np.arange(0, b - 2)
                cand = cand[val[cand, T]]
                if len(cand) == 0: continue
                s = sc[b, cand]
                t = bstart[b] + T; y = yi[t]; actual = LM[b, T]
                for Smin in SS_:
                    okc = cand[s >= Smin]; oks = s[s >= Smin]
                    order = np.lexsort((okc, oks))[::-1]                              # score desc, recency desc
                    okc = okc[order]
                    for mode in MODES:
                        if mode == "top1": sel = okc[:1]
                        elif mode == "top3": sel = okc[:3]
                        elif mode == "all": sel = okc
                        else: sel = cand[rng.integers(len(cand)):][:1] if False else cand[[rng.integers(len(cand))]]
                        if mode != "rand1" and len(sel) == 0: continue
                        labs = set()
                        for e in sel:
                            ii = np.nonzero(Link[e, :T, T])[0]
                            labs.update(LM[b, ii].tolist())
                        if not labs: continue
                        ex = float(sum(prob[l] for l in labs)); hit = actual in labs
                        ci = CFGS.index((lk, T, Smin, mode))
                        S[ci, y, 0] += 1; S[ci, y, 1] += hit; S[ci, y, 2] += ex; S[ci, y, 3] += sum(size[l] for l in labs)
    return S

if __name__ == "__main__":
    game, nshuf = sys.argv[1], int(sys.argv[2])
    nums, year, ym = load(game); blocks = blocks_month(ym)
    rng = np.random.default_rng(4242); out = []; t0 = time.time()
    for r in range(nshuf + 1):
        x = nums if r == 0 else shuffle_year(nums, year, rng)
        out.append(run_once(x, year, blocks, rng).astype(np.float32))
        if r % 5 == 0: print(game, r, round(time.time() - t0, 1), flush=True)
    np.savez_compressed(os.path.join(OUT, f"p3_{game}.npz"), S=np.array(out), cfgs=np.array([str(c) for c in CFGS]), years=np.arange(Y0, 2027))
