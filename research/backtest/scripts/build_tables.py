"""Light cache se final tables: default per-pattern, saal-wise, set-size bucket, persistence, max-test. Output ../out/tables_light.md + Excel.
Usage: python analysis3_light.py (pehle) phir python build_tables.py"""
import os, math, numpy as np, pandas as pd
from analysis import load, prep, stat, by_year, OUT
from analysis2 import persistence, autocorr, DEFAULTS
real = pd.read_csv(os.path.join(OUT, "variants_real.csv"))
real = real[real.pat.isin(["copy", "family", "dana", "tokri"])].copy()
mt = pd.read_csv(os.path.join(OUT, "max_test_light.csv"))
nt = pd.read_csv(os.path.join(OUT, "variants_shuffle_light.csv.gz"))
L = []
# 1 default
d = real[[(r.pat in DEFAULTS and r.variant == DEFAULTS[r.pat]) for r in real.itertuples()]].copy()
d["break_even_cell_%"] = np.where(d.avg_set < 40, 100 / 95, 100 / 90).round(3)
cal = pd.read_csv(os.path.join(OUT, "default_vs_shuffle_light.csv"))
d = d.merge(cal[["pat", "shuf_lift_mean", "shuf_z_sd", "shuf_z_max", "runs"]], on="pat", how="left")
cols = ["pat", "variant", "n", "avg_set", "hit_rate", "random_rate", "lift", "lift_lo", "lift_hi", "z", "lift_h1", "lift_h2", "roi_%", "roi_se_%", "cell_win_%", "break_even_cell_%", "shuf_lift_mean", "shuf_z_max", "runs"]
T1 = d[cols]
# 2 top variants by z + set size buckets
el = real[real.eligible].copy()
el["size_bucket"] = pd.cut(el.avg_set, [0, 2.5, 4.5, 8, 1000], labels=["<=2.5", "2.5-4.5", "4.5-8", ">8"])
T2 = el.sort_values("z", ascending=False).head(20)[["pat", "variant", "n", "avg_set", "random_rate", "hit_rate", "lift", "lift_lo", "lift_hi", "z", "lift_h1", "lift_h2", "roi_%"]]
T3 = el.sort_values(["size_bucket", "lift"], ascending=[True, False]).groupby("size_bucket", observed=True).head(4)[["size_bucket", "pat", "variant", "n", "avg_set", "lift", "lift_lo", "lift_hi", "z", "roi_%"]]
# 3 saal-wise
yrs = []
fl = load("real", "light")
for pat, kind, sub in (("dana", "farak", "core"), ("dana", "gap", "core"), ("dana", "same", "core"), ("family", None, None), ("copy", None, None)):
    x = fl[fl.pat == pat]
    if kind: x = x[(x.kind == kind) & (x["sub"] == sub)]
    f = prep(x)
    for y, v in by_year(f).items():
        yrs.append({"pat": pat + (":" + kind if kind else ""), "year": y, "n": v[0], "lift": v[1]})
T4 = pd.DataFrame(yrs).pivot(index="pat", columns="year", values="lift")
# 4 persistence (light)
pr = []
fd = fl.copy()
for pat in ("dana", "family", "copy"):
    pr += persistence(fd, pat)
T5 = pd.DataFrame(pr)
T6 = pd.DataFrame([autocorr(fd, p) for p in ("dana", "family", "copy")])
for nm, t in (("1 default asli vs random vs shuffle", T1), ("2 top z variants", T2), ("3 kam set par lift (set-size bucket)", T3), ("4 saal-wise lift", T4.reset_index()), ("5 max-test (multiple testing)", mt), ("6 persistence hit-map", T5), ("7 autocorr", T6)):
    L.append(f"## {nm}\n\n" + t.to_markdown(index=False) + "\n")
open(os.path.join(OUT, "tables_light.md"), "w").write("\n".join(L))
with pd.ExcelWriter("/sdcard/Download/Research_backtest_summary.xlsx") as w:
    for nm, t in (("default", T1), ("top_z", T2), ("kam_set", T3), ("saal", T4.reset_index()), ("max_test", mt), ("persistence", T5), ("autocorr", T6), ("all_variants", real)):
        t.to_excel(w, sheet_name=nm, index=False)
print("ok")
