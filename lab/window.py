"""Meri Window (24 Nov 2026): app ke andar ek alag, 'apni chuni hui' screen.

1) Roz ke NAYE Naksha pattern (002) aur unse bani jodi (copy ho sakti hain).
2) Top 30 jodi: sab pattern me jo number sabse zyada baar aaye (Number Rank ALL ke top 30), copy ho sakti hain.
3) Do alag kagaz ki pocket (har ek Rs 10,000): Naksha ki jodi aur Top 30 jodi. Roz apne aap paper trading:
   FB par har jodi Rs 10, na aaye to GB par Rs 15, na aaye to GL par Rs 20, na aaye to DS par Rs 25. Jis game me hit aaya, us din wahin ruk jao.

Sab sirf kagaz ka research hai: software dikhata hai, faisla insaan ka.

Imaandari ka niyam: tokri (basket) roz ek hi baar, us din ka pehla scan aate hi LOCK hoti hai (play_date ke liye). Baad ke scan use nahi badalte,
isliye FB/GB/GL ka result dekh kar tokri badalne ka lookahead nahi hota. Pocket ka hisaab START se pehle ke din nahi ginta (wahan tokri result ke baad bani thi).
Hisaab 'rows' (site ka poora result) aur hath se dale result (manual_results.json) se bina state ke nikalta hai; sirf tokri window_log.json me rakhi jati hai.
"""
import datetime as dt

from . import data, rank

START = dt.date(2026, 11, 25)           # pehla poora din jiski tokri subah ke scan me bani (24 Nov ki tokri result ke baad bani, isliye nahi ginte)
CAPITAL = 10000
TOP_N = 30
LADDER = (("FB", 10), ("GB", 15), ("GL", 20), ("DS", 25))        # (game, har jodi par Rs)
GAME_IDX = {"FB": 0, "GB": 1, "GL": 2, "DS": 3}
POCKETS = (("naksha", "Naksha ki jodi (naye pattern)"), ("top30", "Top 30 jodi (sab pattern ka baar-baar)"))
KEEP_DAYS = 150


def new_state():
    return {"days": {}}


def baskets(rep, rows):
    """Aaj ke scan se: (naye Naksha pattern ki list, top-30 jodi). Sirf wahi jinke andaze (targets) hain."""
    play = data.play_date(rows)
    naksha = []
    for p in rep.get("patterns", []):
        if p.get("key") != "naksha":
            continue
        for it in p.get("items", []):
            tg = it.get("targets") or []
            if not it.get("new") or not tg:
                continue
            nums = sorted({int(n) for t in tg for n in t["numbers"]})
            naksha.append({"id": it["id"], "name": it.get("name"), "title": it.get("title"), "numbers": nums,
                           "games": sorted({t["game"] for t in tg})})
    rk = rank.build(rep, rows)
    allg = next(g for g in rk["groups"] if g["key"] == "all")
    top = [{"n": r["n"], "score": r["score"], "votes": r["votes"], "baar": r["baar"]} for r in allg["lists"]["ALL"][:TOP_N]]
    return play, naksha, top


def naksha_all(rk):
    """Aaj ke SAB active number: Naksha 1 (purane + naye) aur Puzzle-Steps - sirf dikhane ke liye, paper basket nahi.
    Naksha-Rashi (2b) isme nahi (user: 'naksha 2b ko meri window me lena ka nahi kaha'; wo 44 items se ~92 jodi chhoota hai).
    -> [{n, votes, naksha, steps, baar, dost, top30}] (votes zyada pehle)."""
    g = {x["key"]: x for x in rk["groups"]}
    allg = {r["n"]: r for r in g["all"]["lists"]["ALL"]}
    top = {r["n"] for r in g["all"]["lists"]["ALL"][:TOP_N]}
    cnt = {}
    for key in ("naksha", "steps"):
        for r in g[key]["lists"]["ALL"]:
            c = cnt.setdefault(r["n"], {"naksha": 0, "steps": 0})
            c[key] += r["votes"]
    out = []
    for n, c in cnt.items():
        a = allg.get(n, {})
        dost = sum(1 for lb in a.get("maps", []) if lb.startswith("Dost "))
        out.append({"n": n, "votes": c["naksha"] + c["steps"], "naksha": c["naksha"], "steps": c["steps"], "baar": a.get("baar", 0), "dost": dost, "top30": n in top})
    out.sort(key=lambda r: (-r["votes"], r["n"]))
    return out


