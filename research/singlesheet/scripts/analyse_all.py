"""Collect all parts -> CSVs in out/ and out/headline.json. usage: analyse_all.py  (after all parts have run)"""
import os, csv, json, warnings
import numpy as np
from common import OUT, Y0
from stats import *
warnings.filterwarnings("ignore")
GAMES = ["FB", "GB", "GL", "DS"]
HL = {}

def wcsv(name, rows):
    if not rows: return
    with open(os.path.join(OUT, name), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

def cfg_rows(game, part, cfgs, r, minn=30, extra=None):
    out = []
    for i, c in enumerate(cfgs):
        if r["n"][i] < minn: continue
        d = dict(game=game, part=part, cfg=str(c), n=int(r["n"][i]), hits=int(r["hit"][i]), exp=round(float(r["exp"][i]), 1),
                 lift=round(float(r["lift"][i]), 3), lo=round(float(r["lift_lo"][i]), 3), hi=round(float(r["lift_hi"][i]), 3),
                 z=round(float(r["z"][i]), 2), p=round(float(r["p"][i]), 4), size=round(float(r["size"][i]), 2))
        if extra: d.update(extra)
        out.append(d)
    return out

def eras(game):
    return ERAS_DS if game == "DS" else ERAS_13

def run_scan(game, part, S, cfgs, minn_elig=200):
    """overall + era + FWER; returns rows, headline"""
    r = zscan(S)
    elig = r["n"] >= minn_elig
    mx, pf = fwer(r, elig)
    hl = dict(game=game, part=part, R=int(S.shape[0] - 1), ncfg=len(cfgs), elig=int(elig.sum()), maxz=float(mx) if mx == mx else None, fwer_p=float(pf) if pf == pf else None,
              frac_z2_real=float((r["z"][elig] > 2).mean()) if elig.any() else None,
              frac_z2_shuf=float((r["zs"][:, elig] > 2).mean()) if elig.any() else None,
              mean_z_real=float(r["z"][elig].mean()) if elig.any() else None)
    return r, hl

all_rows = []
for game in GAMES:
    # ---------- part 1
    for scheme in ("month", "block30"):
        fn = os.path.join(OUT, f"p1_{game}_{scheme}.npz")
        if not os.path.exists(fn): continue
        z = np.load(fn, allow_pickle=True); S = z["S"]; D = z["D"]; cfgs = list(z["cfgs"]); dcfgs = list(z["dcfgs"])
        r, hl = run_scan(game, f"p1_{scheme}", S, cfgs); HL[f"{game}_p1_{scheme}"] = hl
        rows = cfg_rows(game, f"p1_{scheme}", cfgs, r, 30)
        # per era z for every cfg
        for e, a, b in eras(game):
            re = zscan(S, a, b)
            for i, c in enumerate(cfgs):
                for x in rows:
                    if x["cfg"] == str(c): x[f"z_{e}"] = round(float(re["z"][i]), 2); x[f"lift_{e}"] = round(float(re["lift"][i]), 3)
        wcsv(f"p1_{game}_{scheme}.csv", rows); all_rows += rows
        # design existence
        Dt = D.sum(2)                       # R+1, dcfg, 2 (with design, triples)
        frac = Dt[:, :, 0] / np.maximum(Dt[:, :, 1], 1)
        drows = []
        for i, c in enumerate(dcfgs):
            sh = frac[1:, i]
            drows.append(dict(game=game, scheme=scheme, cfg=str(c), triples=int(Dt[0, i, 1]), real_frac=round(float(frac[0, i]), 4), shuf_mean=round(float(sh.mean()), 4),
                              shuf_sd=round(float(sh.std(ddof=1)), 4), z=round(float((frac[0, i] - sh.mean()) / sh.std(ddof=1)), 2) if sh.std() > 0 else 0))
        wcsv(f"p1_design_exist_{game}_{scheme}.csv", drows)
    # ---------- part 2,3
    for part in ("p2", "p3"):
        fn = os.path.join(OUT, f"{part}_{game}.npz")
        if not os.path.exists(fn): continue
        z = np.load(fn, allow_pickle=True); S = z["S"]; cfgs = list(z["cfgs"])
        r, hl = run_scan(game, part, S, cfgs, 100); HL[f"{game}_{part}"] = hl
        rows = cfg_rows(game, part, cfgs, r, 20)
        wcsv(f"{part}_{game}.csv", rows); all_rows += rows
    # ---------- part 4
    fn = os.path.join(OUT, f"p4_{game}.npz")
    if os.path.exists(fn):
        z = np.load(fn, allow_pickle=True); S = z["S"]; cfgs = list(z["pcfgs"]); FQ = z["FQ"]; fc = list(z["fcfgs"])
        r, hl = run_scan(game, "p4_predict", S, cfgs, 100); HL[f"{game}_p4"] = hl
        rows = cfg_rows(game, "p4_predict", cfgs, r, 20)
        wcsv(f"p4_{game}.csv", rows); all_rows += rows
        T = FQ.sum(2)                       # run, cfg, 3 (windows, windows>=1, count)
        fr = []
        for i, c in enumerate(fc):
            a = T[:, i, 1] / np.maximum(T[:, i, 0], 1); m = T[:, i, 2] / np.maximum(T[:, i, 0], 1)
            sd = a[1:].std(ddof=1)
            fr.append(dict(game=game, cfg=str(c), windows=int(T[0, i, 0]), frac_real=round(float(a[0]), 4), frac_shuf=round(float(a[1:].mean()), 4), z_frac=round(float((a[0] - a[1:].mean()) / sd), 2) if sd > 0 else 0,
                           mean_cnt_real=round(float(m[0]), 4), mean_cnt_shuf=round(float(m[1:].mean()), 4)))
        wcsv(f"p4_freq_{game}.csv", fr)
    # ---------- part 5
    fn = os.path.join(OUT, f"p5_{game}.npz")
    if os.path.exists(fn):
        z = np.load(fn, allow_pickle=True); R = z["R"]; H = z["H"]
        T = R.sum(3)                        # run, link, chain, 3
        rr = []
        for li, lk in enumerate(("palat", "rashi")):
            for ch, nm in enumerate(("S12 vs S23 (design span)", "T tightest 2-link span month vs next month")):
                for k, kn in ((1, "equal"), (2, "within1")):
                    n = T[:, li, ch, 0]; v = T[:, li, ch, k] / np.maximum(n, 1)
                    sd = v[1:].std(ddof=1)
                    rr.append(dict(game=game, link=lk, chain=nm, stat=kn, pairs=int(n[0]), real=round(float(v[0]), 4), shuf_mean=round(float(v[1:].mean()), 4), shuf_sd=round(float(sd), 4),
                                   z=round(float((v[0] - v[1:].mean()) / sd), 2) if sd > 0 else 0, p_two=round(float((1 + (np.abs(v[1:] - v[1:].mean()) >= abs(v[0] - v[1:].mean())).sum()) / (len(v))), 4)))
        wcsv(f"p5_{game}.csv", rr)
        hist = [dict(game=game, link=lk, L=L, real=int(H[0, li, L]), shuf_mean=round(float(H[1:, li, L].mean()), 1)) for li, lk in enumerate(("palat", "rashi")) for L in range(3, 17)]
        wcsv(f"p5_hist_{game}.csv", hist)
wcsv("all_cfg_rows.csv", all_rows)
json.dump(HL, open(os.path.join(OUT, "headline.json"), "w"), indent=1)
for k, v in HL.items(): print(k, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in v.items() if a not in ("game", "part")})
