"""Part 5: does the design span (box count) repeat from step to step more than chance?
S12(k)= minimal boundary L (3..15) at which a design (>=2 common links, same relative rows) exists between months k, k+1 (code 16 = none).
Chain test: S12(k) vs S23=S12(k+1)  (equal / within 1).  T(k)= tightest span of >=2 links inside month k; T(k) vs T(k+1).
usage: part5.py GAME NSHUF -> out/p5_<GAME>.npz  R[run,link,chain,year,3 (n, equal, within1)], H[run,link,17] histogram of S12
"""
import sys, time
import numpy as np
from common import *

LSALL = list(range(3, 16))
def run_once(nums, year, blocks):
    N = len(nums); yi = year - Y0
    nb = blocks.max() + 1
    bstart = np.searchsorted(blocks, np.arange(nb)); bend = np.append(bstart[1:], N) - 1
    R = np.zeros((2, 2, 2026 - Y0 + 1, 3)); H = np.zeros((2, 17))
    for li, lk in enumerate(("palat", "rashi")):
        lab, prob, size = arrays(nums, lk)
        S12 = np.full(nb, 16); T = np.full(nb, 16)
        for L in LSALL:
            I, J = pairs(L); P = len(I)
            starts = np.arange(0, N - L + 1)
            A = (lab[starts[:, None] + I[None, :]] == lab[starts[:, None] + J[None, :]]) & (blocks[starts] == blocks[starts + L - 1])[:, None]
            A = np.vstack([A, np.zeros((L - 1, P), bool)]).astype(np.float32)
            nl = A.sum(1)
            for b in range(nb):
                Ab = A[bstart[b]:bend[b] + 1]
                if T[b] == 16 and (nl[bstart[b]:bend[b] + 1] >= 2).any(): T[b] = L
                if b + 1 < nb and S12[b] == 16:
                    A2 = A[bstart[b + 1]:bend[b + 1] + 1]
                    Ab = Ab[Ab.any(1)]; A2 = A2[A2.any(1)]
                    if len(Ab) and len(A2) and ((Ab @ A2.T) >= 2).any(): S12[b] = L
        S12 = S12[:-1]
        for ch, seq in enumerate((S12, T)):
            for k in range(len(seq) - 1 if ch == 0 else len(seq) - 1):
                y = yi[bstart[k + 1]]
                if seq[k] == 16 or seq[k + 1] == 16: continue
                R[li, ch, y, 0] += 1; R[li, ch, y, 1] += seq[k] == seq[k + 1]; R[li, ch, y, 2] += abs(int(seq[k]) - int(seq[k + 1])) <= 1
        np.add.at(H[li], S12, 1)
    return R, H

if __name__ == "__main__":
    game, nshuf = sys.argv[1], int(sys.argv[2])
    nums, year, ym = load(game); blocks = blocks_month(ym)
    rng = np.random.default_rng(5); RR, HH = [], []; t0 = time.time()
    for r in range(nshuf + 1):
        x = nums if r == 0 else shuffle_year(nums, year, rng)
        R, H = run_once(x, year, blocks); RR.append(R); HH.append(H)
        if r % 5 == 0: print(game, r, round(time.time() - t0, 1), flush=True)
    np.savez_compressed(os.path.join(OUT, f"p5_{game}.npz"), R=np.array(RR, dtype=np.float32), H=np.array(HH), years=np.arange(Y0, 2027))
