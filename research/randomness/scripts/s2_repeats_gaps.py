"""2) Repeats (lag 1..60), band (gap) distribution & longest band, hot/cold overdispersion (windows). Baseline = shuffle (marginals same)."""
import numpy as np, common as c
S = c.load_all()
NS = 300
rows_rep, summ, band_rows, disp_rows = [], [], [], []

def rep_table(x, key):
    n = len(x); y = key[x]
    cnt = np.bincount(y); q = float((cnt * (cnt - 1)).sum() / (n * (n - 1)))   # P(do alag position same group), marginals se
    out = []
    for k in range(1, 61):
        m = n - k; obs = int((y[:-k] == y[k:]).sum()); e = m * q; sd = np.sqrt(m * q * (1 - q))
        z = (obs - e) / sd; out.append((k, obs, e, z, c.norm_2p(z)))
    return out

for g, (D, x) in S.items():
    for kn, key in (("number", np.arange(100)), ("class", c.CLS_IDX)):
        t = rep_table(x, key)
        for k, o, e, z, p in t: rows_rep.append([g, kn, k, o, e, z, p])
        ps = [r[4] for r in t]; zs = np.array([r[3] for r in t])
        ks, _ = c.ks_uniform_p(ps)
        summ.append([g, kn, 60, sum(p < .05 for p in ps), 3.0, min(ps), min(1, min(ps) * 60), float(zs.sum() / np.sqrt(60)), c.norm_2p(zs.sum() / np.sqrt(60)), ks, int(c.bh(ps))])

c.save_csv("s2_repeat_lags.csv", ["game", "key", "lag", "obs", "exp", "z", "p"], rows_rep)
c.save_csv("s2_repeat_summary.csv", ["game", "key", "n_lags", "n_p<.05", "exp_n", "min_p", "bonferroni_min_p", "pooled_z(sum z/sqrt60)", "pooled_p", "KS_p_uniform", "BH_rejects"], summ)

# ---- band (gap) distribution
def gaps(x):
    o = np.argsort(x, kind="stable"); xs = x[o]; d = np.diff(o); same = xs[1:] == xs[:-1]
    return d[same]

bins = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1 << 30]
def band_stats(x):
    g = gaps(x); h = np.histogram(g, bins=bins)[0]
    p_geo = np.array([(0.99 ** (bins[i] - 1) - 0.99 ** (bins[i + 1] - 1)) for i in range(len(bins) - 1)])
    return g, h, p_geo

for gname, (D, x) in S.items():
    rg = c.rng(21 + len(x))
    g, h, p_geo = band_stats(x)
    # first-order: mean band, longest band, chi2 of band histogram vs shuffle
    # lamba: uniform-marginal geometric, empirical q ka geometric
    cnt = np.bincount(x, minlength=100)
    obs_max = int(g.max()); obs_mean = float(g.mean())
    # longest unseen interval per number including start/end
    def longest(x_):
        o = np.argsort(x_, kind="stable"); xs = x_[o]
        best = 0
        for v in range(100):
            pos = o[xs == v]
            if len(pos) == 0: best = max(best, len(x_)); continue
            gg = np.concatenate([[pos[0]], np.diff(pos), [len(x_) - 1 - pos[-1]]]); best = max(best, int(gg.max()))
        return best
    def chi_h(h_, e_):
        m = e_ > 5; return float((((h_[m] - e_[m]) ** 2) / e_[m]).sum())
    exp_h = h.sum() * p_geo / p_geo.sum()
    # shuffle baseline
    sims_h, sims_max, sims_long, sims_mean = [], [], [], []
    for _ in range(NS):
        xs_ = rg.permutation(x); gg = gaps(xs_)
        hh = np.histogram(gg, bins=bins)[0]; sims_h.append(hh); sims_max.append(int(gg.max())); sims_mean.append(gg.mean()); sims_long.append(longest(xs_) if len(x) < 6000 or _ < 100 else 0)
    sims_h = np.array(sims_h); mu = sims_h.mean(0); sd = sims_h.std(0)
    obs_chi = float((((h - mu) ** 2) / np.where(mu > 0, mu, 1)).sum()); sim_chi = (((sims_h - mu) ** 2) / np.where(mu > 0, mu, 1)).sum(1)
    sl = np.array([v for v in sims_long if v > 0]); ol = longest(x)
    res = dict(game=gname, n=len(x), n_gaps=len(g), mean_band=obs_mean, mc_mean_band=float(np.mean(sims_mean)), p_mean_band=c.mc_p(obs_mean, sims_mean, "two"),
               max_interior_band=obs_max, mc_max_interior_mean=float(np.mean(sims_max)), p_max_interior=c.mc_p(obs_max, sims_max, "two"),
               longest_unseen=ol, mc_longest_unseen_mean=float(sl.mean()), p_longest_unseen=c.mc_p(ol, sl, "two"),
               hist_chi2=obs_chi, p_hist_chi2=c.mc_p(obs_chi, sim_chi, "upper"))
    band_rows.append(res)
    for i in range(len(bins) - 1):
        band_rows.append(dict(game=gname, bin="%d-%s" % (bins[i], "inf" if bins[i + 1] > 1e6 else bins[i + 1] - 1), obs=int(h[i]), shuffle_mean=float(mu[i]), shuffle_sd=float(sd[i]), z=float((h[i] - mu[i]) / sd[i]) if sd[i] > 0 else 0.0))
    print(gname, res, flush=True)
c.save_json("s2_band.json", band_rows)

# ---- hot/cold overdispersion windows
for gname, (D, x) in S.items():
    rg = c.rng(33 + len(x)); n = len(x)
    for W in (30, 90, 365, 100, 200, 500, 1000):
        nw = n // W
        if nw < 4: continue
        xx = x[:nw * W]
        def stat(v):
            w = np.repeat(np.arange(nw), W); cnt = np.bincount(w * 100 + v, minlength=nw * 100).reshape(nw, 100)
            tot = cnt.sum(0); E = tot / nw            # expected per window per number (marginal)
            Ex = np.where(E > 0, E, 1)
            chi = (((cnt - E) ** 2) / Ex).sum()
            cc = cnt - cnt.mean(0)                    # persistence: window t vs t+1 correlation pooled
            r = float((cc[:-1] * cc[1:]).sum() / (cc ** 2).sum())
            return float(chi), r
        obs, r_obs = stat(xx)
        sims = np.array([stat(rg.permutation(xx)) for _ in range(NS)])
        z = (obs - sims[:, 0].mean()) / sims[:, 0].std(); zr = (r_obs - sims[:, 1].mean()) / sims[:, 1].std()
        disp_rows.append([gname, W, nw, obs, float(sims[:, 0].mean()), float(sims[:, 0].std()), z, c.mc_p(obs, sims[:, 0], "two"), r_obs, zr, c.mc_p(r_obs, sims[:, 1], "two")])
        print(gname, "W", W, "chi2 z %.2f p %.3f | persist r %.4f z %.2f" % (z, disp_rows[-1][7], r_obs, zr), flush=True)
c.save_csv("s2_dispersion.csv", ["game", "W", "n_windows", "chi2_obs", "shuffle_mean", "shuffle_sd", "z", "p_two", "persist_r", "persist_z", "persist_p"], disp_rows)
print("== repeat summary"); [print(r) for r in summ]
