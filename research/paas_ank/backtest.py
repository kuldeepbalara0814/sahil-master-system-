"""Paas-ank pattern ka backtest (user ka logic, 25 Nov 2026).

Trigger: kisi bhi game (FB/GB/GL/DS) ka number jiske dono ank me 1 ka fark ho (non-circular: 01,10,12,21,...,89,98).
Tokri S: us number ke ank {a,b}: wo sab number jinka pehla ank a/b ho YA doosra ank a/b ho (36 jodi).
Window: trigger ke baad agle 4 draw (FB->GB->GL->DS ke kram me, agle din samet). PASS: kisi draw ka number S me.
Tulna: (1) random (36% har draw: 1-0.64^4 = 83.2%), (2) control trigger (ank paas-paas nahi, tokri utni hi), (3) saal-ke-andar shuffle.
Kharcha: har step par S ki har jodi Rs 1, pehla hit aate hi ruk jao, 95x. Ye sirf research, paper.
"""
import csv, math, sys
import numpy as np

rows = list(csv.DictReader(open("data/results.csv")))
dates = [r["date"] for r in rows]
years = np.array([int(d[:4]) for d in dates])
M = np.array([[int(r["fd"]), int(r["gb"]), int(r["gl"]), int(r["ds"])] for r in rows])
N_ROWS = len(rows)
W = 4
PAY = 95


def analyse(M, mask_fn, years_flat, lo=None, hi=None, nonoverlap=False):
    """M: (rows,4). -> dict stats. mask_fn(t,u) -> bool array (trigger)."""
    x = M.reshape(-1)
    t, u = x // 10, x % 10
    n = len(x)
    trig = mask_fn(t, u)
    idx = np.nonzero(trig)[0]
    idx = idx[idx + W < n]
    if lo is not None:
        idx = idx[(years_flat[idx] >= lo) & (years_flat[idx] <= hi)]
    if nonoverlap:                                                  # window chalu ho to naya trigger nahi
        keep, nxt = [], -1
        for i in idx:
            if i >= nxt:
                keep.append(i)
                nxt = i + W + 1
        idx = np.array(keep, dtype=int)
    a, b = t[idx], u[idx]
    hit = np.zeros((len(idx), W), dtype=bool)
    for k in range(1, W + 1):
        j = idx + k
        tj, uj = t[j], u[j]
        hit[:, k - 1] = (tj == a) | (tj == b) | (uj == a) | (uj == b)
    passed = hit.any(1)
    first = np.where(passed, hit.argmax(1) + 1, 0)
    steps = np.where(passed, first, W)
    spent = 36.0 * steps
    win = np.where(passed, PAY, 0.0)
    roi = (win.sum() - spent.sum()) / spent.sum() if len(idx) else 0.0
    gidx = idx % 4
    return {"n": len(idx), "pass": int(passed.sum()), "rate": passed.mean() if len(idx) else 0.0, "roi": roi, "first": first, "idx": idx, "passed": passed, "gidx": gidx}


consec = lambda t, u: np.abs(t - u) == 1
consec_circ = lambda t, u: (np.abs(t - u) == 1) | (np.abs(t - u) == 9)
control = lambda t, u: (np.abs(t - u) >= 2) & (np.abs(t - u) <= 8)           # ank alag, par paas-paas nahi (tokri phir bhi 36)
years_flat = np.repeat(years, 4)
BASE = 1 - 0.64 ** W


def wilson(p, n, z=1.96):
    if n == 0:
        return (0, 0)
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - r) / d, (c + r) / d)


def line(label, s):
    lo, hi = wilson(s["rate"], s["n"])
    z = (s["rate"] - BASE) / math.sqrt(BASE * (1 - BASE) / max(1, s["n"]))
    print(f"{label:34s} trigger {s['n']:5d}  pass {s['pass']:5d} = {100*s['rate']:5.2f}%  (95% {100*lo:5.2f}-{100*hi:5.2f})  random {100*BASE:.1f}%  z {z:+5.2f}  ROI {100*s['roi']:+6.1f}%")


print("data:", dates[0], "->", dates[-1], f"({N_ROWS} din, {N_ROWS*4} draw)")
print(f"random: har draw 36%, 4 draw me pass = {100*BASE:.1f}%; har step 36 jodi par 95x => expected ROI = {100*(0.36*95/36-1):+.1f}%\n")
A = analyse(M, consec, years_flat)
C = analyse(M, control, years_flat)
Ci = analyse(M, consec_circ, years_flat)
line("PAAS-ANK trigger (sab)", A)
line("  circular (09,90 bhi)", Ci)
line("CONTROL (ank paas nahi, tokri 36)", C)
line("PAAS-ANK, window overlap nahi", analyse(M, consec, years_flat, nonoverlap=True))
print("\n-- pehle kis step me pass (paas-ank):", {k: int((A['first'] == k).sum()) for k in range(0, 5)}, "(0 = fail)")
print("   random ke hisaab se step 1/2/3/4 par pehla pass %:", [round(100 * 0.64 ** (k - 1) * 0.36, 1) for k in range(1, 5)], "fail", round(100 * 0.64 ** 4, 1))
print("   asli %:", [round(100 * (A['first'] == k).mean(), 1) for k in range(1, 5)], "fail", round(100 * (A['first'] == 0).mean(), 1))

