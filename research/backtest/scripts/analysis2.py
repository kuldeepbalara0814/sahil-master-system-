"""Persistence, ensemble, shuffle-null, headline tables. Usage: python analysis2.py"""
import os, glob, math, json
import numpy as np
import pandas as pd
from analysis import load, prep, stat, halves, by_year, variants, table, CACHE, OUT, NMIN, EMIN

DEFAULTS = {"copy": "shape=all game=all", "family": "shape=all size=all all", "naksha": "L=all top12 all", "naksha2": "L=all top12 all",
            "dana": "kind=all all core window=sd", "steps": "L=all links=all top8", "tokri": "window=365d top6"}


def zc(h, p, month):
    d = h - p
    cl = pd.Series(d).groupby(np.asarray(month)).sum()
    se = math.sqrt((cl ** 2).sum()) or 1e-9
    return round((h.sum() - p.sum()) / se, 2)


# ------------------------------------------------------------------ persistence
def persistence(df, pat, maxlag=3):
    """df: ek pattern ke records (t,id,hit,p,month). Map jo pichle 1-3 din me (usi id se) aaya aur hit hua vs jo hit nahi hua vs naya."""
    d = df[df.pat == pat][["t", "id", "hit", "p", "month"]].copy()
    d = d.drop_duplicates(["t", "id"])
    hit = {(r.t, r.id): r.hit for r in d.itertuples()}
    g1, g3 = [], []
    for r in d.itertuples():
        prev = [hit.get((r.t - k, r.id)) for k in range(1, maxlag + 1)]
        seen = [x for x in prev if x is not None]
        y = hit.get((r.t - 1, r.id))
        g1.append("new" if y is None else ("hit_yday" if y else "nohit_yday"))
        g3.append("new" if not seen else ("hit_3d" if any(seen) else "nohit_3d"))
    d["g1"], d["g3"] = g1, g3
    rows = []
    for col in ("g1", "g3"):
        for grp, x in d.groupby(col):
            rows.append({"pat": pat, "window": col, "group": grp, "n": len(x), "hit_rate": round(x.hit.mean(), 4), "random_rate": round(x.p.mean(), 4),
                         "lift": round(x.hit.sum() / x.p.sum(), 3) if x.p.sum() else np.nan, "z": zc(x.hit, x.p, x.month)})
    return rows


def autocorr(df, pat):
    """Din ka standardized excess (hit - p) ka lag-1 correlation (sirf lagatar din)."""
    d = df[df.pat == pat]
    day = d.groupby("t").apply(lambda x: pd.Series({"ex": (x.hit - x.p).sum() / math.sqrt(max((x.p * (1 - x.p)).sum(), 1e-9))}), include_groups=False)
    ts = day.index.values
    s = pd.Series(day.ex.values, index=ts)
    prev = s.reindex(ts - 1)
    m = ~np.isnan(prev.values)
    if m.sum() < 20:
        return {"pat": pat, "pairs": int(m.sum()), "lag1_corr": np.nan, "se": np.nan}
    r = np.corrcoef(s.values[m], prev.values[m])[0, 1]
    return {"pat": pat, "pairs": int(m.sum()), "lag1_corr": round(float(r), 3), "se": round(1 / math.sqrt(m.sum()), 3)}


def persist_all(tag):
    light, heavy = load(tag, "light"), load(tag, "heavy")
    rows, ac = [], []
    for pat, src in (("naksha", heavy), ("naksha2", heavy), ("stepsD", heavy), ("danaD", light)):
        if src is None:
            continue
        rows += persistence(src, pat)
    for pat, src in (("naksha", heavy), ("naksha2", heavy), ("stepsD", heavy), ("danaD", light), ("copy", light), ("family", light)):
        if src is not None:
            ac.append(autocorr(src, pat))
    return pd.DataFrame(rows), pd.DataFrame(ac)


# ------------------------------------------------------------------ ensemble
def ensemble(tag):
    e = pd.read_csv(os.path.join(CACHE, f"{tag}_ens.csv.gz"))
    day = e[e.n == -1].set_index("t")["hit"]          # us din ke alag-alag number kitne aaye
    v = e[e.n >= 0].copy()
    v["votes"] = v[["v_nak", "v_nak2", "v_fam", "v_copy", "v_dana", "v_steps"]].sum(axis=1)
    v["score"] = v["votes"] + v["tok"]
    v["month"] = v["date"].str[:7]
    v["base"] = v["t"].map(day) / 100.0
    days = sorted(day.index)
    rows = []

    def bucket(name, sub):
        E = sub.base.sum()
        H = sub.hit.sum()
        rows.append({"bucket": name, "n": len(sub), "hit_rate": round(H / max(len(sub), 1), 4), "random_rate": round(E / max(len(sub), 1), 4),
                     "lift": round(H / E, 3) if E else np.nan, "z": zc(sub.hit, sub.base, sub.month) if len(sub) else np.nan})
    # zero-vote numbers: har din 100 - voted
    ndays = len(days)
    voted = v.groupby("t").size()
    zero_n = int((100 - voted.reindex(days).fillna(0)).sum())
    zero_h = float((day.reindex(days) - v.groupby("t").hit.sum().reindex(days).fillna(0)).sum())
    zero_E = float(((100 - voted.reindex(days).fillna(0)) * day.reindex(days) / 100).sum())
    rows.append({"bucket": "votes=0 (koi map nahi)", "n": zero_n, "hit_rate": round(zero_h / zero_n, 4), "random_rate": round(zero_E / zero_n, 4), "lift": round(zero_h / zero_E, 3), "z": np.nan})
    for nm, lo, hi in (("votes=1", 1, 1), ("votes=2", 2, 2), ("votes=3", 3, 3), ("votes=4-5", 4, 5), ("votes=6-8", 6, 8), ("votes=9-14", 9, 14), ("votes>=15", 15, 999)):
        bucket(nm, v[(v.votes >= lo) & (v.votes <= hi)])
    bucket("tokri number (baar)", v[v.tok == 1])
    bucket("tokri + votes>=3", v[(v.tok == 1) & (v.votes >= 3)])
    for col, nm in (("v_nak", "naksha"), ("v_nak2", "naksha2"), ("v_fam", "family"), ("v_copy", "copy"), ("v_dana", "dana"), ("v_steps", "steps")):
        bucket(f"{nm} vote>=1", v[v[col] >= 1])
    # rank-style: har din top-K number (score, phir votes) -- Number Rank list
    for K in (1, 3, 5, 10, 20):
        top = v.sort_values(["t", "score", "votes", "n"], ascending=[True, False, False, True]).groupby("t").head(K)
        bucket(f"top{K} per day (score)", top)
    # zyada vote wale numbers me kitne alag (voted > ...)
    return pd.DataFrame(rows), len(days)


