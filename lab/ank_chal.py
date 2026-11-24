"""009 Ank-Chal (naya pattern, 24 Nov 2026) - patterns/009_ank_chal/README.md

Niyam (bahut chhota):
  * Har game ka 2 draw pehle wala number lo. Uska ANDAR ank (dahai) aur BAHAR ank (ikayi) alag-alag.
  * Aaj usi game me wahi ank usi jagah (andar/andar, bahar/bahar) aaye to PASS.
  * Paper me sirf un line par dekho jahan 13 saal ka record break-even se upar ho (neeche PICKS).
    2026-11-24 ki jaanch ke hisaab se: DS andar, DS bahar, FB andar. (FB = app me FD.)

Kyun: 2013-2026 me 8 line ka average 11.21% hai (random 10%, 9.5x par break-even 10.53%).
Chuni hui 3 line 11.95% (2013-19: 12.13%, 2020-26: 11.76%) - yaani aage ke data par bhi tiki.

Ye module sirf PAAS ka data dekhta hai (aage ka kuch nahi). data.GAMES = (FD, GB, GL, DS).
"""
import datetime as dt
import math

from . import data

START = dt.date(2026, 11, 24)    # forward paper-test ki shuruat: iske baad ke din hi asli (aage ka) record. Isse pehle ka sab chuni hui line par in-sample hai.

GAMES = data.GAMES
LAG = 2
PAYOUT = 9.5
BREAKEVEN = 1 / PAYOUT          # 10.526%
PICKS = ((3, "andar"), (3, "bahar"), (0, "andar"))     # (game index, jagah)
NAMES = {0: "FB", 1: "GB", 2: "GL", 3: "DS"}
POS_HI = {"andar": "andar (dahai)", "bahar": "bahar (ikayi)"}


def ank(n, pos):
    return n // 10 if pos == "andar" else n % 10


def series(rows, gi, pos, lag=LAG):
    return [ank(r[1][gi], pos) for r in rows]


def next_ank(rows, gi, pos, lag=LAG):
    """Khelne wala ank: lag draw pehle wale number ka ank. Aaj ka koi result nahi dekha."""
    if len(rows) <= lag:
        return None
    return ank(rows[-lag][1][gi], pos)


def line_stats(rows, gi, pos, lag=LAG, start=None):
    a = series(rows, gi, pos, lag)
    hit = 0
    n = 0
    first = lag if start is None else max(lag, start)
    for i in range(first, len(a)):
        n += 1
        hit += a[i] == a[i - lag]
    rate = hit / n if n else 0.0
    z = (hit - n * 0.10) / math.sqrt(n * 0.10 * 0.90) if n else 0.0
    return {"hit": hit, "n": n, "rate": rate, "z": z, "roi": PAYOUT * rate - 1}


def stats(rows, lag=LAG):
    """Saari 8 line ka hisaab (report/card ke liye)."""
    out = {}
    for gi, g in enumerate(GAMES):
        for pos in ("andar", "bahar"):
            s = line_stats(rows, gi, pos, lag)
            s["pick"] = (gi, pos) in PICKS
            out[NAMES[gi] + ":" + pos] = s
    tot_h = sum(line_stats(rows, gi, pos, lag)["hit"] for gi, pos in PICKS)
    tot_n = sum(line_stats(rows, gi, pos, lag)["n"] for gi, pos in PICKS)
    out["PICKS"] = {"hit": tot_h, "n": tot_n, "rate": tot_h / tot_n if tot_n else 0,
                    "roi": PAYOUT * (tot_h / tot_n) - 1 if tot_n else 0,
                    "breakeven": BREAKEVEN, "picks": [(NAMES[g], p) for g, p in PICKS]}
    return out


def history(rows, lag=LAG, last=None):
    """Pichhle kuch din ka pass/fail (scoreboard ke liye). [(date, game, pos, ank, hit)]"""
    out = []
    for i in range(lag, len(rows)):
        if last is not None and i < len(rows) - last:
            continue
        for gi, pos in PICKS:
            want = ank(rows[i - lag][1][gi], pos)
            got = ank(rows[i][1][gi], pos)
            out.append((rows[i][0], NAMES[gi], pos, want, want == got))
    return out


def scoreboard(rows, days=90, lag=LAG):
    h = history(rows, lag, last=days)
    n = len(h)
    hit = sum(1 for x in h if x[4])
    return {"days": days, "bets": n, "hits": hit, "rate": hit / n if n else 0,
            "roi": PAYOUT * (hit / n) - 1 if n else 0, "breakeven": BREAKEVEN}


def item(rows, gi, pos, play_date):
    s = line_stats(rows, gi, pos)
    want = next_ank(rows, gi, pos)
    g = NAMES[gi]
    return {
        "id": "ank:%s:%s" % (g, pos),
        "kind": "ank",
        "end": play_date.isoformat(),
        "name": "Ank-%s-%s" % (g, POS_HI[pos].split()[0]),
        "status": "aaj",
        "strength": "theek" if s["z"] >= 2 else "kamzor",
        "ambiguous": False,
        "loc": [],
        "title": "%s ka %s ank: %d (%s se)" % (g, POS_HI[pos], want, "2 draw pehle"),
        "lines": [
            "Paper me dekho: %s me ank %d (%s). 9.5x par break-even 10.53%%." % (g, want, POS_HI[pos]),
            "13 saal: %d/%d = %.2f%% (ROI %+.1f%%, z %+.1f). Random 10%%." % (
                s["hit"], s["n"], 100 * s["rate"], 100 * s["roi"], s["z"]),
            "Pass: aaj %s me %s ank %d aaye. Fail: koi doosra ank." % (g, POS_HI[pos].split()[0], want),
        ],
        "ank_targets": [{"game": g, "ank": want, "pos": pos}],      # 'targets' nahi: wo poore number (00-99) ke liye hai (hit-log, Number Rank); ank ko wahan number ginna galat hoga
        "pattern": {"id": "009", "key": "ank", "naam": "Ank-Chal"},
    }


