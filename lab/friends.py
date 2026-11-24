"""Dost (saathi) numbers.

Dost = jo number kisi number ke aas-paas sabse zyada aata hai.
Window: x aane ke baad  ->  usi din ke baaki games  +  agle kaam ke din ke FD,GB,GL,DS.
Dono taraf ginti: (x ke baad y) + (y ke baad x).   Teen samay: poora, pichle 3 mahine, is mahina.
"""
import datetime as dt
import math

import numpy as np

from . import data

TIERS = ["green"] * 3 + ["yellow"] * 3 + ["orange"] * 4    # 10 dost: top 3 hara, beech 3 peela, last 4 narangi
PERIOD_NAMES = {"poora": "Poora (sab saal)", "last3m": "Pichle 3 mahine (is mahine samet)", "month": "Is mahina (chal raha)"}


def month_start(d, back=0):
    y, m = d.year, d.month - back
    while m <= 0:
        m += 12
        y -= 1
    return dt.date(y, m, 1)


def periods(rows):
    """{naam: since_date or None} - latest tarikh ke hisaab se."""
    last = rows[-1][0]
    return {"poora": None, "last3m": month_start(last, 2), "month": month_start(last, 0)}


def counts(rows, since=None):
    """C[x,y] = x ke window me y aane ki baar; kk[x] = window ki lambai ka jod; seen[x] = x kitni baar aaya."""
    C = np.zeros((100, 100), dtype=np.int32)
    kk = np.zeros(100, dtype=np.int64)
    seen = np.zeros(100, dtype=np.int64)
    for i in range(len(rows) - 1):
        d, R, _ = rows[i]
        d2, R2, _ = rows[i + 1]
        if since is not None and d < since:
            continue
        if not data.adjacent(d, d2):
            continue                        # window poora nahi
        for g in range(4):
            x = R[g]
            w = R[g + 1:] + R2
            seen[x] += 1
            kk[x] += len(w)
            for y in set(w):
                if y != x:
                    C[x, y] += 1
    return C, kk, seen


def pair_pct(cnt, x, y):
    """x aur y ke saath aane ka % (dono ke mauke me se)."""
    C, kk, seen = cnt
    trials = int(seen[x] + seen[y])
    return (int(C[x, y] + C[y, x]) / trials) if trials else 0.0


def top_friends(cnt, x, k=10):
    """x ke top-k dost. Sirf wahi jo kam se kam 1 baar saath aaye."""
    C, kk, seen = cnt
    out = []
    for y in range(100):
        if y == x:
            continue
        tog = int(C[x, y] + C[y, x])
        if tog == 0:
            continue
        trials = int(seen[x] + seen[y])
        exp = float(kk[x] + kk[y]) / 100.0
        z = (tog - exp) / math.sqrt(max(exp, 1e-9))
        out.append(dict(n=y, together=tog, after=int(C[x, y]), before=int(C[y, x]), trials=trials,
                        expected=round(exp, 2), pct=tog / trials if trials else 0.0,
                        random_pct=exp / trials if trials else 0.0, z=round(z, 2)))
    out.sort(key=lambda f: (-f["together"], -f["z"], f["n"]))
    out = out[:k]
    for i, f in enumerate(out):
        f["tier"] = TIERS[i] if i < len(TIERS) else "orange"
    return out


class Friends:
    """Teeno samay ki ginti ek baar banao, phir kisi bhi number ka table do."""

    def __init__(self, rows):
        self.rows = rows
        self.per = periods(rows)
        self.cnt = {name: counts(rows, since) for name, since in self.per.items()}

    def table(self, x, k=10):
        res = {}
        for name in self.per:
            res[name] = top_friends(self.cnt[name], x, k)
        base = {f["n"]: i for i, f in enumerate(res["poora"])}
        for name in ("last3m", "month"):
            for i, f in enumerate(res[name]):
                j = base.get(f["n"])
                f["change"] = "naya" if j is None else ("upar" if i < j else "neeche" if i > j else "wahi")
                ov = pair_pct(self.cnt["poora"], x, f["n"])
                f["overall_pct"] = ov
                f["boost"] = round(f["pct"] / ov, 2) if ov > 0 else None      # overall se kitna guna zyada
        for name in ("last3m", "month"):
            few = int(self.cnt[name][2][x]) < 8
            for f in res[name]:
                f["few"] = few                                              # bahut kam data ka nishaan
        for f in res["poora"]:
            f["change"] = "-"
        last = self.rows[-1]
        return {"number": x, "seen": {n: int(self.cnt[n][2][x]) for n in self.per},
                "last_date": last[0].isoformat(), "last_has": x in last[1],        # aakhri din ginti me nahi (uska agla din nahi aaya)
                "since": {n: (s.isoformat() if s else None) for n, s in self.per.items()}, "friends": res}

    def snapshot(self, k=3):
        """Har number ke top-k dost har samay ke liye (drift pakadne ke liye)."""
        snap = {"asof": self.rows[-1][0].isoformat(), "top": {}}
        for x in range(100):
            snap["top"][str(x)] = {n: [f["n"] for f in top_friends(self.cnt[n], x, k)] for n in self.per}
        return snap


def drift(prev, new):
    """Do snapshot ka farak: 'pehle 10 par 93 tha, ab 94'."""
    out = []
    if not prev:
        return out
    for x in range(100):
        for name in ("poora", "last3m", "month"):
            a = prev["top"].get(str(x), {}).get(name, [])
            b = new["top"].get(str(x), {}).get(name, [])
            if a and b and a[0] != b[0]:
                out.append(dict(number=x, period=name, old=a[0], new=b[0]))
    return out