def dost_baar(rk):
    """Aaj ke Dost (pichhli line ke 12 dost x 3 samay) + Baar (2 point) ke number - sirf dikhane ke liye; Top 30 isse nahi banti
    (backtest research/dost_top30: dost+baar 28.6% vs random 30%). -> [{n, dost, baar, score, top30}] score zyada pehle."""
    g = {x["key"]: x for x in rk["groups"]}
    allg = {r["n"]: r for r in g["all"]["lists"]["ALL"]}
    top = {r["n"] for r in g["all"]["lists"]["ALL"][:TOP_N]}
    out = []
    for r in g["dost"]["lists"]["ALL"]:
        out.append({"n": r["n"], "dost": r["votes"], "baar": r["baar"], "score": r["votes"] + 2 * r["baar"], "top30": r["n"] in top})
    seen = {x["n"] for x in out}
    for n, r in allg.items():                                       # baar ki tokri ke wo number jo kisi dost list me nahi
        if r["baar"] and n not in seen:
            out.append({"n": n, "dost": 0, "baar": 1, "score": 2, "top30": n in top})
    out.sort(key=lambda r: (-r["score"], -r["dost"], r["n"]))
    return out


def steps007(rep):
    """Card 007 (Puzzle-Steps) ke aaj ke number aur har pattern me kya ban raha hai. -> {date, all, items:[{id, name, title, aaj, aage}], aage_all}"""
    items = []
    for p in rep.get("patterns", []):
        if p.get("key") != "steps":
            continue
        for no, it in enumerate(p.get("items", []), 1):
            if it.get("status") != "aaj":
                continue
            items.append({"no": no, "id": it["id"], "name": it.get("name"), "title": it.get("title"),
                          "aaj": it.get("targets") or [], "aage": it.get("aage") or []})
    return {"date": rep.get("play_date"), "items": items,
            "all": sorted({n for it in items for t in it["aaj"] for n in t["numbers"]}),
            "aage_all": sorted({n for it in items for t in it["aage"] for n in t["numbers"]})}


def record(state, rep, rows, known=None):
    """Is play_date ki tokri abhi tak nahi bani to LOCK karo. -> True agar nayi bani.
    known = partial/hath wale result {date: {game: n}}: us din ka koi result pehle hi aa chuka ho to tokri 'late' (ginti me nahi)."""
    play, naksha, top = baskets(rep, rows)
    days = state.setdefault("days", {})
    key = play.isoformat()
    if key in days:
        return False
    if any(e.get("pattern") == "Naksha" for e in rep.get("errors") or []) or rep.get("play_date") not in (None, key):
        return False                                              # tuta ya purana scan: tokri lock nahi karni
    days[key] = {"asof": rep.get("asof"), "scan_time": rep.get("time"), "naksha": naksha, "top30": top}
    if (known or {}).get(key):
        days[key]["late"] = True
    for d in sorted(days)[:-KEEP_DAYS]:
        del days[d]
    return True


def numbers_of(day, pocket):
    if pocket == "naksha":
        return sorted({n for it in day.get("naksha", []) for n in it["numbers"]})
    return sorted(x["n"] for x in day.get("top30", []))


def _mult(count):
    return 95 if count < 40 else 90                                # paper.settle jaisa hi niyam


def _results(rows_by_date, manual, date):
    """{game: number} jo us din tak aa chuke (poori line ho to chaaron, warna hath se dale hue)."""
    out = {}
    if date in rows_by_date:
        v = rows_by_date[date]
        out = {g: int(v[i]) for g, i in GAME_IDX.items()}
    for g, n in ((manual or {}).get(date) or {}).items():
        if g in GAME_IDX and g not in out:
            out[g] = int(n)
    return out


