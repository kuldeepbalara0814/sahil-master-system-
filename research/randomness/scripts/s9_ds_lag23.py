"""9) DS short-lag repeat excess (lag 2,3 rows): stable across decades? expected from the game's own marginal (shuffle-equivalent)."""
import numpy as np, common as c
S = c.load_all(); rows = []
for g in ("DS", "FB", "GB", "GL"):
    D, x = S[g]; yr = c.years(D); dec = (yr // 10) * 10 if g == "DS" else (yr // 5) * 5
    for d in np.unique(dec):
        m = dec == d; v = x[m]; n = len(v); pm = np.bincount(v, minlength=100) / n
        for L in (1, 2, 3, 4):
            o = int((v[L:] == v[:-L]).sum()); e = (n - L) * float((pm ** 2).sum()); sd = np.sqrt(e)
            rows.append([g, int(d), L, n, o, round(e, 1), round(o / e, 3), round((o - e) / sd, 2)])
c.save_csv("s9_lag_by_period.csv", ["game", "period_start", "lag_rows", "n", "obs_repeats", "expected", "ratio", "z"], rows)
for r in rows:
    if r[2] in (2, 3): print(r)
