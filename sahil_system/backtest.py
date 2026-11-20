"""Backtest: har din ka predict vs agle din ka asli result, random se compare."""
import datetime
import math

import api
import step1_tokari, step2_evergreen, step3_universal, step4_magic
import step5_dayfix, step6_murda, step7_haruf, step8_baki, step9_monthtrend

MAGIC = [12, 23, 84, 96]


def _predict(hist, day_in, game_date, formula):
    today = datetime.date.fromisoformat(game_date)
    dates = sorted(d for d in hist if d <= day_in)
    murda = [x for d in dates[-3:] for x in hist[d]]
    ym = today.strftime("%Y-%m")
    month_nums = list({x for d, v in hist.items() if d <= day_in and d.startswith(ym) for x in v})
    scores = {}
    for jodi, base in step1_tokari.create_basket(hist[day_in]).items():
        t = base
        if "2" in formula: t += step2_evergreen.check_evergreen(jodi)[0]
        if "3" in formula: t += step3_universal.check_universal(jodi, today)[0]
        if "4" in formula: t += step4_magic.check_magic(jodi)[0]
        if "5" in formula: t += step5_dayfix.check_dayfix(jodi, today.weekday())[0]
        if "6" in formula: t += step6_murda.check_murda(jodi, murda)[0]
        if "7" in formula: t += step7_haruf.check_haruf(jodi, today, "Y", ["3", "0"])[0]
        if "8" in formula: t += step8_baki.check_baki(jodi, murda, MAGIC)[0]
        if "9" in formula: t += step9_monthtrend.check_monthtrend(jodi, month_nums)[0]
        scores[jodi] = t
    top = [j for j, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)][:30]
    return top[:4], top[4:14], top[14:30]


def _random_hit(k, distinct):
    """k number random chune to 'distinct' alag asli numbers me se koi ek aane ka chance."""
    return 1 - math.comb(100 - distinct, k) / math.comb(100, k)


def run(formula):
    hist = api.load_history()
    dates = sorted(hist)
    pairs = [(a, b) for a, b in zip(dates, dates[1:])
             if (datetime.date.fromisoformat(b) - datetime.date.fromisoformat(a)).days == 1]
    n = h4 = h14 = h30 = 0
    r4 = r14 = r30 = 0.0
    for a, b in pairs:
        l1, l2, l3 = _predict(hist, a, b, formula)
        actual = set(hist[b])
        m = len(actual)
        n += 1
        h4 += bool(actual & set(l1))
        h14 += bool(actual & set(l1 + l2))
        h30 += bool(actual & set(l1 + l2 + l3))
        r4 += _random_hit(4, m)
        r14 += _random_hit(14, m)
        r30 += _random_hit(30, m)
    pct = lambda x: round(100 * x / n, 1) if n else 0.0
    return {
        "formula": sorted(formula),
        "days": n,
        "from": pairs[0][0] if pairs else None,
        "to": pairs[-1][1] if pairs else None,
        "L1": {"hit": pct(h4), "random": pct(r4)},
        "L1L2": {"hit": pct(h14), "random": pct(r14)},
        "top30": {"hit": pct(h30), "random": pct(r30)},
        "note": "Hit = us din ke 4 asli me se koi ek list me aaya. Random = bina soche utne hi number chunne ka chance.",
    }
