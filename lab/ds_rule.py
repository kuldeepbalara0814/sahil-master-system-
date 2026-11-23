"""008 DS Recency: DS ke pichle number dohrate hai (paper forward test + apne aap chalne wala kagaz ka khata).
Rule FROZEN: badla nahi jayega. Sirf paas ka data; kuch save nahi karta (rows se hi nikalta hai), isliye naya result aate hi apne aap update.
Do tarah: "one" = roz ek number (DS ka 2 din pehle wala), "four" = roz 4 number (DS ke 2,3,4,5 result pehle wale).
Imandari se: ye "mazboot dikhta hua asar" hai (research/recency/REPORT.md), pakka pattern nahi. Sirf paper.
"""
import datetime as dt

from . import data

START = dt.date(2026, 11, 24)        # forward test yahin se (isse pehle ka sab itihaas)
LAGS = (2, 3, 4, 5)                  # "four" rule; lag 1 (abhi nikla number) chhodte hain
MODES = {"one": (2,), "four": LAGS}
PAYOUT = 95                          # 40 se kam number par 95 guna
STAKE = 30                           # rupaye per number per din (user ne kaha: roz 30 Rs)
CAPITAL = 10000                      # kagaz ki shuruaati raqam
HORIZON = 90
BREAKEVEN = 1 / PAYOUT * 100         # % per number

RULES = [
    "Roz DS ke liye bet apne aap lagta hai (kagaz par). Aap ko kuch nahi karna.",
    "Rule 1 (roz ek number): DS ka jo number 2 result pehle aaya tha wahi aaj ka number. (Abhi nikla number, yaani 1 pehle wala, chhoda jata hai.)",
    "Rule 2 (roz 4 number): DS ke 2, 3, 4 aur 5 result pehle wale number (jo number do baar aaye wo ek hi gina jata hai).",
    f"Har number par roz Rs {STAKE}. Jeet par Rs {STAKE * PAYOUT} milte hai ({PAYOUT} guna). Haar par Rs {STAKE} jata hai.",
    f"Shuruaati kagaz ki raqam Rs {CAPITAL}. Har din ka munafa ya ghata is me judta-ghatta rehta hai.",
    "Mahine ka aakhri din chhuti hai, us din bet nahi hota. Rule beech me badla nahi jayega.",
    "Ek din me jeet aaye ya na aaye, rule roz chalta hai. Hit kam aata hai, isliye lambi haar normal hai.",
]


def numbers_for(rows, i, lags=LAGS):
    """rows[i] ka DS pehle se: rows[i-k] ke DS (k in lags), alag-alag (duplicate hata ke). i = len(rows) ho to 'aaj' (abhi bina row)."""
    if i - max(lags) < 0:
        return []
    out = []
    for k in lags:
        x = int(rows[i - k][1][3])
        if x not in out:
            out.append(x)
    return out


def _tally(items):
    stakes = sum(x["stakes"] for x in items)
    hits = sum(1 for x in items if x["hit"])
    return stakes, hits


def _ledger(rows, lags, lo, hi=None):
    """Khata: rows[lo:hi] ke har din ka bet, jeet/haar aur chalta balance (CAPITAL se)."""
    out, bal = [], CAPITAL
    for i in range(lo, hi if hi is not None else len(rows)):
        nums = numbers_for(rows, i, lags)
        ds = int(rows[i][1][3])
        hit = ds in nums
        cost = len(nums) * STAKE
        win = STAKE * PAYOUT if hit else 0
        bal += win - cost
        out.append({"date": rows[i][0].isoformat(), "numbers": nums, "ds": ds, "hit": hit, "stakes": len(nums), "bet": cost, "win": win, "net": win - cost, "balance": bal})
    return out


