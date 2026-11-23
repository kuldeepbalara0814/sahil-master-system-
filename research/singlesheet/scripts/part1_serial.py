"""Part 1 with a REPEAT-PRESERVING null (serial surrogate). usage: part1_serial.py GAME SCHEME NSHUF
Null: x_t = x_{t-k} with prob q_k (k=1..5, fitted so lag-k repeat rate matches real), else draw from per-decade marginal.
Output out/p1s_<GAME>_<SCHEME>.npz (same layout as part1; run 0 = real) + printed lag-repeat check."""
import sys, time
import numpy as np
from common import *
import part1
from part1 import run_once

KMAX = 5
def lag_rates(x):
    return np.array([(x[k:] == x[:-k]).mean() for k in range(1, KMAX + 1)])

def fit(nums, year):
    dec = (year // 10)
    marg = {d: np.bincount(nums[dec == d], minlength=100) / (dec == d).sum() for d in np.unique(dec)}
    r0 = np.mean([ (np.bincount(nums[dec == d], minlength=100)/(dec==d).sum()) @ (np.bincount(nums[dec == d], minlength=100)/(dec==d).sum()) for d in np.unique(dec)])
    r = lag_rates(nums)
    q = np.clip((r - r0) / (1 - r0), 0, None)
    return marg, q, r, r0

def surrogate(nums, year, marg, q, rng):
    N = len(nums); dec = year // 10
    out = np.zeros(N, np.int16)
    cdf = {d: np.cumsum(p) for d, p in marg.items()}
    U = rng.random(N); V = rng.random(N)
    qc = np.cumsum(q)
    for t in range(N):
        u = U[t]
        k = np.searchsorted(qc, u) + 1 if u < qc[-1] else 0
        if k and t - k >= 0: out[t] = out[t - k]
        else: out[t] = min(np.searchsorted(cdf[dec[t]], V[t]), 99)
    return out

if __name__ == "__main__":
    game, scheme, nshuf = sys.argv[1], sys.argv[2], int(sys.argv[3])
    nums, year, ym = load(game)
    blocks = blocks_month(ym) if scheme == "month" else blocks_30(len(nums))
    marg, q, r, r0 = fit(nums, year)
    print("real lag rates", r.round(4), "r0", round(r0, 4), "q", q.round(4), flush=True)
    rng = np.random.default_rng(777)
    SS, DD = [], []; t0 = time.time(); sr = []
    for i in range(nshuf + 1):
        x = nums if i == 0 else surrogate(nums, year, marg, q, rng)
        if i > 0: sr.append(lag_rates(x))
        S, D = run_once(x, year, blocks)
        SS.append(S.astype(np.float32)); DD.append(D.astype(np.float32))
        if i % 10 == 0: print(i, round(time.time() - t0, 1), flush=True)
    print("surrogate lag rates mean", np.mean(sr, 0).round(4), flush=True)
    np.savez_compressed(os.path.join(OUT, f"p1s_{game}_{scheme}.npz"), S=np.array(SS), D=np.array(DD),
                        cfgs=np.array([str(c) for c in part1.CFGS]), years=np.arange(Y0, 2027))