print("\n-- hisse (discovery 2013-19 / holdout 2020-26):")
for lo, hi, lab in ((2013, 2019, "2013-19"), (2020, 2026, "2020-26")):
    line(f"PAAS-ANK {lab}", analyse(M, consec, years_flat, lo, hi))
    line(f"CONTROL  {lab}", analyse(M, control, years_flat, lo, hi))
print("\n-- saal-dar-saal (paas-ank pass%, control pass%, ROI%):")
for y in range(2013, 2027):
    a, c = analyse(M, consec, years_flat, y, y), analyse(M, control, years_flat, y, y)
    print(f"  {y}: paas-ank {a['n']:4d} trig {100*a['rate']:5.1f}% ROI {100*a['roi']:+5.1f}% | control {100*c['rate']:5.1f}% ROI {100*c['roi']:+5.1f}%")
print("\n-- trigger kis game me aaya (paas-ank):")
for g, nm in enumerate(("FB", "GB", "GL", "DS")):
    m = A["gidx"] == g
    r = A["passed"][m].mean()
    print(f"  {nm}: trigger {m.sum():4d}  pass {100*r:5.2f}%")

# ---- shuffle (saal ke andar, har game ka column alag) null
rng = np.random.default_rng(7)
nulls_rate, nulls_roi = [], []
for _ in range(300):
    Ms = M.copy()
    for y in np.unique(years):
        ix = np.nonzero(years == y)[0]
        for g in range(4):
            Ms[ix, g] = Ms[rng.permutation(ix), g]
    s = analyse(Ms, consec, years_flat)
    nulls_rate.append(s["rate"]); nulls_roi.append(s["roi"])
nr, no = np.array(nulls_rate), np.array(nulls_roi)
print(f"\n-- 300 shuffle (saal-ke-andar): pass% mean {100*nr.mean():.2f} (min {100*nr.min():.2f}, max {100*nr.max():.2f}) | ROI% mean {100*no.mean():+.1f} (max {100*no.max():+.1f})")
print(f"   asli pass {100*A['rate']:.2f}%  -> shuffle se zyada wale: {(nr >= A['rate']).sum()}/300 ; asli ROI {100*A['roi']:+.1f}% -> shuffle se zyada: {(no >= A['roi']).sum()}/300")

# ---- A-only (andar, 20 number) aur B-only (bahar) alag
def part(which):
    x = M.reshape(-1); t, u = x // 10, x % 10; n = len(x)
    idx = np.nonzero(consec(t, u))[0]; idx = idx[idx + W < n]
    a, b = t[idx], u[idx]; ok = np.zeros(len(idx), bool)
    for k in range(1, W + 1):
        tj, uj = t[idx + k], u[idx + k]
        ok |= ((tj == a) | (tj == b)) if which == "A" else ((uj == a) | (uj == b))
    return ok.mean()
print(f"\n-- sirf A (andar, 20 jodi): pass {100*part('A'):.2f}% (random {100*(1-0.8**4):.1f}%) | sirf B (bahar, 20 jodi): pass {100*part('B'):.2f}% (random {100*(1-0.8**4):.1f}%)")

# ---- paise ka hisaab (Rs 1 har jodi): kitne step, kitna kharcha, saal bhar me net
steps = np.where(A["first"] > 0, A["first"], W)
spent = 36.0 * steps
win = np.where(A["passed"], float(PAY), 0.0)
years_span = (N_ROWS / 365.25)
print(f"\n-- paise (Rs 1 har jodi, pehla hit par ruk jao): avg {steps.mean():.2f} step/trigger, kharcha Rs {spent.mean():.1f}/trigger, net Rs {(win-spent).mean():+.2f}/trigger")
print(f"   trigger/saal {A['n']/years_span:.0f} -> net/saal Rs {(win-spent).sum()/years_span:+.0f} (Rs 1/jodi); Rs 10/jodi par {(win-spent).sum()/years_span*10:+.0f}")
print(f"   random me wahi: net/trigger Rs {-0.05*spent.mean():+.2f} (ROI -5%) -> saal me Rs {-0.05*spent.sum()/years_span:+.0f} (Rs 1/jodi)")