def _summary(led):
    stakes, hits = _tally(led)
    bet = sum(x["bet"] for x in led)
    win = sum(x["win"] for x in led)
    streak = 0
    for x in reversed(led):
        if x["hit"]:
            break
        streak += 1
    longest = cur = 0
    for x in led:
        cur = 0 if x["hit"] else cur + 1
        longest = max(longest, cur)
    low = min((x["balance"] for x in led), default=CAPITAL)
    return {"days": len(led), "stakes": stakes, "hits": hits, "bet": bet, "win": win, "net": win - bet, "balance": CAPITAL + win - bet,
            "rate": None if not stakes else round(100 * hits / stakes, 2), "roi": None if not bet else round(100 * (win - bet) / bet, 1),
            "streak": streak, "longest": longest, "lowest": low}


def view(rows):
    N = len(rows)
    play = data.play_date(rows)
    first = next((i for i in range(N) if rows[i][0] >= START), N)
    modes = {}
    for key, lags in MODES.items():
        led = _ledger(rows, lags, first)
        s = _summary(led)
        today = numbers_for(rows, N, lags)
        prev_lo = max(max(lags), first - 350)                   # START se pehle ke ~350 din: "agar ye rule chalta"
        hist = _summary(_ledger(rows, lags, prev_lo, first)) if first > prev_lo else None
        modes[key] = {"lags": list(lags), "today": {"date": play.isoformat(), "numbers": today, "bet": len(today) * STAKE, "win_if_hit": STAKE * PAYOUT},
                      **s, "ledger": led[-40:][::-1], "past_year": hist}
    four = modes["four"]
    stakes = four["stakes"]
    exp = round(stakes * 0.0137, 1)
    verdict = (f"{stakes} stake par asli rate ke hisaab se lagbhag {exp} hit aane chahiye, random me ~{round(stakes * 0.0105, 1)}. "
               "Itne kam hit se asli aur random me farak pakadna mushkil hai (R&D: 90 din me faisla nahi ho sakta, kam se kam kai saal chahiye). Isliye ise sirf lambe samay ka hisaab maano; rule mat badlo.")
    ref = []
    for i in range(N):
        if rows[i][0] >= dt.date(2022, 1, 1):
            nums = numbers_for(rows, i)
            ref.append({"stakes": len(nums), "hit": int(rows[i][1][3]) in nums})
    rs, rh = _tally(ref)
    return {"start": START.isoformat(), "play_date": play.isoformat(), "today": modes["four"]["today"] | {"stakes": len(modes["four"]["today"]["numbers"])},
            "rule": "DS ke 2, 3, 4, 5 result pehle wale 4 number (exact, palat nahi), roz",
            "days": four["days"], "horizon": HORIZON, "left": max(0, HORIZON - four["days"]), "stakes": stakes, "hits": four["hits"],
            "rate": four["rate"], "random": 1.0, "breakeven": round(BREAKEVEN, 2), "roi": four["roi"], "streak": four["streak"], "longest": four["longest"],
            "history": [{"date": x["date"], "numbers": x["numbers"], "ds": x["ds"], "hit": x["hit"]} for x in four["ledger"][:30]],
            "ref": {"since": "2022-01-01", "stakes": rs, "hits": rh, "rate": round(100 * rh / rs, 2) if rs else None},
            "verdict": verdict, "modes": modes, "rules": RULES, "stake": STAKE, "payout": PAYOUT, "capital": CAPITAL,
            "warning": "Ye sirf paper hai. Hit ~17 din me ek aata hai, 100+ din tak bina hit bhi ho sakta hai, aur ek saal -39% se +57% gaya hai. 90 din (~360 stake, ~5 hit) me faisla nahi hota; asli aur random ka farak dikhne me ~5 saal lagte hai. Asli paisa lagane ki salah nahi."}


def mark_flags(ser):
    """DS chart par rang: ser = [(tarikh, number)] row-wise. -> {tarikh: 2 (roz-1 rule se hit, wo 4 me bhi), 1 (sirf roz-4 rule se hit)}. Naya result aate hi aage apne aap."""
    flags = {}
    k = max(LAGS)
    for i in range(k, len(ser)):
        v = ser[i][1]
        if v in {ser[i - l][1] for l in LAGS}:
            flags[ser[i][0]] = 2 if v == ser[i - 2][1] else 1
    return flags
