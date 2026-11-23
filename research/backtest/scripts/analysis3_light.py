"""Light-only: shuffle null + max-test + default calibration (heavy ke bina). Usage: python analysis3_light.py"""
import os, numpy as np, pandas as pd
from analysis2 import null_runs, max_test, DEFAULTS, OUT
real = pd.read_csv(os.path.join(OUT, "variants_real.csv"))
real = real[real.pat.isin(["copy","family","dana","tokri"])]
nt = null_runs(); nt.to_csv(os.path.join(OUT, "variants_shuffle_light.csv.gz"), index=False)
print("shuffle runs:", nt.tag.nunique())
mt = max_test(real, nt); mt.to_csv(os.path.join(OUT, "max_test_light.csv"), index=False); print(mt.to_string())
cal = []
for pat, name in DEFAULTS.items():
    r = real[(real.pat == pat) & (real.variant == name)]; g = nt[(nt.pat == pat) & (nt.variant == name)]
    if len(r):
        cal.append(dict(pat=pat, variant=name, real_lift=r.lift.iloc[0], real_z=r.z.iloc[0], runs=len(g), shuf_lift_mean=g.lift.mean(), shuf_z_mean=g.z.mean(), shuf_z_sd=g.z.std(), shuf_z_max=g.z.max()))
cal = pd.DataFrame(cal).round(3); cal.to_csv(os.path.join(OUT, "default_vs_shuffle_light.csv"), index=False); print(cal.to_string())
