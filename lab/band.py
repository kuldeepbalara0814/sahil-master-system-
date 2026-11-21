"""Band rashi / band number: kitne din se (kisi bhi game me) nahi aaye.

Rashi = number ke har ank me 5 jodne se bani family (01 -> 01 10 15 51 56 65 60 06, 8 number; jodi rashi 11 -> 11 16 61 66, 4 number).
Cross aur half jodi alag rashi ki hoti hain. Kul 15 rashi: 10 (8 number) + 5 jodi rashi (4 number).
"""
from lab import data

ZONE_LO, ZONE_HI = 15, 30             # aap ke anusar 15 se 30 din band reh sakti hai, 1 mahine se zyada kam hota hai


def key(n):
    return tuple(sorted((n // 10 % 5, n % 10 % 5)))


RASHIS = {}
for _n in range(100):
    RASHIS.setdefault(key(_n), []).append(_n)


def label(nums):
    s = " ".join(f"{n:02d}" for n in nums)
    return s


def zone(days):
    return "kam" if days > ZONE_HI else ("zone" if days >= ZONE_LO else "chhota")


def status(rows, min_days=15):
    end = rows[-1][0]
    seen = {}
    for d, v, _ in rows:
        for n in v:
            seen[n] = d
    first = rows[0][0]
    rashis, numbers = [], []
    for k, nums in RASHIS.items():
        last = max((seen[n] for n in nums if n in seen), default=first)
        band = (end - last).days
        rashis.append({"rashi": f"{nums[0]:02d}", "kind": "jodi" if len(nums) == 4 else "rashi", "numbers": nums,
                       "band": band, "last": last.isoformat(), "zone": zone(band)})
    for n in range(100):
        last = seen.get(n, first)
        band = (end - last).days
        numbers.append({"n": n, "band": band, "last": last.isoformat(), "rashi": f"{RASHIS[key(n)][0]:02d}", "zone": zone(band)})
    rashis.sort(key=lambda x: (-x["band"], x["rashi"]))
    numbers.sort(key=lambda x: (-x["band"], x["n"]))
    return {"end": end.isoformat(), "min": min_days,
            "rashis": [x for x in rashis if x["band"] >= min_days], "closest": rashis[:3],
            "numbers": [x for x in numbers if x["band"] >= min_days]}


def history(rows, min_days=15):
    """Itihas: rashi min_days se band thi, uske baad agle din / 3 din / 5 din me khuli? (sirf pehle ka data dekh kar, har line par)."""
    out = {}
    L = len(rows)
    for size in (8, 4):
        a = n1 = n3 = n5 = 0
        for k, nums in RASHIS.items():
            if len(nums) != size:
                continue
            s = set(nums)
            pres = [bool(s & set(r[1])) for r in rows]
            run = 0
            for i in range(L - 5):
                if run >= min_days:
                    a += 1
                    n1 += pres[i]
                    n3 += any(pres[i:i + 3])
                    n5 += any(pres[i:i + 5])
                run = 0 if pres[i] else run + 1
        base = 100 * (1 - (1 - size / 100) ** 4)
        out[str(size)] = {"cases": a, "next1": round(100 * n1 / a, 1) if a else None, "next3": round(100 * n3 / a, 1) if a else None,
                          "next5": round(100 * n5 / a, 1) if a else None, "random1": round(base, 1)}
    return out
