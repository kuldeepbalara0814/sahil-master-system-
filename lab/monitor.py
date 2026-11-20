"""Monitor: har strategy ka rolling hit % vs break-even. Asar ghat jaye to chetavani."""
import datetime as dt
import math

from . import data, picks

BE95 = data.BREAKEVEN_95


def wilson(h, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    p = h / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    w = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - w, c + w


def status(hit, bets):
    """hara = break-even se kaafi upar, peela = aas-paas, laal = neeche. bets kam ho to 'kam data'."""
    if bets < 300:
        return "kam data"
    r = hit / BE95
    return "hara" if r >= 1.10 else "peela" if r >= 0.95 else "laal"


def period_stats(res, sel):
    """res = [(date, game, hit, size)]  ->  per-number-per-game hit"""
    trials = sum(s for d, g, h, s in res if sel(d))
    hits = sum(1 for d, g, h, s in res if sel(d) and h)
    lo, hi = wilson(hits, trials)
    hit = hits / trials if trials else 0.0
    return {"trials": trials, "hits": hits, "hit_pct": hit, "ci_low": lo, "ci_high": hi,
            "roi95": 95 * hit - 1, "status": status(hit, trials)}


def health(rows):
    last = rows[-1][0]
    per = {"all": lambda d: True, "y2016": lambda d: d.year >= 2016,
           "last12m": lambda d: d > last - dt.timedelta(days=365),
           "last3m": lambda d: d > last - dt.timedelta(days=92),
           "last30d": lambda d: d > last - dt.timedelta(days=30)}
    runs = {"single": picks.walk_single(rows), "list10s": picks.walk(rows, picks.K_DEFAULT, sequential=False),
            "list10": picks.walk(rows, picks.K_DEFAULT, sequential=True)}
    out = {"asof": last.isoformat(), "breakeven": BE95, "strategies": {}, "alerts": []}
    for name, res in runs.items():
        out["strategies"][name] = {p: period_stats(res, sel) for p, sel in per.items()}
        s3 = out["strategies"][name]["last3m"]
        if s3["status"] == "laal":
            out["alerts"].append(f"{name}: pichle 3 mahine ka hit {100 * s3['hit_pct']:.2f}% break-even {100 * BE95:.2f}% se neeche hai")
    return out
