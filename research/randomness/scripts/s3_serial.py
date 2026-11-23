"""3) Serial structure: autocorr, runs, cross-game same-day / lagged, calendar effects (weekday, day-of-month, month, day after holiday)."""
import numpy as np, common as c, datetime as dt
S = c.load_all()
NP = 500
out_ac, out_run, out_cross, out_cal = [], [], [], []

def acf(v, K=60):
    v = v - v.mean(); d = (v * v).sum(); return np.array([(v[:-k] * v[k:]).sum() / d for k in range(1, K + 1)])

# ---------- autocorrelation
for g, (D, x) in S.items():
    n = len(x)
    ser = {"number": x.astype(float), "tens": (x // 10).astype(float), "unit": (x % 10).astype(float), "class": c.CLS[x].astype(float),
           "number_ind_double": c.DOUBLE[x].astype(float)}
    for nm, v in ser.items():
        r = acf(v); band = 1.96 / np.sqrt(n); outside = [k + 1 for k in range(60) if abs(r[k]) > band]
        Q = n * (n + 2) * sum(r[k] ** 2 / (n - k - 1) for k in range(60)); p = c.chi2_sf(Q, 60)
        ps = [c.norm_2p(r[k] * np.sqrt(n)) for k in range(60)]
        out_ac.append([g, nm, n, round(band, 4), len(outside), 3.0, " ".join(map(str, outside[:12])), float(r[0]), float(Q), p, min(ps), min(1, 60 * min(ps))])
c.save_csv("s3_autocorr_summary.csv", ["game", "series", "n", "band95", "n_lags_outside", "expected", "lags_outside(first12)", "r_lag1", "LjungBox_Q60", "p_LB", "min_p", "bonf_min_p"], out_ac)

# ---------- runs tests
def runs_z(b):
    b = np.asarray(b).astype(int); n1 = b.sum(); n0 = len(b) - n1
    R = 1 + (b[1:] != b[:-1]).sum(); mu = 2 * n1 * n0 / len(b) + 1; var = (mu - 1) * (mu - 2) / (len(b) - 1)
    return float((R - mu) / np.sqrt(var)), int(R), float(mu)
for g, (D, x) in S.items():
    med = np.median(x)
    z, R, mu = runs_z(x > med); out_run.append([g, "above/below median", R, mu, z, c.norm_2p(z)])
    z, R, mu = runs_z(x % 2 == 0); out_run.append([g, "even/odd", R, mu, z, c.norm_2p(z)])
    z, R, mu = runs_z((x // 10) >= 5); out_run.append([g, "tens>=5", R, mu, z, c.norm_2p(z)])
    z, R, mu = runs_z((x % 10) >= 5); out_run.append([g, "unit>=5", R, mu, z, c.norm_2p(z)])
    def ud_runs(v):
        d = np.diff(v); d = d[d != 0]; s = d > 0; return int(1 + (s[1:] != s[:-1]).sum())
    rg0 = c.rng(40); R0 = ud_runs(x); sims0 = np.array([ud_runs(rg0.permutation(x)) for _ in range(300)])
    out_run.append([g, "up/down runs (MC shuffle)", R0, float(sims0.mean()), (R0 - sims0.mean()) / sims0.std(), c.mc_p(R0, sims0, "two")])
    # longest run of ayse same-parity vs MC
    def longest(b):
        ch = np.flatnonzero(np.diff(b.astype(int)) != 0); idx = np.concatenate([[-1], ch, [len(b) - 1]]); return int(np.diff(idx).max())
    rg = c.rng(41); b = x > med; ob = longest(b); sims = [longest(rg.permutation(b)) for _ in range(200)]
    out_run.append([g, "longest run above/below median", ob, float(np.mean(sims)), (ob - np.mean(sims)) / max(np.std(sims), 1e-9), c.mc_p(ob, sims, "two")])
c.save_csv("s3_runs.csv", ["game", "test", "obs_runs", "expected", "z", "p"], out_run)

# ---------- cross game same-day and lagged
dmap = {g: {d: v for d, v in zip(*S[g][:1], S[g][1])} for g in S}
pairs = [("FB", "GB"), ("FB", "GL"), ("GB", "GL"), ("FB", "DS13"), ("GB", "DS13"), ("GL", "DS13")]
for a, b in pairs:
    common = sorted(set(dmap[a]) & set(dmap[b]))
    xa = np.array([dmap[a][d] for d in common]); xb = np.array([dmap[b][d] for d in common]); n = len(common)
    def eq_test(ya, yb, K):
        ca, cb = np.bincount(ya, minlength=K) / len(ya), np.bincount(yb, minlength=K) / len(yb); q = float((ca * cb).sum())
        o = int((ya == yb).sum()); m = len(ya); z = (o - m * q) / np.sqrt(m * q * (1 - q)); return o, m * q, z, c.norm_2p(z)
    o, e, z, p = eq_test(xa, xb, 100); out_cross.append([a, b, "same-day equal number", 0, n, o, e, z, p])
    o, e, z, p = eq_test(c.CLS_IDX[xa], c.CLS_IDX[xb], 55); out_cross.append([a, b, "same-day equal class", 0, n, o, e, z, p])
    o, e, z, p = eq_test(c.RASHI_IDX[xa], c.RASHI_IDX[xb], 15); out_cross.append([a, b, "same-day equal rashi", 0, n, o, e, z, p])
    r = float(np.corrcoef(xa, xb)[0, 1]); z = r * np.sqrt(n); out_cross.append([a, b, "same-day correlation of number", 0, n, r, 0, z, c.norm_2p(z)])
    for nm, fa, fb in (("tens-tens", xa // 10, xb // 10), ("unit-unit", xa % 10, xb % 10), ("tens-unit", xa // 10, xb % 10), ("unit-tens", xa % 10, xb // 10)):
        t = np.zeros((10, 10)); np.add.at(t, (fa, fb), 1); st, df, p = c.chi2_indep(t); out_cross.append([a, b, "same-day indep chi2 " + nm, 0, n, st, df, (st - df) / np.sqrt(2 * df), p])
    # lagged: b[t+L] vs a[t], L=-7..7 (not 0)
    idx = {d: i for i, d in enumerate(S[a][0])}; idxb = {d: i for i, d in enumerate(S[b][0])}
    ya_all, yb_all = S[a][1], S[b][1]
    zs = []
    for L in list(range(-7, 0)) + list(range(1, 8)):
        pa, pb = [], []
        for d, i in idx.items():
            j = idxb.get(d)
            if j is None: continue
            j2 = j + L
            if 0 <= j2 < len(yb_all): pa.append(ya_all[i]); pb.append(yb_all[j2])
        pa, pb = np.array(pa), np.array(pb); o, e, z, p = eq_test(c.CLS_IDX[pa], c.CLS_IDX[pb], 55); zs.append(z)
        o2, e2, z2, p2 = eq_test(pa, pb, 100)
        out_cross.append([a, b, "lagged equal number (b shifted by L rows)", L, len(pa), o2, e2, z2, p2])
        out_cross.append([a, b, "lagged equal class (b shifted by L rows)", L, len(pa), o, e, z, p])
c.save_csv("s3_cross_game.csv", ["gameA", "gameB", "test", "lag", "n", "obs/stat", "exp/df", "z", "p"], out_cross)

# ---------- calendar effects (permutation chi2 of group x value)
def perm_chi(lab, val, K, R_, nperm=NP):
    lab = np.asarray(lab); val = np.asarray(val); L = int(lab.max()) + 1
    def st(v):
        t = np.bincount(lab * K + v, minlength=L * K).reshape(L, K).astype(float)
        e = np.outer(t.sum(1), t.sum(0)) / t.sum(); m = e > 0
        return float(((t[m] - e[m]) ** 2 / e[m]).sum())
    o = st(val); sims = np.array([st(R_.permutation(val)) for _ in range(nperm)])
    return o, float(sims.mean()), c.mc_p(o, sims)
def perm_mean(lab, val, R_, nperm=NP):
    lab = np.asarray(lab); L = int(lab.max()) + 1
    def st(v):
        s = np.bincount(lab, weights=v, minlength=L); cn = np.bincount(lab, minlength=L); m = cn > 0
        mu = v.mean(); return float((cn[m] * (s[m] / cn[m] - mu) ** 2).sum())
    v = val.astype(float); o = st(v); sims = np.array([st(R_.permutation(v)) for _ in range(nperm)])
    return o, float(sims.mean()), c.mc_p(o, sims)
for g, (D, x) in S.items():
    R_ = c.rng(51 + len(x)); n = len(x)
    wd = np.array([d.weekday() for d in D]); dom = np.array([d.day - 1 for d in D]); mon = np.array([d.month - 1 for d in D])
    have = set(D); aft = np.array([(d - dt.timedelta(days=1)) not in have for d in D]).astype(int)   # pichla din chhuti (mahine ka aakhri din)
    aft[0] = 0
    tests = [("weekday", wd), ("day-of-month", dom), ("month-of-year", mon), ("day-after-holiday", aft)]
    for nm, lab in tests:
        for vn, val, K in (("number", x, 100), ("tens", x // 10, 10), ("unit", x % 10, 10), ("class", c.CLS_IDX[x], 55)):
            if nm in ("day-of-month",) and vn in ("number", "class"): continue
            o, mu, p = perm_chi(lab, val, K, R_, NP if K <= 10 else 300); out_cal.append([g, nm, vn + " (chi2 perm)", n, o, mu, p])
        o, mu, p = perm_mean(lab, x, R_); out_cal.append([g, nm, "mean number (between-group SS perm)", n, o, mu, p])
        # repeat rate lag1 by group-of-today
        y = (x[1:] == x[:-1]).astype(int); o, mu, p = perm_chi(lab[1:], y, 2, R_); out_cal.append([g, nm, "lag1 repeat rate by group", n, o, mu, p])
        # doubles
        o, mu, p = perm_chi(lab, c.DOUBLE[x].astype(int), 2, R_); out_cal.append([g, nm, "doubles rate by group", n, o, mu, p])
    print(g, "calendar done", flush=True)
c.save_csv("s3_calendar.csv", ["game", "factor", "test", "n", "stat", "perm_mean", "p_perm"], out_cal)
print("== autocorr"); [print(r) for r in out_ac]
print("== runs"); [print(r) for r in out_run]
print("== cross"); [print(r) for r in out_cross if r[3] == 0 or abs(r[7]) > 2.6]
print("== calendar p<0.05"); [print(r) for r in out_cal if r[-1] < .05]
print("calendar tests", len(out_cal), "p<.05:", sum(r[-1] < .05 for r in out_cal), "BH rejects", c.bh([r[-1] for r in out_cal]))