def ladder_day(numbers, results, balance):
    """Ek din ki seedhi (ladder). -> {steps, net, stop, hit, status}. status: hit | no_hit | pending | nothing | low."""
    nums = set(numbers)
    if not nums:
        return {"steps": [], "net": 0, "stop": None, "hit": None, "status": "nothing", "spent": 0}
    mult = _mult(len(nums))
    steps, net, spent = [], 0, 0
    bal = balance
    for game, stake in LADDER:
        cost = stake * len(nums)
        if bal < cost:
            return {"steps": steps, "net": net, "stop": None, "hit": None, "status": "low", "spent": spent}
        if game not in results:
            return {"steps": steps, "net": net, "stop": None, "hit": None, "status": "pending", "spent": spent, "next": {"game": game, "stake": stake, "cost": cost}}
        r = results[game]
        spent += cost
        if r in nums:
            win = stake * mult
            gain = win - cost
            net += gain
            steps.append({"game": game, "stake": stake, "cost": cost, "result": r, "hit": True, "net": gain})
            return {"steps": steps, "net": net, "stop": game, "hit": {"game": game, "n": r}, "status": "hit", "spent": spent, "mult": mult}
        net -= cost
        bal -= cost
        steps.append({"game": game, "stake": stake, "cost": cost, "result": r, "hit": False, "net": -cost})
    return {"steps": steps, "net": net, "stop": None, "hit": None, "status": "no_hit", "spent": spent, "mult": mult}


def pocket(state, rows, manual, pocket_key):
    days = state.get("days", {})
    by = {d.isoformat(): v for d, v, _ in rows}
    bal = CAPITAL
    out, curve = [], []
    totals = {"days": 0, "hit_days": 0, "spent": 0, "net": 0, "by_game": {g: 0 for g, _ in LADDER}, "no_hit": 0, "low": 0}
    peak, dd = CAPITAL, 0
    for date in sorted(days):
        if date < START.isoformat() or days[date].get("late"):       # late = result aane ke baad bani tokri
            continue
        nums = numbers_of(days[date], pocket_key)
        res = _results(by, manual, date)
        ld = ladder_day(nums, res, bal)
        pending = ld["status"] == "pending"
        bal += ld["net"]
        rec = {"date": date, "numbers": nums, "count": len(nums), "net": ld["net"], "balance": bal, "status": ld["status"], "steps": ld["steps"],
               "stop": ld["stop"], "hit": ld["hit"], "spent": ld["spent"], "next": ld.get("next")}
        out.append(rec)
        if ld["status"] in ("hit", "no_hit", "low"):
            curve.append({"date": date, "balance": bal})
        if ld["status"] in ("hit", "no_hit"):
            totals["days"] += 1
            totals["spent"] += ld["spent"]
            totals["net"] += ld["net"]
            if ld["status"] == "hit":
                totals["hit_days"] += 1
                totals["by_game"][ld["stop"]] += 1
            else:
                totals["no_hit"] += 1
            peak = max(peak, bal)
            dd = max(dd, peak - bal)
        elif ld["status"] == "low":
            totals["low"] += 1
        if pending:
            pass
    roi = round(100 * totals["net"] / totals["spent"], 1) if totals["spent"] else 0.0
    return {"key": pocket_key, "capital": CAPITAL, "balance": bal, "net": bal - CAPITAL, "roi": roi, "max_drawdown": dd, "totals": totals,
            "curve": curve, "days": out[-40:][::-1]}


def view(state, rows, manual=None, today=None):
    days = state.get("days", {})
    play = data.play_date(rows).isoformat()
    cur = days.get(play)
    pockets = {k: pocket(state, rows, manual, k) for k, _ in POCKETS}
    plan = None
    if cur:
        plan = {}
        for k, _ in POCKETS:
            nums = numbers_of(cur, k)
            plan[k] = {"numbers": nums, "count": len(nums), "mult": _mult(len(nums)) if nums else None,
                       "ladder": [{"game": g, "stake": s, "cost": s * len(nums)} for g, s in LADDER],
                       "worst_cost": sum(s for _, s in LADDER) * len(nums), "counted": play >= START.isoformat() and not cur.get("late"), "late": bool(cur.get("late"))}
    return {"play_date": play, "start": START.isoformat(), "capital": CAPITAL, "ladder": [{"game": g, "stake": s} for g, s in LADDER],
            "naksha_new": cur.get("naksha", []) if cur else [], "top30": cur.get("top30", []) if cur else [], "locked": bool(cur),
            "scan_time": cur.get("scan_time") if cur else None, "plan": plan, "pockets": pockets,
            "pocket_names": dict(POCKETS)}
