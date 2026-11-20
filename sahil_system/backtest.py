"""Backtest: har din ka predict vs agle din ka asli result, random se compare.

Pass = us din ke 4 asli result (FD GB GL DS) me se koi ek list me aaya.
Random = bina soche utne hi number chunne par pass hone ka chance.
Note: engine ki lists me "00" ko 0 likha hai aur record me 100; dono ko ek maana gaya hai.
"""
import datetime
import math

import api
import step1_tokari, step2_evergreen, step3_universal, step4_magic
import step5_dayfix, step6_murda, step7_haruf, step8_baki, step9_monthtrend

MAGIC = [12, 23, 84, 96]
NAMES = {
    "2": "Evergreen", "3": "Universal (1-3 tarikh)", "4": "Magic", "5": "Day Fix",
    "6": "Murda", "7": "Haruf", "8": "Baki", "9": "Month Trend",
}
_cache = {}


def _bonus(f, j, today, murda, month_nums):
    if f == "2": return step2_evergreen.check_evergreen(j)[0]
    if f == "3": return step3_universal.check_universal(j, today)[0]
    if f == "4": return step4_magic.check_magic(j)[0]
    if f == "5": return step5_dayfix.check_dayfix(j, today.weekday())[0]
    if f == "6": return step6_murda.check_murda(j, murda)[0]
    if f == "7": return step7_haruf.check_haruf(j, today, "Y", ["3", "0"])[0]
    if f == "8": return step8_baki.check_baki(j, murda, MAGIC)[0]
    return step9_monthtrend.check_monthtrend(j, month_nums)[0]


def _days():
    """Har din ke liye: basket, har formula ka bonus, asli result. Record badalne par hi dobara bante hain."""
    hist = api.load_history()
    key = (len(hist), max(hist) if hist else "")
    if _cache.get("key") == key:
        return _cache["days"]
    dates = sorted(hist)
    days = []
    for a, b in zip(dates, dates[1:]):
        if (datetime.date.fromisoformat(b) - datetime.date.fromisoformat(a)).days != 1:
            continue
        today = datetime.date.fromisoformat(b)
        murda = [x for d in [d for d in dates if d <= a][-3:] for x in hist[d]]  # aakhri 3 din ke 12 result
        ym = today.strftime("%Y-%m")
        month_nums = list({x for d, v in hist.items() if d <= a and d.startswith(ym) for x in v})
        basket = step1_tokari.create_basket(hist[a])
        bonus = {f: {j: _bonus(f, j, today, murda, month_nums) for j in basket} for f in NAMES}
        days.append((a, b, basket, bonus, set(hist[b])))
    _cache.update(key=key, days=days)
    return days


def _top30(basket, bonus, formula):
    score = {j: base + sum(bonus[f][j] for f in formula) for j, base in basket.items()}
    ranked = [j for j, _ in sorted(score.items(), key=lambda x: x[1], reverse=True)][:30]
    return [100 if j == 0 else j for j in ranked]


def _random_hit(k, distinct):
    return 1 - math.comb(100 - distinct, k) / math.comb(100, k)


def run(formula):
    days = _days()
    n = len(days)
    hit = {4: 0, 14: 0, 30: 0}
    rnd = {4: 0.0, 14: 0.0, 30: 0.0}
    for a, b, basket, bonus, actual in days:
        top = _top30(basket, bonus, formula)
        for k in hit:
            hit[k] += bool(actual & set(top[:k]))
            rnd[k] += _random_hit(k, len(actual))
    pct = lambda x: round(100 * x / n, 1) if n else 0.0
    return {
        "formula": sorted(formula),
        "days": n,
        "from": days[0][0] if days else None,
        "to": days[-1][1] if days else None,
        "L1": {"hit": pct(hit[4]), "random": pct(rnd[4])},
        "L1L2": {"hit": pct(hit[14]), "random": pct(rnd[14])},
        "top30": {"hit": pct(hit[30]), "random": pct(rnd[30])},
        "note": "Hit = us din ke 4 asli me se koi ek list me aaya. Random = bina soche utne hi number chunne ka chance.",
    }


def report():
    """Har formula ki alag list (Tokari + sirf wahi formula), aur combination bhi."""
    rows = [("-", "Sirf Tokari", [])]
    rows += [(f, NAMES[f], [f]) for f in NAMES]
    rows += [("256", "Default 2+5+6", ["2", "5", "6"]), ("all", "Sab 2-9", list(NAMES))]
    out = []
    for fid, name, fs in rows:
        r = run(fs)
        out.append({"id": fid, "name": name, "L1": r["L1"], "L1L2": r["L1L2"], "top30": r["top30"]})
    first = run([])
    return {"days": first["days"], "from": first["from"], "to": first["to"], "rows": out,
            "note": first["note"] + " 90% ke liye random (~75%) se kaafi upar chahiye."}
