"""Idea ka backtest: aaj tak ke result par dekho ki idea chalta ya nahi.

Idea (spec) ek chhota dict hai:
  mode     "rule" (kisi pichle result se number banao) | "hot" (pichle N din me sabse zyada aaye) | "cold" (sabse der se nahi aaya)
  sources  [{"game":"GB","lag":1}]   lag 1 = kal (pichla kaam ka din), 0 = aaj ke pehle wale game
  value    None ya number  -> sirf tab bet jab source me ye number aaye
  base     "source" | "fixed" (fixed me "fixed":[..] numbers)
  ops      ["same","palat","plus1","minus1","family","dost3"]   source number se kaun kaun se number lagane hain
  on       ["FD","GB"..]   kin games me lagana hai
  days     None ya [0..6] (Somvar=0)
  window, topk   hot/cold ke liye
Har number par Rs5. Payout 95 guna (40 se kam number) ya 90 guna. Koi bhi bet sirf us din tak ke data se banti hai (aage ka data nahi dekhta).
"""
import datetime as dt
import math

import numpy as np

from . import data, monitor, picks

GAMES = data.GAMES                      # FD GB GL DS
STAKE = 5
RANDOM = 0.01
BE95 = data.BREAKEVEN_95
MAX_LAG = 7


def palat(n):
    return (n % 10) * 10 + n // 10


class History:
    """Result array + tez lookup (kisi bhi din tak ka hot/cold/dost)."""

    def __init__(self, rows):
        self.rows = rows
        self.N = len(rows)
        self.dates = [r[0] for r in rows]
        self.R = np.array([r[1] for r in rows], dtype=np.int16) if rows else np.zeros((0, 4), dtype=np.int16)
        adj = [False] * self.N                         # adj[i]: row i-1 aur i adjacent
        for i in range(1, self.N):
            adj[i] = data.adjacent(self.dates[i - 1], self.dates[i])
        self.adj = adj
        self.chain = [0] * self.N                      # i tak lagatar adjacent kitne piche tak
        for i in range(1, self.N):
            self.chain[i] = self.chain[i - 1] + 1 if adj[i] else 0
        cs = np.zeros((self.N + 1, 100), dtype=np.int32)    # sab 4 games ki cumulative ginti
        for i in range(self.N):
            cs[i + 1] = cs[i]
            for g in range(4):
                cs[i + 1, self.R[i, g]] += 1
        self.cs = cs

    def lag_ok(self, i, lag):
        return i - lag >= 0 and self.chain[i] >= lag


class DostWalk:
    """Har checkpoint par 'tab tak ke data' se dost table (aage ka data nahi)."""

    def __init__(self, h, step=30, k=10):
        self.h, self.step, self.k = h, step, k
        self.C = np.zeros((100, 100), dtype=np.int64)
        self.kk = np.zeros(100, dtype=np.int64)
        self.seen = np.zeros(100, dtype=np.int64)
        self.done = 0
        self.cp = -1
        self.table = None

    def _advance(self, upto):
        h = self.h
        while self.done < upto - 1:                  # window poora: row done aur done+1 dono jaanti hon
            j = self.done
            if h.adj[j + 1]:
                R, R2 = h.R[j].tolist(), h.R[j + 1].tolist()
                for g in range(4):
                    x = R[g]
                    w = R[g + 1:] + R2
                    self.seen[x] += 1
                    self.kk[x] += len(w)
                    for y in set(w):
                        if y != x:
                            self.C[x, y] += 1
            self.done += 1

    def top(self, i, x, k):
        cp = i // self.step
        if cp != self.cp:
            self._advance(i)
            tog = self.C + self.C.T
            exp = (self.kk[:, None] + self.kk[None, :]) / 100.0
            z = (tog - exp) / np.sqrt(np.maximum(exp, 1e-9))
            self.table, self.zz, self.cp = tog, z, cp
        tog, z = self.table[x].copy(), self.zz[x]
        tog[x] = 0
        order = np.lexsort((np.arange(100), -z, -tog))
        return [int(y) for y in order if tog[y] > 0][:k]


def known(src_game, lag, tgt):
    """Kya ye source target game ke time tak pata hota hai?"""
    gi, ti = GAMES.index(src_game), GAMES.index(tgt)
    return lag >= 1 or gi < ti


