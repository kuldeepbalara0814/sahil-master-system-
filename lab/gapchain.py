"""Gap filter: ek hi gap se bane 'step' pakadta hai.

Ek 'class' = number ya uska palat (28 aur 82 ek hi). Class kisi bhi game me aaye to us din ka 'step' hai.
Chain = d, d+g, d+2g ... (har step par class aaya). 2 step ban gaye to 3rd step d+2g par 'aane wala' hai;
aa gaya to 'pass', nahi aaya to 'nahi aaya'. Sirf paas ka data dekhta hai (aage ka kuch nahi).
"""
import datetime as dt

from lab import data

GAME_NAMES = ("FB", "GB", "GL", "DS")
PALETTE = ["FF9800", "E040FB", "1DE9B6", "FF5252", "C6FF00", "7C4DFF", "FFD740", "40C4FF"]   # pehla = narangi
STATUS = {"aane": "aane wala", "pass": "pass", "miss": "nahi aaya", "chhuti": "chhuti"}


def cls(n):
    return min(n, (n % 10) * 10 + n // 10)


def find(rows, gaps=(3, 4, 5, 6, 7), days=15, end=None, show="all"):
    """-> chains list. Har chain: cls, gap, steps[{date,hits}], status, due, next_due, color."""
    gaps = sorted({int(g) for g in gaps if 1 <= int(g) <= 10})
    days = max(3, min(int(days), 400))
    end = end or rows[-1][0]
    start = end - dt.timedelta(days=days - 1)
    by = {d: v for d, v, _ in rows if start <= d <= end}
    where = {}
    for d, v in by.items():
        for g, n in enumerate(v):
            where.setdefault(cls(n), {}).setdefault(d, []).append({"game": GAME_NAMES[g], "g": g, "n": int(n)})
    td = lambda d, k: d + dt.timedelta(days=k)
    chains = []
    for c, dates in where.items():
        for g in gaps:
            for d in sorted(dates):
                if td(d, -g) in dates:                       # run ka shuru nahi, aage ka hissa hai
                    continue
                run = [d]
                while td(run[-1], g) in dates:
                    run.append(td(run[-1], g))
                if len(run) < 2:
                    continue
                due = td(run[-1], g)
                if len(run) >= 3:
                    status, nxt = "pass", (due if due > end else None)
                elif due > end:
                    status, nxt = "aane", None
                else:
                    status, nxt = ("chhuti" if data.is_last_day(due) else "miss"), None
                if status == "aane" and data.is_last_day(due):
                    status = "chhuti"
                chains.append({"cls": [c, (c % 10) * 10 + c // 10], "gap": g, "len": len(run), "status": status,
                               "due": due.isoformat() if status in ("aane", "chhuti") else None,
                               "next_due": nxt.isoformat() if nxt else None,
                               "steps": [{"date": x.isoformat(), "hits": dates[x]} for x in run]})
    order = {"aane": 0, "pass": 1, "miss": 2, "chhuti": 3}
    chains.sort(key=lambda x: (order[x["status"]], x["due"] or "9", x["steps"][-1]["date"], x["cls"][0], x["gap"]))
    if show in order:
        chains = [x for x in chains if x["status"] == show]
    for i, x in enumerate(chains):
        x["color"] = PALETTE[i % len(PALETTE)]
        x["status_text"] = STATUS[x["status"]]
    return {"end": end.isoformat(), "start": start.isoformat(), "gaps": gaps, "days": days, "chains": chains}


def marks(res):
    """Chart par rang: [{date, g (0-3), color, kind step|pass|due, text, tip}]. due wale din ke chaar column me baant diye jaate hain."""
    out, slot = [], {}
    for ch in res["chains"]:
        a, b = ch["cls"]
        label = f"{a:02d}" if a == b else f"{a:02d}/{b:02d}"
        tip = f"{label} gap {ch['gap']} din, {ch['len']} step: {ch['status_text']}"
        for st in ch["steps"]:
            for h in st["hits"]:
                out.append({"date": st["date"], "g": h["g"], "color": ch["color"], "kind": "step", "text": "", "tip": tip})
        if ch["len"] >= 3:
            for h in ch["steps"][2]["hits"]:                 # 3rd step: alag nishan (moti border)
                out.append({"date": ch["steps"][2]["date"], "g": h["g"], "color": ch["color"], "kind": "pass", "text": "", "tip": tip})
        for dd in (ch["due"], ch["next_due"]):
            if dd:
                i = slot.get(dd, 0)
                slot[dd] = i + 1
                out.append({"date": dd, "g": i % 4, "color": ch["color"], "kind": "due", "text": f"{a:02d}?", "tip": tip})
    return out
