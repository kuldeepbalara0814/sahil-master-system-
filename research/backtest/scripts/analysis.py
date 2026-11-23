"""Cache (harness ka output) se: har pattern asli vs random, variant sweep, shuffle-control, max-test, persistence, ensemble.
Usage: python analysis.py   -> ../out/*.csv aur ../out/tables.md
"""
import os, sys, glob, math, json
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "..", "cache")
OUT = os.path.join(HERE, "..", "out")
NMIN = 100          # variant tabhi gina jab itne andaze ho
EMIN = 8            # aur random se itne pass ki ummeed


def load(tag, part):
    f = os.path.join(CACHE, f"{tag}_{part}.csv.gz")
    if not os.path.exists(f):
        return None
    d = pd.read_csv(f, dtype={"nums": str, "id": str, "sub": str, "strength": str, "ltype": str})
    d["month"] = d["date"].str[:7]
    d["year"] = d["date"].str[:4].astype(int)
    return d


def prep(d, mode="any"):
    """-> frame with columns hit,p,stake,wins,s,month,date (mode: any / loc / alt)."""
    d = d.copy()
    if mode == "loc":
        d = d[d["loc_n"].notna()]
        return pd.DataFrame({"hit": d["loc_hit"].astype(float), "p": d["loc_p"], "stake": d["loc_n"], "wins": d["loc_win"], "s": d["s"], "month": d["month"], "date": d["date"], "year": d["year"], "pay": 95.0})
    if mode == "alt":
        d = d[d["alt_cells"] > 0]
        p = 1 - (1 - d["s"] / 100.0) ** d["alt_cells"]
        return pd.DataFrame({"hit": (d["alt_cellhits"] > 0).astype(float), "p": p, "stake": d["s"] * d["alt_cells"], "wins": d["alt_cellhits"], "s": d["s"], "month": d["month"], "date": d["date"], "year": d["year"], "pay": np.where(d["s"] < 40, 95.0, 90.0)})
    return pd.DataFrame({"hit": d["hit"].astype(float), "p": d["p"], "stake": d["s"] * d["cells"], "wins": d["cellhits"], "s": d["s"], "month": d["month"], "date": d["date"], "year": d["year"], "pay": np.where(d["s"] < 40, 95.0, 90.0)})


def stat(f):
    n = len(f)
    if n == 0:
        return None
    H, E = f["hit"].sum(), f["p"].sum()
    var = (f["p"] * (1 - f["p"])).sum()
    d = f["hit"] - f["p"]
    cl = d.groupby(f["month"]).sum()
    se_c = math.sqrt((cl ** 2).sum()) or 1e-9
    z_n = (H - E) / math.sqrt(var) if var > 0 else 0.0
    z_c = (H - E) / se_c
    lift = H / E if E > 0 else float("nan")
    ret = (f["pay"] * f["wins"] - f["stake"])
    stake = f["stake"].sum()
    roi = ret.sum() / stake if stake else float("nan")
    rcl = ret.groupby(f["month"]).sum()
    roi_se = math.sqrt((rcl ** 2).sum()) / stake if stake else float("nan")
    return {"n": n, "avg_set": round(f["s"].mean(), 2), "hits": int(H), "hit_rate": round(H / n, 4), "random_hits": round(E, 1), "random_rate": round(E / n, 4),
            "lift": round(lift, 3), "lift_lo": round((H - 1.96 * se_c) / E, 3) if E > 0 else float("nan"), "lift_hi": round((H + 1.96 * se_c) / E, 3) if E > 0 else float("nan"),
            "z_naive": round(z_n, 2), "z": round(z_c, 2), "roi_%": round(100 * roi, 1), "roi_se_%": round(100 * roi_se, 1),
            "cell_win_%": round(100 * f["wins"].sum() / stake, 3) if stake else float("nan")}


