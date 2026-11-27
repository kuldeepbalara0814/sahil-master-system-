"""Auto paper pockets (patterns/015_auto_pockets/README.md). Sirf KAGAZ ka hisaab, asli paisa nahi.

Har tarah ki list ka apna Rs 10,000 ka pocket, ek hi niyam (Meri Window wala): har jodi par FB Rs 10, na aaye to GB Rs 15, GL Rs 20, DS Rs 25;
jis game me aaye wahin us din ruk. Milta hai stake ka 95 guna (40 ya zyada jodi par 90 guna).
Tokri us din ke subah ke scan (DS ke baad) par ek baar LOCK; result aane ke baad bani tokri (late) ginti me nahi.
Ginti START se; balance chalta rehta hai (mahine ka closing = agle mahine ka opening). data/pockets.json kabhi kaata nahi jata."""
import datetime as dt
import io
import random

from . import baar, data, rank, window, yaad

START = dt.date(2026, 12, 1)
CAPITAL = 10000
TOP = 30
LISTS = (("top30", "30 jodi (sab pattern)"), ("dost", "Dost 30"), ("baar", "Baar (din) ki jodi"), ("rashi", "Rashi (Naksha-Rashi) 30"),
         ("naksha", "Naksha (naye)"), ("naksha_sab", "Naksha sab (naye + pehle bane)"), ("card007", "Card 007"), ("family", "Family"),
         ("dana", "Dana-Farak"), ("copy", "Jodi-Copy"), ("random", "Random 30 (sirf tulna)"))
GAMES = ("FB", "GB", "GL", "DS")


def new_state():
    return {"days": {}}


def baskets(rep, rows):
    """-> {key: sorted numbers} aaj (play date) ke liye. Sirf scan aur poori lines se."""
    play = data.play_date(rows)
    rk = rank.build(rep, rows)
    g = {x["key"]: x["lists"]["ALL"] for x in rk["groups"]}
    top = lambda key: sorted(r["n"] for r in g.get(key, [])[:TOP])
    return {"top30": top("all"), "dost": top("dost"), "rashi": top("naksha2"), "family": top("family"), "dana": top("dana"), "copy": top("copy"),
            "baar": sorted(baar.tokri(rows, play.weekday(), asof=play)["numbers"]),
            "naksha": sorted({n for it in window.baskets(rep, rows)[1] for n in it["numbers"]}),
            "naksha_sab": sorted(yaad.view(rows)["aaj"]["all"]),
            "card007": sorted(window.steps007(rep)["all"]),
            "random": sorted(random.Random(f"sahil-{play.isoformat()}").sample(range(100), TOP))}


def record(state, rep, rows, known=None):
    """Is play date ki sab tokri ek baar lock. -> True agar nayi bani."""
    play = data.play_date(rows).isoformat()
    days = state.setdefault("days", {})
    if play in days or rep.get("play_date") not in (None, play) or rep.get("errors"):
        return False
    days[play] = {"lists": baskets(rep, rows)}
    if (known or {}).get(play):
        days[play]["late"] = True
    return True


def statement(state, rows, manual, key):
    """Ek pocket ka poora hisaab: din-wise line, mahine-wise opening/closing, aur random se kitne hit din ki ummeed thi."""
    by = {d.isoformat(): v for d, v, _ in rows}
    bal, lines, months = CAPITAL, [], {}
    tot = {"days": 0, "hit_days": 0, "expected_hit_days": 0.0, "spent": 0, "won": 0, "net": 0, "skipped": 0, "by_game": {g: 0 for g in GAMES}}
    for date in sorted(state.get("days", {})):
        day = state["days"][date]
        if date < START.isoformat() or day.get("late"):
            continue
        nums = day["lists"].get(key) or []
        res = window._results(by, manual, date)
        ld = window.ladder_day(nums, res, bal)
        opening = bal
        bal += ld["net"]
        spent = ld.get("spent", 0)
        won = spent + ld["net"]
        lines.append({"date": date, "count": len(nums), "numbers": nums, "results": res, "status": ld["status"], "hit": ld["hit"], "stop": ld["stop"],
                      "spent": spent, "won": won, "net": ld["net"], "opening": opening, "balance": bal})
        m = months.setdefault(date[:7], {"month": date[:7], "opening": opening, "closing": bal, "net": 0, "hit_days": 0, "days": 0})
        m["closing"] = bal
        m["net"] += ld["net"]
        if ld["status"] in ("hit", "no_hit"):
            m["days"] += 1
            tot["days"] += 1
            tot["spent"] += spent
            tot["won"] += won
            tot["net"] += ld["net"]
            tot["expected_hit_days"] += 1 - (1 - len(nums) / 100) ** 4
            if ld["status"] == "hit":
                m["hit_days"] += 1
                tot["hit_days"] += 1
                tot["by_game"][ld["stop"]] += 1
        elif ld["status"] == "low":
            tot["skipped"] += 1
    tot["expected_hit_days"] = round(tot["expected_hit_days"], 1)
    return {"key": key, "naam": dict(LISTS)[key], "capital": CAPITAL, "balance": bal, "totals": tot, "months": list(months.values()), "lines": lines}