# ------------------------------------------------------------------ shuffle null
def null_runs():
    tags = sorted({os.path.basename(f).rsplit("_", 1)[0] for f in glob.glob(os.path.join(CACHE, "shuf*_light.csv.gz"))})
    res = []
    for tg in tags:
        if tg == "real":
            continue
        light, heavy = load(tg, "light"), load(tg, "heavy")
        t = table(variants(light, heavy))
        t["tag"] = tg
        res.append(t)
    return pd.concat(res) if res else pd.DataFrame()


def max_test(real_t, null_t):
    """Har pattern aur sab milake: asli me sabse bada z (eligible variant) vs shuffle me sabse bade z ka distribution."""
    out = []
    pats = list(real_t.pat.unique()) + ["ALL"]
    for pat in pats:
        r = real_t[real_t.eligible & ((real_t.pat == pat) | (pat == "ALL"))]
        if not len(r):
            continue
        zr = r.z.max()
        lr = r.loc[r.z.idxmax(), "variant"]
        nulls = []
        for tg, g in null_t.groupby("tag"):
            gg = g[g.eligible & ((g.pat == pat) | (pat == "ALL"))]
            if len(gg):
                nulls.append(gg.z.max())
        nulls = np.array(nulls)
        K = len(r)
        out.append({"pat": pat, "K_variants": K, "best_variant": lr, "best_z": zr, "best_lift": r.loc[r.z.idxmax(), "lift"],
                    "bonferroni_p": min(1.0, K * 0.5 * math.erfc(zr / math.sqrt(2))) if zr > 0 else 1.0,
                    "null_runs": len(nulls), "null_max_z_median": round(float(np.median(nulls)), 2) if len(nulls) else np.nan,
                    "null_max_z_max": round(float(nulls.max()), 2) if len(nulls) else np.nan,
                    "perm_p": round((1 + (nulls >= zr).sum()) / (1 + len(nulls)), 3) if len(nulls) else np.nan})
    return pd.DataFrame(out)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    real = pd.read_csv(os.path.join(OUT, "variants_real.csv"))
    null_t = null_runs()
    null_t.to_csv(os.path.join(OUT, "variants_shuffle_all.csv.gz"), index=False)
    mt = max_test(real, null_t)
    mt.to_csv(os.path.join(OUT, "max_test.csv"), index=False)
    print(mt.to_string())
    # null calibration of default variants
    cal = []
    for pat, name in DEFAULTS.items():
        r = real[(real.pat == pat) & (real.variant == name)]
        g = null_t[(null_t.pat == pat) & (null_t.variant == name)] if len(null_t) else pd.DataFrame()
        cal.append({"pat": pat, "variant": name, "real_lift": r.lift.iloc[0] if len(r) else np.nan, "real_z": r.z.iloc[0] if len(r) else np.nan,
                    "shuf_runs": len(g), "shuf_lift_mean": round(g.lift.mean(), 3) if len(g) else np.nan, "shuf_lift_sd": round(g.lift.std(), 3) if len(g) else np.nan,
                    "shuf_z_mean": round(g.z.mean(), 2) if len(g) else np.nan, "shuf_z_sd": round(g.z.std(), 2) if len(g) else np.nan})
    cal = pd.DataFrame(cal)
    cal.to_csv(os.path.join(OUT, "default_vs_shuffle.csv"), index=False)
    print(cal.to_string())
    # persistence
    pr_real, ac_real = persist_all("real")
    pr_real.to_csv(os.path.join(OUT, "persistence_real.csv"), index=False)
    ac_real.to_csv(os.path.join(OUT, "autocorr_real.csv"), index=False)
    print(pr_real.to_string()); print(ac_real.to_string())
    # persistence on one shuffled run (null)
    tg = sorted({os.path.basename(f).rsplit("_", 1)[0] for f in glob.glob(os.path.join(CACHE, "shuf_*_heavy.csv.gz"))})
    if tg:
        pn, an = persist_all(tg[0])
        pn.to_csv(os.path.join(OUT, "persistence_shuffle1.csv"), index=False)
        an.to_csv(os.path.join(OUT, "autocorr_shuffle1.csv"), index=False)
    en, nd = ensemble("real")
    en.to_csv(os.path.join(OUT, "ensemble_real.csv"), index=False)
    print(en.to_string())
    if tg:
        e2, _ = ensemble(tg[0])
        e2.to_csv(os.path.join(OUT, "ensemble_shuffle1.csv"), index=False)
