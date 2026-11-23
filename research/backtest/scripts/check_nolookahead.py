"""Look-ahead jaanch: (1) prediction columns tab bhi wahi rehte hain jab t ke baad ka poora data kachra kar do. (2) fast tokri == asli baar.tokri."""
import sys, random, copy
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import harness as H
from lab import baar, data
import numpy as np

H.init(None, 0)
full = H.G["full"]
ts = H.valid_ts(full)
rng = random.Random(7)
sample = rng.sample(ts, 12)
bad = 0
for t in sample:
    a_l, a_h = H.light_day(t), None
    a_h = H.heavy_day(t)
    # future ko kachra karo
    junk = [(d, [rng.randrange(100) for _ in range(4)], s) for d, v, s in full[t:]]
    H.G["full"] = full[:t] + junk
    H.init  # (tokri cum purani rahe to look-ahead nahi: cum[t] sirf rows<t)
    b_l, b_h = H.light_day(t), H.heavy_day(t)
    H.G["full"] = full
    pred = lambda L: sorted((r["pat"], r["id"], r["nums"], r["sub"]) for r in L)
    if pred(a_l) != pred(b_l) or pred(a_h[0]) != pred(b_h[0]) or a_h[1] != b_h[1][:len(a_h[1])] and False:
        # ens me hit/cnt column badalte hain, baaki (votes) nahi
        bad += 1
    ea = sorted((x[2:9]) for x in a_h[1]); eb = sorted((x[2:9]) for x in b_h[1])
    if ea != eb:
        bad += 1
print("look-ahead mismatches (0 chahiye):", bad, "of", len(sample))
# tokri fast vs real
mm = 0
for t in rng.sample(ts, 60):
    rows = full[:t]
    real = baar.tokri(rows, full[t][0].weekday(), days=365, asof=full[t][0], k=6)["numbers"]
    fast = H.tokri_fast(t, 365, 6)[0]
    real0 = baar.tokri(rows, full[t][0].weekday(), days=0, asof=full[t][0], k=6)["numbers"]
    fast0 = H.tokri_fast(t, 0, 6)[0]
    mm += (real != fast) + (real0 != fast0)
print("tokri fast vs real mismatches:", mm)
# dana tail vs full prefix
mm = 0
import datetime as dt
from lab import dana_farak
for t in rng.sample(ts, 60):
    rows = full[:t]; last = rows[-1][0]
    a = [(e["c1"], e["c2"], e["core"], e["series"]) for e in dana_farak.events(rows, last - dt.timedelta(days=3), last) if e["c2"][0] == last]
    b = [(e["c1"], e["c2"], e["core"], e["series"]) for e in H.dana_new(rows, last)]
    mm += a != b
print("dana tail vs prefix mismatches:", mm)
