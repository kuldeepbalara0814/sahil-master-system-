"""Helpers: z-scores vs within-year shuffle runs (run 0 = real)."""
import numpy as np
from common import Y0

ERAS_DS = [("1966-79", 1966, 1979), ("1980-89", 1980, 1989), ("1990-99", 1990, 1999), ("2000-09", 2000, 2009), ("2010-19", 2010, 2019), ("2020-26", 2020, 2026)]
ERAS_13 = [("2013-19", 2013, 2019), ("2020-26", 2020, 2026)]

def ymask(a, b):
    y = np.arange(Y0, 2027); return (y >= a) & (y <= b)

def zscan(S, a=Y0, b=2026, minn=1):
    """S [R+1, C, Y, 4(n,hit,exp,size)] -> dict of arrays (per cfg)."""
    m = ymask(a, b)
    T = S[:, :, m, :].sum(2).astype(float)                    # R+1, C, 4
    ex = T[..., 1] - T[..., 2]
    real = ex[0]; sh = ex[1:]
    mu = sh.mean(0); sd = sh.std(0, ddof=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        z = np.where(sd > 0, (real - mu) / sd, 0.0)
        lift = np.where(T[0, :, 2] > 0, T[0, :, 1] / T[0, :, 2], np.nan)
        lsh = np.where(T[1:, :, 2] > 0, T[1:, :, 1] / T[1:, :, 2], np.nan)
        lsd = np.nanstd(lsh, 0, ddof=1); lmu = np.nanmean(lsh, 0)
        size = np.where(T[0, :, 0] > 0, T[0, :, 3] / T[0, :, 0], np.nan)
    p = (1 + (sh >= real[None, :]).sum(0)) / (sh.shape[0] + 1)
    zs = np.where(sd > 0, (sh - mu) / sd, 0.0)
    return dict(n=T[0, :, 0], hit=T[0, :, 1], exp=T[0, :, 2], lift=lift, lift_lo=lift - 1.96 * lsd, lift_hi=lift + 1.96 * lsd,
                shuf_lift=lmu, excess=real, z=z, p=p, size=size, zs=zs, real=real, sh=sh, sd=sd)

def fwer(res, elig):
    """family-wise p for max z over eligible cfgs (permutation of max)."""
    zr = res["z"][elig]; zs = res["zs"][:, elig]
    if len(zr) == 0: return np.nan, np.nan
    mx = zr.max(); msh = zs.max(1)
    return mx, (1 + (msh >= mx).sum()) / (len(msh) + 1)
