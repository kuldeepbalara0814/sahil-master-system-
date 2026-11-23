"""5) Drift / change-points: year-wise (DS decade-wise) homogeneity of number distribution, mean, digit marginals, repeat rate, class/rashi; permutation change-point scan."""
import numpy as np, common as c
S = c.load_all(); NS = 200
rows = []; cp_rows = []
def hom(tab):
    st, df, p = c.chi2_indep(tab); return st, df, p
for g, (D, x) in S.items():
    rg = c.rng(500 + len(x)); yr = c.years(D); n = len(x)
    ys = np.unique(yr)
    groups = {"year": yr} if g != "DS" else {"year": yr, "decade": (yr // 10) * 10}
    feats = {"tens digit": x // 10, "unit digit": x % 10, "class(55)": c.CLS_IDX[x], "rashi(15)": c.RASHI_IDX[x], "number(100) 10-bin": x // 10}
    for gn, lab in groups.items():
        u = np.unique(lab)
        for fn, f in feats.items():
            K = int(f.max()) + 1; tab = np.zeros((len(u), K)); np.add.at(tab, (np.searchsorted(u, lab), f), 1)
            tab = tab[:, tab.sum(0) > 0]
            st, df, p = hom(tab)
            # permutation check of the chi2 (small expected counts)
            sims = []
            for _ in range(100):
                fp = rg.permutation(f); t2 = np.zeros((len(u), K)); np.add.at(t2, (np.searchsorted(u, lab), fp), 1); t2 = t2[:, t2.sum(0) > 0]
                sims.append(hom(t2)[0])
            rows.append([g, gn, fn, len(u), st, df, p, c.mc_p(st, sims)])
        # mean & repeat rate by group (ANOVA-like via permutation of group labels)
        mu = np.array([x[lab == k].mean() for k in u]); rep = np.array([(x[1:][lab[1:] == k] == x[:-1][lab[1:] == k]).mean() for k in u])
        def sv(v, l): return np.var([v[l == k].mean() for k in u]) if False else None
        ob = np.var(mu * np.sqrt([(lab == k).sum() for k in u]))
        sims = []
        for _ in range(NS):
            lp = rg.permutation(lab); sims.append(np.var(np.array([x[lp == k].mean() for k in u]) * np.sqrt([(lp == k).sum() for k in u])))
        rows.append([g, gn, "group mean spread (permuted labels)", len(u), float(ob), 0, 0.0, c.mc_p(ob, sims)])
        rr = np.array([(rep[i], (lab == k).sum()) for i, k in enumerate(u)])
        rows.append([g, gn, "next-day repeat rate range min..max", len(u), float(rep.min()), float(rep.max()), 0.01, 0.0])
    # change-point scan on mean, tens, unit: max |CUSUM| standardized vs permutation
    for fn, f in (("mean", x.astype(float)), ("tens", (x // 10).astype(float)), ("unit", (x % 10).astype(float)), ("class-is-double", c.DOUBLE[x].astype(float))):
        def scan(v):
            cs = np.cumsum(v - v.mean()); k = np.arange(1, len(v)); s = v.std() * np.sqrt(k * (len(v) - k) / len(v))
            z = np.abs(cs[:-1]) / np.where(s > 0, s, 1); return z.max(), int(z.argmax())
        ob, loc = scan(f); sims = np.array([scan(rg.permutation(f))[0] for _ in range(NS)])
        cp_rows.append([g, fn, ob, str(D[loc]), float(np.mean(sims)), c.mc_p(ob, sims)])
    print(g, "drift done", flush=True)
c.save_csv("s5_drift.csv", ["game", "grouping", "feature", "groups", "stat", "df_or_max", "p_chi2", "p_perm"], rows)
c.save_csv("s5_changepoint.csv", ["game", "series", "max_std_cusum", "at_date", "perm_mean", "p_perm"], cp_rows)
for r in rows + cp_rows: print(r)