def numbers_for(h, spec, i, t, dost):
    """Din i, game t (index) par spec se kaun se number lagenge."""
    mode = spec.get("mode", "rule")
    if mode == "hot":
        w = int(spec.get("window", 30))
        if i < w:
            return []
        c = h.cs[i] - h.cs[i - w]
        order = np.lexsort((np.arange(100), -c))
        return [int(x) for x in order[: int(spec.get("topk", 10))] if c[x] > 0]
    if mode == "cold":
        last = np.full(100, -1, dtype=np.int64)
        lo = max(0, i - 400)
        for j in range(lo, i):
            last[h.R[j, t]] = j
        order = np.lexsort((np.arange(100), last))        # sabse purana pehle
        return [int(x) for x in order[: int(spec.get("topk", 10))]]
    vals = []
    if spec.get("base") == "fixed":
        vals = [int(v) for v in spec.get("fixed", [])]
    else:
        for s in spec.get("sources", []):
            lag = int(s.get("lag", 1))
            if not known(s["game"], lag, GAMES[t]) or not h.lag_ok(i, lag):
                return []
            vals.append(int(h.R[i - lag, GAMES.index(s["game"])]))
        if spec.get("value") is not None:
            vals = [v for v in vals if v == int(spec["value"])]
    out = set()
    for v in vals:
        for op in spec.get("ops") or ["same"]:
            if op == "same":
                out.add(v)
            elif op == "palat":
                out.add(palat(v))
            elif op == "plus1":
                out.add((v + 1) % 100)
            elif op == "minus1":
                out.add((v - 1) % 100)
            elif op == "family":
                out |= picks.family(v)
            elif op.startswith("dost"):
                out |= set(dost.top(i, v, int(op[4:] or 3)))
    return sorted(out)


def run(rows, spec):
    """Poora backtest. Wapas: dict (summary, years, games, parts, recent, today)."""
    h = History(rows)
    targets = [GAMES.index(g) for g in spec.get("on", ["FD"])]
    days = spec.get("days")
    uses_dost = any(op.startswith("dost") for op in (spec.get("ops") or []))
    dost = DostWalk(h) if uses_dost else None
    start = max(30, int(spec.get("window", 30)) + 1) if spec.get("mode") in ("hot",) else 30
    bets = []                                   # (i, t, n, hit)
    for i in range(start, h.N):
        if days is not None and h.dates[i].weekday() not in days:
            continue
        for t in targets:
            nums = numbers_for(h, spec, i, t, dost)
            if not nums:
                continue
            bets.append((i, t, len(nums), 1 if int(h.R[i, t]) in nums else 0))
    out = {"bets": len(bets)}
    out.update(analyse(h, bets))
    out["today"] = today(h, spec, targets, DostWalk(h) if uses_dost else None)
    return out


def _stats(h, sel):
    n_bets = len(sel)
    trials = sum(b[2] for b in sel)
    hits = sum(b[3] for b in sel)
    cost = sum(b[2] * STAKE for b in sel)
    ret = sum(STAKE * (95 if b[2] < 40 else 90) * b[3] for b in sel)
    hit = hits / trials if trials else 0.0
    lo, hi = monitor.wilson(hits, trials)
    return {"bets": n_bets, "numbers": trials, "hits": hits, "hit_pct": hit, "ci_low": lo, "ci_high": hi,
            "cost": cost, "net": ret - cost, "roi": (ret - cost) / cost if cost else 0.0,
            "avg_n": trials / n_bets if n_bets else 0.0}


