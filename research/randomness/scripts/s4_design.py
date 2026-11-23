"""4) Design/copy structure on a single column, vs shuffled-within-year controls (marginals same)."""
import numpy as np, common as c, datetime as dt, sys
NSH = int(sys.argv[1]) if len(sys.argv) > 1 else 200
S = c.load_all()
G = list(range(1, 16)); DMAX = 29; LS = (8, 10, 12)

def shuffle_within_year(x, bounds, rg):
    y = x.copy()
    for a, b in bounds: y[a:b] = rg.permutation(x[a:b])
    return y

def year_bounds(D):
    Y = c.years(D); out = []; s = 0
    for i in range(1, len(Y) + 1):
        if i == len(Y) or Y[i] != Y[s]: out.append((s, i)); s = i
    return out

def month_pairs(D, shift_months, days=range(1, 29)):
    """(idx_a, idx_b, group_id) : har (saal,mahina) ka (day d) -> agle mahine ka wahi d."""
    ix = {d: i for i, d in enumerate(D)}; PA, PB, GID = [], [], []; gid = 0
    ym = sorted(set((d.year, d.month) for d in D))
    for (y, m) in ym:
        y2, m2 = (y + (m + shift_months - 1) // 12, (m + shift_months - 1) % 12 + 1)
        got = False
        for d in days:
            try: a = ix.get(dt.date(y, m, d)); b = ix.get(dt.date(y2, m2, d))
            except ValueError: continue
            if a is not None and b is not None: PA.append(a); PB.append(b); GID.append(gid); got = True
        if got: gid += 1
    return np.array(PA), np.array(PB), np.array(GID), gid

def stats(cl, n, mp, tri):
    """cl = class idx series. returns dict of statistics."""
    out = {}
    eq = {d: (cl[:-d] == cl[d:]) for d in range(1, DMAX + max(G) + 1)}
    tot, win = [], []
    for g in G:
        T = 0; acc = np.zeros(n - g - 1, bool)
        for d in range(1, DMAX + 1):
            m = n - d - g
            ev = eq[d][:m] & eq[d][g:g + m]; T += int(ev.sum()); acc[:m] |= ev
        tot.append(T); win.append(int(acc.sum()))
    out["T"] = np.array(tot); out["W"] = np.array(win)
    # independence-adjusted expectation using observed lag repeat rates
    r = np.array([eq[d].mean() for d in range(1, DMAX + 1)]); out["Eind"] = np.array([sum((n - d - g) * r[d - 1] ** 2 for d in range(1, DMAX + 1)) for g in G])
    # month-to-month class matches by shift
    PA, PB, GID, ng = mp
    mm = {}
    for s in range(-3, 4):
        pb = PB + s; ok = (pb >= 0) & (pb < n); m = (cl[PA[ok]] == cl[pb[ok]]); k = np.bincount(GID[ok], weights=m, minlength=ng)
        mm[s] = (int(m.sum()), int((k >= 3).sum()), int(k.max()))
    out["MM"] = mm
    # steps-like common links across blocks
    for key, (A, B, Cc) in tri.items():
        eqd = eq
        res = {}
        for L in LS:
            res[L] = [np.zeros(len(A), int), np.zeros(len(A), int)]
        ok = (A + 12 < n) & (B + 12 < n) & (Cc + 12 < n); A, B, Cc = A[ok], B[ok], Cc[ok]
        for L in LS:
            res[L] = [np.zeros(len(A), int), np.zeros(len(A), int)]
        for i in range(12):
            for j in range(i + 1, 12):
                dd = j - i; e = eqd[dd]
                ea, eb, ec = e[A + i], e[B + i], e[Cc + i]
                for L in LS:
                    if j < L: res[L][0] += (ea & eb); res[L][1] += (ea & eb & ec)
        for L in LS:
            p2, p3 = res[L]
            out["steps_%s_L%d" % (key, L)] = (int(p2.sum()), int((p2 >= 2).sum()), int((p2 >= 3).sum()), int((p3 >= 2).sum()), int(p3.max()))
    return out

rows = []; pair_rows = []; mm_rows = []; st_rows = []
for gname, (D, x) in S.items():
    n = len(x); bounds = year_bounds(D); rg = c.rng(61 + n)
    mp = month_pairs(D, 1)
    PA, PB, _, _ = month_pairs(D, 1, days=range(1, 29))
    # triples for steps: a, b(+1 month), c(+2 months)
    ix = {d: i for i, d in enumerate(D)}; A, B, Cc = [], [], []
    for (y, m) in sorted(set((d.year, d.month) for d in D)):
        for d in range(1, 29):
            ds = []
            for k in range(3):
                yy, mm_ = y + (m - 1 + k) // 12, (m - 1 + k) % 12 + 1
                ds.append(ix.get(dt.date(yy, mm_, d)))
            if None not in ds: A.append(ds[0]); B.append(ds[1]); Cc.append(ds[2])
    tri = {"3mo": (np.array(A), np.array(B), np.array(Cc))}
    obs = stats(c.CLS_IDX[x], n, mp, tri)
    sims = [stats(c.CLS_IDX[shuffle_within_year(x, bounds, rg)], n, mp, tri) for _ in range(NSH)]
    print(gname, "done sims", flush=True)
    for nm in ("T", "W"):
        arr = np.array([s[nm] for s in sims])
        for gi, g in enumerate(G):
            z = (obs[nm][gi] - arr[:, gi].mean()) / arr[:, gi].std()
            pair_rows.append([gname, nm, g, int(obs[nm][gi]), float(arr[:, gi].mean()), float(arr[:, gi].std()), float(z), c.mc_p(obs[nm][gi], arr[:, gi], "two"), float(obs["Eind"][gi]) if nm == "T" else 0.0])
        tot_o = obs[nm].sum(); tot_s = arr.sum(1)
        rows.append([gname, "link pairs: %s summed over g=1..15" % nm, int(tot_o), float(tot_s.mean()), float(tot_s.std()), float((tot_o - tot_s.mean()) / tot_s.std()), c.mc_p(tot_o, tot_s, "two"), "ratio obs/shuffle %.3f; independence-adjusted ratio %.3f" % (tot_o / tot_s.mean(), tot_o / obs["Eind"].sum() if nm == "T" else 0)])
    for s_ in range(-3, 4):
        for j, nm in enumerate(["total same-class matches", "month-pairs with k>=3", "max k"]):
            arr = np.array([s["MM"][s_][j] for s in sims]); o = obs["MM"][s_][j]
            mm_rows.append([gname, s_, nm, o, float(arr.mean()), float(arr.std()), float((o - arr.mean()) / max(arr.std(), 1e-9)), c.mc_p(o, arr, "two")])
    for L in LS:
        key = "steps_3mo_L%d" % L
        for j, nm in enumerate(["common links (sum, 2 months)", "month-pairs >=2 common", "month-pairs >=3 common", "3-month triples >=2 common (full step design)", "max common in triple"]):
            arr = np.array([s[key][j] for s in sims]); o = obs[key][j]
            st_rows.append([gname, L, nm, o, float(arr.mean()), float(arr.std()), float((o - arr.mean()) / max(arr.std(), 1e-9)), c.mc_p(o, arr, "upper")])
c.save_csv("s4_link_pairs_by_gap.csv", ["game", "stat", "gap_g", "obs", "shuffle_mean", "shuffle_sd", "z", "p_two", "indep_expected"], pair_rows)
c.save_csv("s4_link_pairs_summary.csv", ["game", "stat", "obs", "shuffle_mean", "shuffle_sd", "z", "p_two", "note"], rows)
c.save_csv("s4_month_copy.csv", ["game", "shift_rows", "stat", "obs", "shuffle_mean", "shuffle_sd", "z", "p_two"], mm_rows)
c.save_csv("s4_steps_keyed.csv", ["game", "L", "stat", "obs", "shuffle_mean", "shuffle_sd", "z", "p_upper"], st_rows)
print("== link pair summary"); [print(r) for r in rows]
print("== month copy shift0"); [print(r) for r in mm_rows if r[1] == 0]
print("== steps"); [print(r) for r in st_rows]
