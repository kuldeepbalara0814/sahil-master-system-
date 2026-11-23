"""008 DS Recency: DS ke 2,3,4,5 result pehle wale 4 exact number (paper forward test, 90 din). Rule FROZEN hai: badla nahi jayega.
Sirf paas ka data; kuch save nahi karta (rows se hi nikalta hai), isliye naya result aate hi apne aap update.
Imandari se: ye "mazboot dikhta hua asar" hai (research/recency/REPORT.md), pakka pattern nahi. Sirf paper.
"""
import datetime as dt

from . import data

START = dt.date(2026, 11, 24)        # forward test yahin se (isse pehle ka sab itihaas)
LAGS = (2, 3, 4, 5)                  # lag 1 (abhi nikla number) chhodte hain
PAYOUT = 95                          # 40 se kam number par 95 guna
HORIZON = 90
BREAKEVEN = 1 / PAYOUT * 100         # % per number


def numbers_for(rows, i):
    """rows[i] ka DS pehle se: rows[i-2..i-5] ke DS, alag-alag (duplicate hata ke). i = len(rows) ho to 'aaj' (abhi bina row)."""
    if i - max(LAGS) < 0:
        return []
    out = []
    for k in LAGS:
        x = int(rows[i - k][1][3])
        if x not in out:
            out.append(x)
    return out


def _tally(items):
    stakes = sum(x["stakes"] for x in items)
    hits = sum(1 for x in items if x["hit"])
    return stakes, hits


def view(rows):
    N = len(rows)
    play = data.play_date(rows)
    hist = []
    for i in range(N):
        d = rows[i][0]
        if d < START:
            continue
        nums = numbers_for(rows, i)
        ds = int(rows[i][1][3])
        hist.append({"date": d.isoformat(), "numbers": nums, "ds": ds, "hit": ds in nums, "stakes": len(nums)})
    stakes, hits = _tally(hist)
    streak = 0
    for x in reversed(hist):
        if x["hit"]:
            break
        streak += 1
    longest = cur = 0
    for x in hist:
        cur = 0 if x["hit"] else cur + 1
        longest = max(longest, cur)
    ref = []
    for i in range(N):
        if rows[i][0] >= dt.date(2022, 1, 1):
            nums = numbers_for(rows, i)
            ref.append({"stakes": len(nums), "hit": int(rows[i][1][3]) in nums})
    rs, rh = _tally(ref)
    today_nums = numbers_for(rows, N)
    rate = 100 * hits / stakes if stakes else None
    days = len(hist)
    if stakes < 300:
        verdict = "Abhi bahut kam data hai. Hit kam aata hai (lagbhag 17 din me ek), isliye jaldi kuch kehna theek nahi."
    elif rate is not None and rate >= BREAKEVEN * 1.1:
        verdict = "Abhi tak break-even ke upar, par ye lambi haar-jeet wala khel hai; 90 din tak rule mat badlo."
    else:
        verdict = "Abhi tak break-even ke aas-paas ya neeche. 90 din pure hone tak rule mat badlo, phir faisla."
    return {"start": START.isoformat(), "play_date": play.isoformat(), "today": {"date": play.isoformat(), "numbers": today_nums, "stakes": len(today_nums)},
            "rule": "DS ke 2, 3, 4, 5 result pehle wale 4 number (exact, palat nahi), roz",
            "days": days, "horizon": HORIZON, "left": max(0, HORIZON - days), "stakes": stakes, "hits": hits,
            "rate": None if rate is None else round(rate, 2), "random": 1.0, "breakeven": round(BREAKEVEN, 2),
            "roi": None if not stakes else round(100 * (hits * PAYOUT - stakes) / stakes, 1), "streak": streak, "longest": longest,
            "history": hist[-30:][::-1], "ref": {"since": "2022-01-01", "stakes": rs, "hits": rh, "rate": round(100 * rh / rs, 2) if rs else None},
            "verdict": verdict,
            "warning": "Ye sirf paper hai. Hit ~17 din me ek aata hai, 100+ din tak bina hit bhi ho sakta hai, aur ek saal -39% se +57% gaya hai. Asli paisa lagane ki salah nahi."}
