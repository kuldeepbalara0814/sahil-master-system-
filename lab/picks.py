"""Aaj ki list: single jodi aur har game ki 10 number ki list.

Sab saaf vazan hain (koi chhupa model nahi). Dhyan se dekha gaya asar:
  * kal ka GB number baaki 3 game me ~1.3-1.5% aata hai (GB me nahi)
  * usi din pehle aaye number baad ke game me ~1.4% aate hain
  * pichle 3 kaam ke din ke number thode zyada aate hain, 4-12 din ke thode kam
  * kal ke same game ka number / uski family agle din kam aati hai  -> list se neeche
"""
from . import data

GAMES = data.GAMES
WEIGHTS = dict(yday_gb=4.0, same_day=4.0, same_day_gb=2.0, rec3=2.0, rec12=0.4, same_game_yday=-3.0, family_yday=-1.0)
K_DEFAULT = 10
PAYOUT_FEWER_THAN_40 = 95


def family(n):
    """Rashi (har ank +5) aur palat se bane numbers (khud n bhi)."""
    t, o = divmod(n, 10)
    out = set()
    for tt in (t, (t + 5) % 10):
        for oo in (o, (o + 5) % 10):
            out.add(tt * 10 + oo)
            out.add(oo * 10 + tt)
    return out


def score_game(prev, today_known, g, w=WEIGHTS):
    """prev = aakhri kuch poori lines [(date, [4], src)], today_known = aaj ke pehle ke games ke result (list)."""
    s = [0.0] * 100
    last = prev[-1][1]
    if g != 1:
        s[last[1]] += w["yday_gb"]
    for x in today_known:
        s[x] += w["same_day_gb"] if g == 1 else w["same_day"]
    for k, (_, R, _) in enumerate(reversed(prev[-12:])):
        for x in R:
            s[x] += w["rec3"] if k < 3 else w["rec12"]
    s[last[g]] += w["same_game_yday"]
    for x in family(last[g]):
        s[x] += w["family_yday"]
    return s


def top_list(prev, today_known, g, k=K_DEFAULT, w=WEIGHTS):
    s = score_game(prev, today_known, g, w)
    order = sorted(range(100), key=lambda n: (-s[n], n))[:k]
    return [(n, round(s[n], 2)) for n in order]


def single_jodi(prev):
    """Kal ka GB number: FD, GL, DS par khelo (GB par nahi)."""
    return {"number": prev[-1][1][1], "games": ["FD", "GL", "DS"], "from": prev[-1][0].isoformat()}


def daily_plan(rows, today_known=None, k=K_DEFAULT):
    """rows = poori lines. today_known = aaj ke ab tak ke result [fd, gb, gl] (pehle ke games)."""
    today_known = list(today_known or [])
    prev = rows[-12:]
    lists = {}
    for g in range(4):
        lists[GAMES[g]] = top_list(prev, today_known[:g], g, k) if g <= len(today_known) else None
    # jab tak pichle game ka result nahi aaya, us game ki 'sequential' list nahi banti
    static = {GAMES[g]: top_list(prev, [], g, k) for g in range(4)}
    return {"play_date": data.play_date(rows).isoformat(), "single": single_jodi(rows),
            "list10": lists, "list10_static": static}


def walk(rows, k=K_DEFAULT, w=WEIGHTS, sequential=True, start=12):
    """Purane saalon par (sirf pehle ka data dekh kar) hit: [(date, game, hit, size)]"""
    out = []
    for i in range(start, len(rows)):
        d, R, _ = rows[i]
        if not data.adjacent(rows[i - 1][0], d):
            continue
        prev = rows[max(0, i - 12):i]
        for g in range(4):
            known = R[:g] if sequential else []
            lst = {n for n, _ in top_list(prev, known, g, k, w)}
            out.append((d, g, R[g] in lst, len(lst)))
    return out


def walk_single(rows, start=2):
    out = []
    for i in range(start, len(rows)):
        d, R, _ = rows[i]
        if not data.adjacent(rows[i - 1][0], d):
            continue
        x = rows[i - 1][1][1]
        for g in (0, 2, 3):
            out.append((d, g, R[g] == x, 1))
    return out
