"""Common helpers: single-column sheet of one game, class/rashi arrays, within-year shuffles."""
import csv, os
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(ROOT, "research", "singlesheet", "out")
Y0 = 1966

def load(game):
    """-> nums (N,) int, year (N,), month key (N,) ; one row per played day (Excel-row counting)."""
    p = os.path.join(ROOT, "data", f"game_{game.lower()}.csv")
    d, v = [], []
    with open(p) as f:
        for r in list(csv.reader(f))[1:]:
            d.append(r[0]); v.append(int(r[1]))
    nums = np.array(v, dtype=np.int16)
    year = np.array([int(x[:4]) for x in d], dtype=np.int32)
    ym = np.array([int(x[:4]) * 12 + int(x[5:7]) for x in d], dtype=np.int32)
    return nums, year, ym

def _pal(n): return (n % 10) * 10 + n // 10
CLS_OF = np.array([min(n, _pal(n)) for n in range(100)])
_u = np.unique(CLS_OF)
CLS_ID = np.searchsorted(_u, CLS_OF)                     # 55 classes
CLS_P = np.array([ (CLS_OF == u).sum() + (_pal(u) != u and 0) for u in _u], dtype=float)
# class size in numbers (palat pair=2, jodi=1)
CLS_SIZE = np.array([len({u, _pal(int(u))}) for u in _u], dtype=float)
CLS_PROB = CLS_SIZE / 100.0
def _fk(n): return tuple(sorted((n // 10 % 5, n % 10 % 5)))
_fks = sorted(set(_fk(n) for n in range(100)))
FAM_ID = np.array([_fks.index(_fk(n)) for n in range(100)])
FAM_SIZE = np.array([sum(1 for n in range(100) if FAM_ID[n] == k) for k in range(15)], dtype=float)
FAM_PROB = FAM_SIZE / 100.0

def arrays(nums, kind):
    """kind 'palat' or 'rashi' -> (label array, prob per label, size per label)"""
    if kind == "palat":
        return CLS_ID[nums], CLS_PROB, CLS_SIZE
    return FAM_ID[nums], FAM_PROB, FAM_SIZE

def nxt_dist(lab):
    """distance (rows) to next row with same label; big if none."""
    N = len(lab); big = 10**6
    idx = np.argsort(lab, kind="stable"); ls = lab[idx]
    nxt = np.full(N, big, dtype=np.int64)
    same = ls[1:] == ls[:-1]
    nxt[idx[:-1][same]] = idx[1:][same] - idx[:-1][same]
    return nxt

def shuffle_year(nums, year, rng):
    out = nums.copy()
    for y in np.unique(year):
        ix = np.where(year == y)[0]
        out[ix] = nums[ix][rng.permutation(len(ix))]
    return out

def blocks_month(ym):
    _, b = np.unique(ym, return_inverse=True)
    return b

def blocks_30(N):
    return np.arange(N) // 30

def pairs(L):
    I, J = np.triu_indices(L, 1)
    return I, J