def view(state, rows, manual=None):
    play = data.play_date(rows).isoformat()
    cur = state.get("days", {}).get(play)
    out = []
    for key, _ in LISTS:
        s = statement(state, rows, manual, key)
        s["lines"] = s["lines"][-45:][::-1]
        s["today"] = (cur or {}).get("lists", {}).get(key, [])
        s["today_cost"] = len(s["today"]) * sum(st for _, st in window.LADDER)
        out.append(s)
    return {"start": START.isoformat(), "capital": CAPITAL, "play_date": play, "late": bool((cur or {}).get("late")),
            "ladder": [{"game": g, "stake": s} for g, s in window.LADDER], "pockets": out}


def xlsx(state, rows, manual=None):
    """Statement Excel: 'Index' (sab pocket), 'Mahine' (opening/closing), har pocket ki apni sheet."""
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    head_fill = PatternFill("solid", fgColor="37474F")
    hit_fill = PatternFill("solid", fgColor="C8E6C9")

    def head(ws, cols, widths):
        ws.append(cols)
        for c in ws[ws.max_row]:
            c.font, c.fill = Font(bold=True, color="FFFFFF"), head_fill
            c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        for i, w in enumerate(widths):
            ws.column_dimensions[chr(65 + i)].width = w
    all_s = [statement(state, rows, manual, k) for k, _ in LISTS]
    wb = Workbook()
    ix = wb.active
    ix.title = "Index"
    ix.append([f"Sahil Lab - Auto paper pockets (sirf kagaz ka hisaab). Shuru {START:%d-%b-%Y}, har pocket Rs {CAPITAL}."])
    head(ix, ["Pocket", "Balance", "Fayda/Nuksan", "Din", "Hit din", "Random me ummeed (hit din)", "Kharcha", "Mila", "FB hit", "GB hit", "GL hit", "DS hit", "Paisa kam (din chhoota)"],
         [30, 11, 13, 6, 8, 16, 10, 10, 7, 7, 7, 7, 12])
    for s in all_s:
        t = s["totals"]
        ix.append([s["naam"], s["balance"], s["balance"] - CAPITAL, t["days"], t["hit_days"], t["expected_hit_days"], t["spent"], t["won"]] + [t["by_game"][g] for g in GAMES] + [t["skipped"]])
    mh = wb.create_sheet("Mahine")
    head(mh, ["Pocket", "Mahina", "Opening", "Fayda/Nuksan", "Closing", "Din", "Hit din"], [30, 10, 11, 13, 11, 6, 8])
    for s in all_s:
        for m in s["months"]:
            mh.append([s["naam"], m["month"], m["opening"], m["net"], m["closing"], m["days"], m["hit_days"]])
    words = {"hit": "HIT", "no_hit": "nahi aaya", "pending": "baaki", "nothing": "tokri khali", "low": "paisa kam"}
    for s in all_s:
        ws = wb.create_sheet(s["naam"].replace("/", "-")[:31])
        head(ws, ["Tarikh", "Jodi ginti", "Opening", "FB", "GB", "GL", "DS", "Haal", "Hit kahan", "Hit number", "Kharcha", "Mila", "Fayda/Nuksan", "Balance", "Tokri ke number"],
             [12, 8, 10, 5, 5, 5, 5, 11, 9, 9, 9, 9, 12, 10, 90])
        for x in s["lines"]:
            ws.append([x["date"], x["count"], x["opening"]] + [(f"{x['results'][g]:02d}" if g in x["results"] else "") for g in GAMES] +
                      [words.get(x["status"], x["status"]), x["stop"] or "", f"{x['hit']['n']:02d}" if x["hit"] else "", x["spent"], x["won"], x["net"], x["balance"],
                       " ".join(f"{n:02d}" for n in x["numbers"])])
            if x["hit"]:
                ws.cell(ws.max_row, 4 + GAMES.index(x["stop"])).fill = hit_fill
                ws.cell(ws.max_row, 8).fill = hit_fill
        ws.freeze_panes = "B2"
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
