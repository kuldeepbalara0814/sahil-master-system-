"""Paper trading (kalpnik paisa). Koi asli paisa nahi.

Ledger = ek JSON: {"capital": 10000, "bets": [...]}.  Har bet: strategy, date, game, number, stake, status.
Jeet: stake x 95 (agar us game me us din 40 se kam alag number khele) warna x 90. Net = stake x (mult-1).
Stake hamesha 5 ke multiple (min 5).
"""
import datetime as dt
import math

from . import data, picks

STRATEGIES = {
    "single": "Single jodi: kal ka GB number, FD+GL+DS par",
    "list10s": "10 number ki list (subah hi sab game ki, aaj ka koi result dekhe bina)",
    "list10": "10 number ki list (har game se pehle, aaj ke pehle ke result dekh kar)",
    "manual": "Meri apni pick",
}


def new_ledger(capital=10000):
    return {"version": 1, "capital": capital, "bets": []}


def check_stake(stake):
    if not isinstance(stake, int) or stake < 5 or stake % 5:
        raise ValueError("stake 5 ke multiple me hona chahiye (5, 10, 15 ...)")


def place(ledger, strategy, date, game, number, stake=5):
    """Nayi bet jodo. Wahi (strategy, date, game, number) dobara ho to False."""
    check_stake(stake)
    if strategy not in STRATEGIES:
        raise ValueError("strategy galat")
    if game not in data.GAMES or not (0 <= number <= 99):
        raise ValueError("game ya number galat")
    d = date if isinstance(date, str) else date.isoformat()
    for b in ledger["bets"]:
        if (b["strategy"], b["date"], b["game"], b["number"]) == (strategy, d, game, number):
            return False
    ledger["bets"].append({"strategy": strategy, "date": d, "game": game, "number": number, "stake": stake,
                           "status": "pending", "result": None, "net": None})
    return True


def settle(ledger, rows):
    """Jo bet ka result aa chuka use jeet/haar likho. Kitni settle hui."""
    res = {d.isoformat(): R for d, R, _ in rows}
    distinct = {}
    for b in ledger["bets"]:
        distinct.setdefault((b["strategy"], b["date"], b["game"]), set()).add(b["number"])
    n = 0
    for b in ledger["bets"]:
        if b["status"] != "pending" or b["date"] not in res:
            continue
        r = res[b["date"]][data.GAMES.index(b["game"])]
        mult = 95 if len(distinct[(b["strategy"], b["date"], b["game"])]) < 40 else 90
        b["result"] = r
        if b["number"] == r:
            b["status"], b["net"] = "win", b["stake"] * (mult - 1)
        else:
            b["status"], b["net"] = "loss", -b["stake"]
        n += 1
    return n


def auto_place(ledger, rows, stake=5):
    """Subah ke liye: single (3 bet), list10s (4 game x 10), list10 ka FD hissa. Kitni nayi bet lagi."""
    play = data.play_date(rows).isoformat()
    plan = picks.daily_plan(rows)
    added = 0
    for g in plan["single"]["games"]:
        added += place(ledger, "single", play, g, plan["single"]["number"], stake)
    for g, lst in plan["list10_static"].items():
        for n, _ in lst:
            added += place(ledger, "list10s", play, g, n, stake)
    for n, _ in (plan["list10"]["FD"] or []):
        added += place(ledger, "list10", play, "FD", n, stake)
    return added


def place_sequential(ledger, rows, today_known, stake=5):
    """Aaj ke ab tak ke result (FD, GB, GL ..) dekh kar agle game ki list10 ki bet lagao."""
    play = data.play_date(rows).isoformat()
    g = len(today_known)
    if g > 3:
        return 0
    prev = rows[-12:]
    added = 0
    for n, _ in picks.top_list(prev, list(today_known), g, picks.K_DEFAULT):
        added += place(ledger, "list10", play, data.GAMES[g], n, stake)
    return added


def summary(ledger, strategy=None):
    bets = [b for b in ledger["bets"] if strategy in (None, b["strategy"])]
    done = [b for b in bets if b["status"] != "pending"]
    staked = sum(b["stake"] for b in done)
    net = sum(b["net"] for b in done)
    wins = [b for b in done if b["status"] == "win"]
    # equity (din ke hisaab se)
    by_day = {}
    for b in done:
        by_day[b["date"]] = by_day.get(b["date"], 0) + b["net"]
    eq, run, peak, dd, curve = ledger["capital"], 0, 0, 0, []
    for d in sorted(by_day):
        run += by_day[d]
        peak = max(peak, run)
        dd = max(dd, peak - run)
        curve.append({"date": d, "net": run, "capital": ledger["capital"] + run})
    months = {}
    for b in done:
        m = b["date"][:7]
        x = months.setdefault(m, {"bets": 0, "wins": 0, "net": 0})
        x["bets"] += 1
        x["wins"] += b["status"] == "win"
        x["net"] += b["net"]
    return {"bets": len(done), "pending": len(bets) - len(done), "wins": len(wins),
            "hit_pct": (len(wins) / len(done)) if done else 0.0, "staked": staked, "net": net,
            "roi": (net / staked) if staked else 0.0, "capital_now": ledger["capital"] + net,
            "max_drawdown": dd, "curve": curve, "months": months}


def summary_all(ledger):
    return {s: summary(ledger, s) for s in STRATEGIES if any(b["strategy"] == s for b in ledger["bets"])}