def halves(f):
    """pehla / doosra half (tarikh ke median se) aur saal-wise lift."""
    if len(f) < 4:
        return {}
    med = sorted(f["date"])[len(f) // 2]
    a, b = f[f["date"] < med], f[f["date"] >= med]
    r = {}
    for nm, x in (("lift_h1", a), ("lift_h2", b)):
        E = x["p"].sum()
        r[nm] = round(x["hit"].sum() / E, 3) if E > 0 else float("nan")
    return r


def by_year(f):
    out = {}
    for y, x in f.groupby("year"):
        E = x["p"].sum()
        out[int(y)] = (len(x), round(x["hit"].sum() / E, 3) if E > 0 else float("nan"))
    return out


# ------------------------------------------------------------------ variant definitions
def variants(light, heavy):
    """-> list of dict(pat, name, frame(prep)). Sab variant jo hum aazmate hain (multiple-testing ka K yahi)."""
    V = []

    def add(pat, name, d, mode="any", dedupe=None):
        if d is None or len(d) == 0:
            return
        if dedupe:
            d = d.sort_values("t").drop_duplicates(dedupe, keep="first")
        V.append({"pat": pat, "name": name, "f": prep(d, mode)})

    # copy
    c = light[light.pat == "copy"] if light is not None else None
    if c is not None:
        for shp in ("seedha", "ulta", "all"):
            for g in (0, 1, 2, 3, "all"):
                d = c
                if shp != "all":
                    d = d[d["shape"] == shp]
                if g != "all":
                    d = d[d["g"] == g]
                add("copy", f"shape={shp} game={'FB GB GL DS'.split()[g] if g != 'all' else 'all'}", d)
    # family
    fm = light[light.pat == "family"] if light is not None else None
    if fm is not None:
        for shp in ("seedha", "ulta", "all"):
            for size in (8, 4, "all"):
                for amb in ("saaf", "confusion", "all"):
                    d = fm
                    if shp != "all":
                        d = d[d["shape"] == shp]
                    if size != "all":
                        d = d[d["kind"] == size]
                    if amb != "all":
                        d = d[d["amb"] == (1 if amb == "confusion" else 0)]
                    add("family", f"shape={shp} size={size} {amb}", d)
    # naksha, naksha2
    if heavy is not None:
        for pat in ("naksha", "naksha2"):
            h = heavy[heavy.pat == pat]
            for L in (10, 12, 15, 18, "all"):
                for k in (1, 3, 6, 12):
                    for stg in ("all", "theek+", "mazboot"):
                        d = h
                        if L != "all":
                            d = d[d["L"] == L]
                        d = d[d["rank"] <= k]
                        if stg == "theek+":
                            d = d[d["strength"].isin(["theek", "mazboot"])]
                        elif stg == "mazboot":
                            d = d[d["strength"] == "mazboot"]
                        add(pat, f"L={L} top{k} {stg}", d)
                        if stg == "all":
                            add(pat, f"L={L} top{k} {stg} [location-exact]", d, mode="loc")
    # dana
    dn = light[light.pat == "dana"] if light is not None else None
    if dn is not None:
        for kind in ("same", "farak", "gap", "all"):
            for amb in ("saaf", "confusion", "all"):
                for sub in ("core", "core+series"):
                    for win in ("sd", "strict"):
                        d = dn[dn["sub"] == sub]
                        if kind != "all":
                            d = d[d["kind"] == kind]
                        if amb != "all":
                            d = d[d["amb"] == (1 if amb == "confusion" else 0)]
                        add("dana", f"kind={kind} {amb} {sub} window={win}", d, mode="alt" if win == "strict" else "any")
    # steps (dedupe: ek link ek baar)
    if heavy is not None:
        st = heavy[heavy.pat == "steps"]
        for L in (8, 10, 12, "all"):
            for nl in (2, 3, 4, "all"):
                for rk in (3, 8, 24):
                    d = st
                    if L != "all":
                        d = d[d["L"] == L]
                    if nl == 4:
                        d = d[d["nlink"] >= 4]
                    elif nl != "all":
                        d = d[d["nlink"] == nl]
                    d = d[d["rank"] <= rk]
                    add("steps", f"L={L} links={nl if nl != 4 else '4+'} top{rk}", d, dedupe="id")
        for ind in ("yes", "no"):
            for lt in ("flat", "standing", "diag", "all"):
                d = st[st["rank"] <= 8]
                d = d[d["ind"] == (1 if ind == "yes" else 0)]
                if lt != "all":
                    d = d[d["ltype"] == lt]
                add("steps", f"indicator={ind} linktype={lt} top8", d, dedupe="id")
        for lt in ("flat", "standing", "diag"):
            add("steps", f"linktype={lt} top8 (any indicator)", st[(st["rank"] <= 8) & (st["ltype"] == lt)], dedupe="id")
    # tokri
    tk = light[light.pat == "tokri"] if light is not None else None
    if tk is not None:
        for days in (365, 730, 1095, 1825, 0):
            for k in (1, 2, 3, 4, 6, 8, 12):
                add("tokri", f"window={'all history' if days == 0 else str(days) + 'd'} top{k}", tk[(tk["L"] == days) & (tk["rank"] == k)])
    return V


def table(V, nmin=NMIN, emin=EMIN):
    rows = []
    for v in V:
        s = stat(v["f"])
        if s is None:
            continue
        s.update(pat=v["pat"], variant=v["name"], eligible=bool(s["n"] >= nmin and s["random_hits"] >= emin))
        s.update(halves(v["f"]))
        rows.append(s)
    return pd.DataFrame(rows)


def run_tag(tag):
    light, heavy = load(tag, "light"), load(tag, "heavy")
    return table(variants(light, heavy))


if __name__ == "__main__":
    t = run_tag("real")
    t.to_csv(os.path.join(OUT, "variants_real.csv"), index=False)
    print(t[t.eligible].sort_values("z", ascending=False).head(25)[["pat", "variant", "n", "avg_set", "hit_rate", "random_rate", "lift", "z", "roi_%"]].to_string())