def analyse(h, bets):
    allb = _stats(h, bets)
    if not bets:
        return {"summary": allb, "years": [], "games": {}, "parts": {}, "recent": {}, "verdict": verdict(allb, None, None)}
    last = h.dates[-1]
    cut = bets[int(len(bets) * 0.7)][0]
    seekha = [b for b in bets if b[0] < cut]
    parakha = [b for b in bets if b[0] >= cut]
    y1 = dt.date(last.year - 1, last.month, min(last.day, 28))
    m3 = (last.replace(day=1) - dt.timedelta(days=62)).replace(day=1)
    r12 = [b for b in bets if h.dates[b[0]] > y1]
    r3 = [b for b in bets if h.dates[b[0]] >= m3]
    years = []
    for y in sorted({h.dates[b[0]].year for b in bets}):
        s = _stats(h, [b for b in bets if h.dates[b[0]].year == y])
        s["year"] = y
        years.append(s)
    games = {GAMES[t]: _stats(h, [b for b in bets if b[1] == t]) for t in sorted({b[1] for b in bets})}
    parts = {"seekha": _stats(h, seekha), "parakha": _stats(h, parakha),
             "seekha_range": [h.dates[seekha[0][0]].isoformat(), h.dates[seekha[-1][0]].isoformat()] if seekha else None,
             "parakha_range": [h.dates[parakha[0][0]].isoformat(), h.dates[parakha[-1][0]].isoformat()] if parakha else None}
    recent = {"last12m": _stats(h, r12), "last3m": _stats(h, r3)}
    z = (allb["hits"] - allb["numbers"] * RANDOM) / math.sqrt(max(allb["numbers"] * RANDOM * (1 - RANDOM), 1e-9))
    allb["z"] = z
    return {"summary": allb, "years": years, "games": games, "parts": parts, "recent": recent,
            "verdict": verdict(allb, parts["parakha"], recent["last12m"])}


def verdict(s, parakha, r12):
    """Seedha Hinglish faisla. Teen rang: hara / peela / laal (ya kam data)."""
    if s["bets"] < 300:
        return {"color": "kam", "title": "Kam data", "text": f"Sirf {s['bets']} bet bani. 300 se kam par kuch pakka nahi kah sakte."}
    be, rnd = BE95, RANDOM
    pk = parakha["hit_pct"] if parakha else 0
    rc = r12["hit_pct"] if r12 and r12["bets"] >= 60 else None
    if s["ci_low"] > rnd and pk >= be and (rc is None or rc >= be):
        return {"color": "hara", "title": "Kuch dum lag raha hai",
                "text": "Poore data me, baad ke hisse me aur pichle 12 mahine me - teeno me break-even se upar. Phir bhi paper trading me kuch din parakh ke hi bharosa karo."}
    if s["hit_pct"] >= be and pk >= rnd:
        return {"color": "peela", "title": "Thoda asar, par pakka nahi",
                "text": "Poore data me break-even ke upar hai, par ya to range random ko chhoo rahi hai ya baad ka hissa kamzor hai. Chhota fayda ho sakta hai, tez utar-chadhav ke saath."}
    return {"color": "laal", "title": "Dum nahi (random jaisa)",
            "text": "Ye idea 13 saal ke data me break-even (1.05%) tak nahi pahunchta, ya baad ke hisse me gir jaata hai. Paper par bhi isse fayda nahi dikhta."}


def today(h, spec, targets, dost):
    """Agli khelne ki tarikh par idea kya lagayega (jahan source pata hai)."""
    i = h.N
    out = {}
    last = h.dates[-1]
    play = data.play_date(h.rows) if h.N else last
    days = spec.get("days")
    for t in targets:
        g = GAMES[t]
        if days is not None and play.weekday() not in days:
            out[g] = {"numbers": [], "why": "Is din ke liye idea nahi (din ka filter)"}
            continue
        if spec.get("mode", "rule") == "rule" and spec.get("base") != "fixed" and any(int(s.get("lag", 1)) == 0 for s in spec.get("sources", [])):
            nums = []                                  # aaj ke pehle wale game ka result abhi pata nahi
        else:
            nums = numbers_for(_Extended(h), spec, i, t, dost)
        if nums:
            out[g] = {"numbers": nums}
        else:
            why = "Pehle wale game ka result aane ke baad" if any(
                int(s.get("lag", 1)) == 0 for s in spec.get("sources", [])) else "Abhi koi bet nahi bani"
            out[g] = {"numbers": [], "why": why}
    out["play_date"] = play.isoformat()
    return out


class _Extended:
    """History jisme ek 'aaj' ka din (anjaana) jud gaya - sirf lag>=1 sources aur hot/cold ke liye."""

    def __init__(self, h):
        self._h = h
        self.N = h.N + 1
        self.R = np.vstack([h.R, np.zeros((1, 4), dtype=np.int16)])
        self.cs = np.vstack([h.cs, h.cs[-1:]])
        self.chain = h.chain + [h.chain[-1] + 1 if h.N else 0]
        self.adj = h.adj + [True]
        self.dates = h.dates + [h.dates[-1] + dt.timedelta(days=1)]

    def lag_ok(self, i, lag):
        return i - lag >= 0 and self.chain[i] >= lag