def forward(rows, lag=LAG):
    """START (24 Nov 2026) ke baad ka asli (aage ka) hisaab: chuni 3 line. Aaj ke din se pehle sab in-sample hai."""
    h = [x for x in history(rows, lag) if x[0] >= START]
    n = len(h)
    hit = sum(1 for x in h if x[4])
    return {"since": START.isoformat(), "bets": n, "hits": hit, "rate": hit / n if n else 0.0,
            "roi": PAYOUT * (hit / n) - 1 if n else 0.0, "breakeven": BREAKEVEN}


STAKE = 30          # kagaz ka khata: har ank par Rs 30 (DS rule 008 jaisa)
CAPITAL = 10000


def view(rows):
    """Active tab ka card: aaj ke ank, 8 line ki table, 90 din, aur START se kagaz ka khata (stateless: rows se hi nikalta hai)."""
    play = data.play_date(rows)
    today = [{"game": NAMES[gi], "pos": pos, "ank": next_ank(rows, gi, pos)} for gi, pos in PICKS]
    lines = []
    for gi in range(4):
        for pos in ("andar", "bahar"):
            s = line_stats(rows, gi, pos)
            hold = line_stats(rows, gi, pos, start=next((i for i, r in enumerate(rows) if r[0].year >= 2020), len(rows)))
            lines.append({"game": NAMES[gi], "pos": pos, "pick": (gi, pos) in PICKS, "hit": s["hit"], "n": s["n"], "rate": round(100 * s["rate"], 2),
                          "roi": round(100 * s["roi"], 1), "z": round(s["z"], 1), "rate_2020": round(100 * hold["rate"], 2)})
    led, bal = [], CAPITAL
    first = next((i for i, r in enumerate(rows) if r[0] >= START), len(rows))
    for i in range(max(first, LAG), len(rows)):
        day = {"date": rows[i][0].isoformat(), "bets": [], "net": 0}
        for gi, pos in PICKS:
            want, got = ank(rows[i - LAG][1][gi], pos), ank(rows[i][1][gi], pos)
            hit = want == got
            net = STAKE * PAYOUT - STAKE if hit else -STAKE
            day["bets"].append({"game": NAMES[gi], "pos": pos, "want": want, "got": got, "hit": hit})
            day["net"] += net
        bal += day["net"]
        day["balance"] = round(bal, 1)
        led.append(day)
    fw = forward(rows)
    return {"play_date": play.isoformat(), "start": START.isoformat(), "stake": STAKE, "capital": CAPITAL, "payout": PAYOUT,
            "breakeven": round(100 * BREAKEVEN, 2), "today": today, "lines": lines, "last90": scoreboard(rows, 90), "forward": fw,
            "balance": round(bal, 1), "ledger": led[-30:][::-1],
            "picks_rate": round(100 * stats(rows)["PICKS"]["rate"], 2),
            "warning": "Ye DS lag-2 number-repeat asar ka ank wala roop hai (alag naya signal nahi). Chuni hui line purane data par mili thi (2013-19 me chuni, 2020-26 me parakhi); asli sabut sirf 24 Nov 2026 se ka record. 9.5x par katauti/limit se asli fayda kam ho sakta hai; 9x par break-even 11.11%. 90 din me kuch sabit nahi hota."}


def scan(rows, asof=None):
    """scanner.py ke liye: aaj ke 3 item + card ka summary."""
    play = data.play_date(rows)
    items = [item(rows, gi, pos, play) for gi, pos in PICKS]
    sc = scoreboard(rows, 90)
    fw = forward(rows)
    return {
        "id": "009", "key": "ank", "naam": "Ank-Chal", "pushti": False,
        "about": "2 draw pehle wale number ka ank (andar/bahar) usi jagah aaye to PASS. Sirf un line par khelo "
                 "jahan 13 saal ka rate 10.53% se upar ho: DS andar, DS bahar, FB andar.",
        "items": items,
        "summary": "Pichhle 90 din: %d/%d pass (%.1f%%), break-even 10.53%%. 13 saal: %.2f%%. Asli forward record (%s se): %d/%d. "
                   "90 din me kuch sabit nahi hota; paper me 6-12 mahine dekho (9.5x par katauti/limit se asli fayda kam ho sakta hai)." % (
                       sc["hits"], sc["bets"], 100 * sc["rate"], 100 * stats(rows)["PICKS"]["rate"], fw["since"], fw["hits"], fw["bets"]),
    }


if __name__ == "__main__":
    import os
    rows = data.load(os.environ.get("LAB_DATA_FILE"))
    print("play date:", data.play_date(rows))
    st = stats(rows)
    for k, v in st.items():
        if k == "PICKS":
            continue
        print("%-12s %4d/%4d = %5.2f%%  ROI %+6.1f%%  z %+5.2f %s" % (
            k, v["hit"], v["n"], 100 * v["rate"], 100 * v["roi"], v["z"], "<-- chuni line" if v["pick"] else ""))
    p = st["PICKS"]
    print("\nchuni hui 3 line: %d/%d = %.2f%%  ROI@9.5x %+.1f%%  (break-even %.2f%%)" % (
        p["hit"], p["n"], 100 * p["rate"], 100 * p["roi"], 100 * p["breakeven"]))
    print("pichhle 90 din:", scoreboard(rows, 90))
    for gi, pos in PICKS:
        print("aaj:", NAMES[gi], pos, "ank", next_ank(rows, gi, pos))
