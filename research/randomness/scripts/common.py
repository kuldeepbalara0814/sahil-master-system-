"""Saanjha helper: data load, chi-square tail, normal tail, BH, class/rashi maps. scipy nahi, sirf numpy/math."""
import csv, math, os, datetime as dt, json
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "out"))
GAMES = ["FB", "GB", "GL", "DS"]
SEED = 20261123


def load(game):
    """(dates list[date], x int array). DS: line date (1966 se)."""
    p = os.path.join(ROOT, "data", "game_%s.csv" % game.lower())
    D, X = [], []
    with open(p, encoding="utf-8") as f:
        for r in csv.reader(f):
            if r[0] == "date":
                continue
            D.append(dt.date.fromisoformat(r[0])); X.append(int(r[1]))
    return D, np.array(X, dtype=np.int64)


def years(D):
    return np.array([d.year for d in D])


def pal(n):
    return (n % 10) * 10 + n // 10

CLS = np.array([min(n, pal(n)) for n in range(100)])            # class id = min(n, palat), 55 distinct
CLS_IDS = sorted(set(CLS.tolist()))
CLS_IDX = np.array([CLS_IDS.index(c) for c in CLS])              # 0..54
def _rashi(n):
    a, b = n // 10 % 5, n % 10 % 5
    return tuple(sorted((a, b)))
RASHIS = sorted(set(_rashi(n) for n in range(100)))
RASHI_IDX = np.array([RASHIS.index(_rashi(n)) for n in range(100)])   # 0..14
DOUBLE = np.array([n // 10 == n % 10 for n in range(100)])
HALF = np.array([(n // 10 - n % 10) % 10 == 5 or (n % 10 - n // 10) % 10 == 5 for n in range(100)])  # antar 5: 05 16 27 38 49 +palat

def exp_prob(idx_map, k):
    """har group ka uniform-number se expected probability."""
    c = np.bincount(idx_map, minlength=k).astype(float)
    return c / 100.0


# ---------- distributions ----------
def _gser(a, x):
    ap, s = a, 1.0 / a; d = s
    for _ in range(2000):
        ap += 1; d *= x / ap; s += d
        if abs(d) < abs(s) * 1e-14: break
    return s * math.exp(-x + a * math.log(x) - math.lgamma(a))

def _gcf(a, x):
    tiny = 1e-300
    b = x + 1 - a; c = 1 / tiny; d = 1 / b; h = d
    for i in range(1, 2000):
        an = -i * (i - a); b += 2
        d = an * d + b; d = tiny if abs(d) < tiny else d
        c = b + an / c; c = tiny if abs(c) < tiny else c
        d = 1 / d; de = d * c; h *= de
        if abs(de - 1) < 1e-14: break
    return math.exp(-x + a * math.log(x) - math.lgamma(a)) * h

def chi2_sf(x, df):
    """P(Chi2_df >= x)."""
    if x <= 0: return 1.0
    a, xx = df / 2.0, x / 2.0
    if xx < a + 1:
        return max(0.0, 1.0 - _gser(a, xx))
    return min(1.0, _gcf(a, xx))

def norm_sf(z):
    return 0.5 * math.erfc(z / math.sqrt(2))

def norm_2p(z):
    return math.erfc(abs(z) / math.sqrt(2))

def chi2_gof(counts, probs):
    """returns (stat, df, p). probs sum 1; groups with tiny expected merged not done (we keep E>=5 by design)."""
    counts = np.asarray(counts, float); n = counts.sum(); e = np.asarray(probs) * n
    m = e > 0
    st = float((((counts[m] - e[m]) ** 2) / e[m]).sum()); df = int(m.sum() - 1)
    return st, df, chi2_sf(st, df)

def chi2_indep(table):
    t = np.asarray(table, float); n = t.sum()
    e = np.outer(t.sum(1), t.sum(0)) / n
    m = e > 0
    st = float((((t[m] - e[m]) ** 2) / e[m]).sum())
    df = (int((t.sum(1) > 0).sum()) - 1) * (int((t.sum(0) > 0).sum()) - 1)
    return st, df, chi2_sf(st, df)

def bh(pvals, q=0.05):
    """Benjamini-Hochberg: kitne reject."""
    p = np.sort(np.asarray(pvals)); m = len(p)
    ok = np.nonzero(p <= q * (np.arange(1, m + 1) / m))[0]
    return int(ok.max() + 1) if len(ok) else 0

def mc_p(obs, sims, tail="upper"):
    """Monte-Carlo p with +1 correction."""
    sims = np.asarray(sims)
    if tail == "upper": k = (sims >= obs).sum()
    elif tail == "lower": k = (sims <= obs).sum()
    else:
        k = min((sims >= obs).sum(), (sims <= obs).sum()) * 2
    return float(min(1.0, (k + 1) / (len(sims) + 1)))

def ks_uniform_p(p):
    """KS test p-values ~ U(0,1); asymptotic."""
    p = np.sort(np.asarray(p)); n = len(p)
    d = max(np.max(np.arange(1, n + 1) / n - p), np.max(p - np.arange(0, n) / n))
    lam = (math.sqrt(n) + 0.12 + 0.11 / math.sqrt(n)) * d
    s = 0.0
    for k in range(1, 100):
        s += 2 * (-1) ** (k - 1) * math.exp(-2 * k * k * lam * lam)
    return float(min(1, max(0, s))), float(d)

def rng(tag=0):
    return np.random.default_rng(SEED + tag)

def save_json(name, obj):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False, default=float)

def save_csv(name, header, rows):
    import time
    for attempt in range(6):
        try:
            with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f); w.writerow(header)
                for r in rows: w.writerow([("%.6g" % v) if isinstance(v, float) else v for v in r])
            return
        except OSError:
            time.sleep(2)
    raise OSError("save_csv failed " + name)

def fmt_p(p):
    return "%.1e" % p if p < 1e-3 else "%.3f" % p


def load_all():
    """dict: FB GB GL DS DS13 (DS sirf 2013 se). value=(dates, x)."""
    out = {g: load(g) for g in GAMES}
    D, x = out["DS"]
    m = np.array([d >= dt.date(2013, 1, 1) for d in D])
    out["DS13"] = ([d for d, k in zip(D, m) if k], x[m])
    return out
