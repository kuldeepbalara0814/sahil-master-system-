"""7) Is the within-year spread of counts too SMALL (more even than chance)? Sum of per-year Pearson chi2 (vs uniform 100) compared to iid-uniform Monte Carlo (5000 sims), for 2013+ games and DS13; also by half-year/quarter windows and per-window max count."""
import numpy as np, common as c
S = c.load_all(); rg = c.rng(777); rows = []
NSIM = 3000
for g in ("FB", "GB", "GL", "DS13"):
    D, x = S[g]; yr = c.years(D)
    for nm, lab in (("year", yr), ("half-year", yr * 2 + np.array([(d.month > 6) for d in D])), ("quarter", yr * 4 + np.array([(d.month - 1) // 3 for d in D]))):
        u, inv = np.unique(lab, return_inverse=True); ns = np.bincount(inv)
        keep = ns > 50; 
        def stat(xv):
            tab = np.zeros((len(u), 100)); np.add.at(tab, (inv, xv), 1)
            e = ns[:, None] / 100.0
            chi = ((tab - e) ** 2 / e).sum(1); mx = tab.max(1)
            return chi[keep].sum() / keep.sum(), mx[keep].mean(), (tab[keep] == 0).sum(1).mean()
        ob = stat(x); sims = np.array([stat(rg.integers(0, 100, len(x))) for _ in range(NSIM if nm != "quarter" else 1500)])
        for j, sn in enumerate(["mean chi2 per window (df=99 expected 99)", "mean max count", "mean number of numbers never seen"]):
            rows.append([g, nm, int(keep.sum()), sn, float(ob[j]), float(sims[:, j].mean()), float(sims[:, j].std()), float((ob[j] - sims[:, j].mean()) / sims[:, j].std()), c.mc_p(ob[j], sims[:, j], "two")])
        print(g, nm, "done", flush=True)
c.save_csv("s7_underdispersion.csv", ["game", "window", "n_windows", "stat", "obs", "iid_mean", "iid_sd", "z", "p_two"], rows)
for r in rows: print(r)
