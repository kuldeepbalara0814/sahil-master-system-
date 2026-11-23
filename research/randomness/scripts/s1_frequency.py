"""1) Frequency: number, class, rashi, tens/unit, doubles, half-jodi; per game, per year, per DS decade. Chi-square + max/min vs Monte-Carlo."""
import numpy as np, common as c
R = c.rng(1)
NSIM = 2000
rows, per = [], []
out = {}

def tests(x):
    n = len(x); res = {}
    cnt = np.bincount(x, minlength=100)
    res["number(100)"] = c.chi2_gof(cnt, np.full(100, .01))
    res["class(55)"] = c.chi2_gof(np.bincount(c.CLS_IDX[x], minlength=55), c.exp_prob(c.CLS_IDX, 55))
    res["rashi(15)"] = c.chi2_gof(np.bincount(c.RASHI_IDX[x], minlength=15), c.exp_prob(c.RASHI_IDX, 15))
    res["tens(10)"] = c.chi2_gof(np.bincount(x // 10, minlength=10), np.full(10, .1))
    res["unit(10)"] = c.chi2_gof(np.bincount(x % 10, minlength=10), np.full(10, .1))
    tab = np.zeros((10, 10)); np.add.at(tab, (x // 10, x % 10), 1)
    res["tens x unit indep"] = c.chi2_indep(tab)
    k = int(c.DOUBLE[x].sum()); z = (k - .1 * n) / np.sqrt(n * .09)
    res["doubles(10%)"] = (z, 1, c.norm_2p(z))
    k = int(c.HALF[x].sum()); z = (k - .1 * n) / np.sqrt(n * .09)
    res["half-jodi(10%)"] = (z, 1, c.norm_2p(z))
    return res, cnt

for g in c.GAMES:
    D, x = c.load(g); n = len(x)
    res, cnt = tests(x)
    for k, (st, df, p) in res.items():
        rows.append([g, "all", k, n, st, df, p])
    # max/min frequency vs MC
    mx, mn = cnt.max(), cnt.min()
    sims = R.multinomial(n, np.full(100, .01), size=NSIM)
    smax, smin = sims.max(1), sims.min(1)
    out[g] = dict(n=n, max=(int(mx), int(cnt.argmax()), float(smax.mean()), c.mc_p(mx, smax)),
                  min=(int(mn), int(cnt.argmin()), float(smin.mean()), c.mc_p(mn, smin, "lower")),
                  exp=n / 100)
    # class max/min z-scores: tail
    # per year / decade
    Y = c.years(D); grp = Y if g != "DS" else (Y // 10) * 10
    label = "year" if g != "DS" else "decade"
    for gv in sorted(set(grp)):
        xx = x[grp == gv]
        r2, _ = tests(xx)
        for k, (st, df, p) in r2.items():
            per.append([g, label, int(gv), k, len(xx), st, df, p])
    if g == "DS":
        for gv in sorted(set(Y)):          # DS bhi saal-wise
            xx = x[Y == gv]; r2, _ = tests(xx)
            for k, (st, df, p) in r2.items():
                per.append([g, "year", int(gv), k, len(xx), st, df, p])

c.save_csv("s1_all.csv", ["game", "scope", "test", "n", "stat", "df", "p"], rows)
c.save_csv("s1_peryear.csv", ["game", "unit", "period", "test", "n", "stat", "df", "p"], per)
# p-value uniformity across years: KS + count p<0.05
summ = []
for g in c.GAMES:
    for t in sorted(set(r[3] for r in per)):
        for u in (["year"] if g != "DS" else ["year", "decade"]):
            ps = [r[7] for r in per if r[0] == g and r[3] == t and r[1] == u]
            if len(ps) < 3: continue
            ks, d = c.ks_uniform_p(ps)
            summ.append([g, u, t, len(ps), sum(p < .05 for p in ps), 0.05 * len(ps), min(ps), ks])
c.save_csv("s1_pvalue_summary.csv", ["game", "unit", "test", "n_periods", "n_p<0.05", "expected", "min_p", "KS_p_uniformity"], summ)
c.save_json("s1_maxmin.json", out)
print("== all-data tests"); [print("%-3s %-20s n=%-6d stat=%8.2f df=%-3d p=%s" % (r[0], r[2], r[3], r[4], r[5], c.fmt_p(r[6]))) for r in rows]
print("== max/min"); [print(g, v) for g, v in out.items()]
print("== per-period p summary"); [print(r[0], r[1], "%-20s" % r[2], r[3], "p<.05:", r[4], "(exp %.1f)" % r[5], "minp %.4f" % r[6], "KS_p %.3f" % r[7]) for r in summ]
