"""Part 1: single-column Step1/Step2/Step3 walk-forward test.
usage: part1.py GAME SCHEME(month|block30) NSHUF
Output: out/p1_<GAME>_<SCHEME>.npz  (stat arrays [run, cfg, year, 4] + cfg list; run 0 = real, 1.. = shuffles)
Per config accumulators per year: n_pred, hits, expected, set-size-sum.  Plus design existence: n_triples, n_with_design.
"""
import sys, time
import numpy as np
from common import *

LS = (6, 8, 10, 12, 15)
KS = (2, 3, 4)
HITS = ("any", "exact", "near")
LINKS = ("palat", "rashi")
CFGS = [(L, lk, K, h) for L in LS for lk in LINKS for K in KS for h in HITS]
CFG_IDX = {c: i for i, c in enumerate(CFGS)}
DCFGS = [(L, lk, K) for L in LS for lk in LINKS for K in KS]
NY = 2026 - Y0 + 1

def run_once(nums, year, blocks):
    N = len(nums); yi = year - Y0
    nb = blocks.max() + 1
    bstart = np.searchsorted(blocks, np.arange(nb)); bend = np.append(bstart[1:], N) - 1
    S = np.zeros((len(CFGS), NY, 4)); D = np.zeros((len(DCFGS), NY, 2))
    for lk in LINKS:
        lab, prob, size = arrays(nums, lk)
        nxt = nxt_dist(lab)
        for L in LS:
            I, J = pairs(L); P = len(I)
            starts = np.arange(0, N - L + 1)
            A = (lab[starts[:, None] + I[None, :]] == lab[starts[:, None] + J[None, :]])
            ok = blocks[starts] == blocks[starts + L - 1]
            A = A & ok[:, None]
            A = np.vstack([A, np.zeros((L - 1, P), bool)]).astype(np.float32)   # pad -> index by start row
            E1 = np.zeros((P, L), np.float32); E1[np.arange(P), I] = 1
            for b3 in range(2, nb):
                b1, b2 = b3 - 2, b3 - 1
                r1 = np.arange(bstart[b1], bend[b1] + 1); r2 = np.arange(bstart[b2], bend[b2] + 1)
                A1 = A[r1]; A2 = A[r2]
                A1 = A1[A1.any(1)]; A2 = A2[A2.any(1)]
                yb = yi[bstart[b3]]
                if len(A1) == 0 or len(A2) == 0:
                    for K in KS:
                        D[DCFGS.index((L, lk, K)), yb, 1] += 1
                    continue
                cnt = A1 @ A2.T
                S3 = np.arange(bstart[b3], bend[b3] + 1); S3 = S3[S3 + L - 1 < N]
                if len(S3) == 0: continue
                t = S3[:, None] + I[None, :]; u = S3[:, None] + J[None, :]
                tin = t <= bend[b3]
                for K in KS:
                    Q = (cnt >= K).astype(np.float32)
                    di = DCFGS.index((L, lk, K))
                    D[di, yb, 1] += 1
                    if not Q.any(): continue
                    D[di, yb, 0] += 1
                    sup = ((Q @ A2) * A1).sum(0) > 0                     # link supported by some design
                    valid = sup[None, :] & tin
                    if not valid.any(): continue
                    # --- exact
                    tt = t[valid]; uu = u[valid]
                    lt = lab[tt]
                    h_ex = (lab[uu] == lt); e_ex = prob[lt]
                    # --- near (u-1,u,u+1 but > t)
                    nn = np.zeros(len(tt)); hn = np.zeros(len(tt), bool)
                    for dlt in (-1, 0, 1):
                        r = uu + dlt; good = (r > tt) & (r < N)
                        nn += good; hn |= good & (lab[np.minimum(r, N - 1)] == lt)
                    e_ne = 1 - (1 - e_ex) ** nn
                    yy = yi[tt]
                    for h, hit, ex in (("exact", h_ex, e_ex), ("near", hn, e_ne)):
                        ci = CFG_IDX[(L, lk, K, h)]
                        np.add.at(S[ci, :, 0], yy, 1); np.add.at(S[ci, :, 1], yy, hit)
                        np.add.at(S[ci, :, 2], yy, ex); np.add.at(S[ci, :, 3], yy, size[lt])
                    # --- any (dedupe by (s3, i))
                    has = (valid.astype(np.float32) @ E1) > 0
                    s_i, i_i = np.nonzero(has)
                    tq = S3[s_i] + i_i; m = L - 1 - i_i; lt = lab[tq]
                    hit = nxt[tq] <= m; ex = 1 - (1 - prob[lt]) ** m
                    ci = CFG_IDX[(L, lk, K, "any")]
                    yy = yi[tq]
                    np.add.at(S[ci, :, 0], yy, 1); np.add.at(S[ci, :, 1], yy, hit)
                    np.add.at(S[ci, :, 2], yy, ex); np.add.at(S[ci, :, 3], yy, size[lt])
    return S, D

if __name__ == "__main__":
    game, scheme, nshuf = sys.argv[1], sys.argv[2], int(sys.argv[3])
    nums, year, ym = load(game)
    blocks = blocks_month(ym) if scheme == "month" else blocks_30(len(nums))
    rng = np.random.default_rng(12345)
    SS, DD = [], []
    t0 = time.time()
    for r in range(nshuf + 1):
        x = nums if r == 0 else shuffle_year(nums, year, rng)
        S, D = run_once(x, year, blocks)
        SS.append(S.astype(np.float32)); DD.append(D.astype(np.float32))
        if r == 0: print(game, scheme, "real pass", round(time.time() - t0, 1), "s", flush=True)
        elif r % 10 == 0: print(r, round(time.time() - t0, 1), flush=True)
    np.savez_compressed(os.path.join(OUT, f"p1_{game}_{scheme}.npz"), S=np.array(SS), D=np.array(DD),
                        cfgs=np.array([str(c) for c in CFGS]), dcfgs=np.array([str(c) for c in DCFGS]), years=np.arange(Y0, 2027))
