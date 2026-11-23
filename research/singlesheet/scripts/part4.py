"""Part 4: crossing (X) / nested / sequential two-link shapes inside a boundary of L rows (single column, month blocks).
Freq: windows (in-block) containing >=1 pair of links of the type (cells all distinct) + mean count per window.
Predict: pair-config present in a step-1 window and a step-2 window; in step 3 (start s3 in current month), when link a (ends first)
is complete -> predict last cell of link b equals first cell of link b. 'cond' = only after link a completed; 'unc' = whenever both first cells known.
usage: part4.py GAME NSHUF -> out/p4_<GAME>.npz  FQ[run,fcfg,year,3], S[run,pcfg,year,4]
"""
import sys, time
import numpy as np
from common import *

LS = (8, 10, 12, 15); TYPES = ("cross", "nested", "seq"); LINKS = ("palat", "rashi")
FCFGS = [(tp, L, lk) for tp in TYPES for L in LS for lk in LINKS]
PCFGS = [(tp, L, lk, md) for tp in TYPES for L in LS for lk in LINKS for md in ("cond", "unc")]
NY = 2026 - Y0 + 1

def configs(L):
    I, J = pairs(L); P = len(I); out = []
    for p in range(P):
        for q in range(P):
            if J[p] >= J[q]: continue            # p = link a (ends first)
            ia, ja, ib, jb = I[p], J[p], I[q], J[q]
            if ia == ib or ib == ja: continue
            tp = "seq" if ja < ib else ("cross" if ia < ib else "nested")
            out.append((p, q, tp, ia, ja, ib, jb))
    return out

CF = {L: configs(L) for L in LS}

def run_once(nums, year, blocks):
    N = len(nums); yi = year - Y0
    nb = blocks.max() + 1
    bstart = np.searchsorted(blocks, np.arange(nb)); bend = np.append(bstart[1:], N) - 1
    FQ = np.zeros((len(FCFGS), NY, 3)); S = np.zeros((len(PCFGS), NY, 4))
    for lk in LINKS:
        lab, prob, size = arrays(nums, lk)
        for L in LS:
            I, J = pairs(L); P = len(I)
            cf = CF[L]; pa = np.array([c[0] for c in cf]); pb = np.array([c[1] for c in cf])
            tps = np.array([TYPES.index(c[2]) for c in cf])
            ia = np.array([c[3] for c in cf]); ja = np.array([c[4] for c in cf]); ib = np.array([c[5] for c in cf]); jb = np.array([c[6] for c in cf])
            starts = np.arange(0, N - L + 1)
            A = (lab[starts[:, None] + I[None, :]] == lab[starts[:, None] + J[None, :]]) & (blocks[starts] == blocks[starts + L - 1])[:, None]
            A = np.vstack([A, np.zeros((L - 1, P), bool)])
            # --- frequency
            wy = yi
            ar = np.arange(N); wv = (ar + L - 1 < N) & (blocks == blocks[np.minimum(ar + L - 1, N - 1)])
            for ch in range(0, N, 3000):
                Ac = A[ch:ch + 3000]; yy = wy[ch:ch + 3000]
                X = (Ac[:, pa] & Ac[:, pb])
                for k, tp in enumerate(TYPES):
                    cnt = X[:, tps == k].sum(1)
                    fi = FCFGS.index((tp, L, lk))
                    np.add.at(FQ[fi, :, 0], yy[wv[ch:ch + 3000]], 1)
                    np.add.at(FQ[fi, :, 1], yy, cnt > 0)
                    np.add.at(FQ[fi, :, 2], yy, cnt)
            # --- prediction
            Af = A.astype(np.float32)
            for b3 in range(2, nb):
                b1, b2 = b3 - 2, b3 - 1
                A1 = A[bstart[b1]:bend[b1] + 1]; A2 = A[bstart[b2]:bend[b2] + 1]
                A1 = A1[A1.any(1)]; A2 = A2[A2.any(1)]
                if len(A1) == 0 or len(A2) == 0: continue
                # pair-config present in step1 window and step2 window
                s1 = (A1[:, pa] & A1[:, pb]).any(0); s2 = (A2[:, pa] & A2[:, pb]).any(0)
                sup = np.nonzero(s1 & s2)[0]
                if len(sup) == 0: continue
                S3 = np.arange(bstart[b3], bend[b3] + 1); S3 = S3[S3 + L - 1 < N]
                if len(S3) == 0: continue
                for c in sup:
                    ta = S3 + ia[c]; ua = S3 + ja[c]; tb = S3 + ib[c]; ub = S3 + jb[c]
                    tp = TYPES[tps[c]]
                    # unconditional: both first cells known in month, and ua known (so timing equal)
                    known = (ua <= bend[b3]) & (tb <= bend[b3])
                    if not known.any(): continue
                    cond = known & (lab[np.minimum(ua, N - 1)] == lab[np.minimum(ta, N - 1)])
                    for md, m in (("unc", known), ("cond", cond)):
                        if not m.any(): continue
                        lt = lab[tb[m]]; hit = lab[ub[m]] == lt; ex = prob[lt]; yy = yi[tb[m]]
                        ci = PCFGS.index((tp, L, lk, md))
                        np.add.at(S[ci, :, 0], yy, 1); np.add.at(S[ci, :, 1], yy, hit)
                        np.add.at(S[ci, :, 2], yy, ex); np.add.at(S[ci, :, 3], yy, size[lt])
    return FQ, S

if __name__ == "__main__":
    game, nshuf = sys.argv[1], int(sys.argv[2])
    nums, year, ym = load(game); blocks = blocks_month(ym)
    rng = np.random.default_rng(99); F_, S_ = [], []; t0 = time.time()
    for r in range(nshuf + 1):
        x = nums if r == 0 else shuffle_year(nums, year, rng)
        f, s = run_once(x, year, blocks); F_.append(f.astype(np.float32)); S_.append(s.astype(np.float32))
        if r % 5 == 0: print(game, r, round(time.time() - t0, 1), flush=True)
    np.savez_compressed(os.path.join(OUT, f"p4_{game}.npz"), FQ=np.array(F_), S=np.array(S_), fcfgs=np.array([str(c) for c in FCFGS]), pcfgs=np.array([str(c) for c in PCFGS]), years=np.arange(Y0, 2027))
