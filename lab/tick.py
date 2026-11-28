"""App ki apni ghadi: kaun sa result ab tak aa jana chahiye tha par nahi aaya (patterns/013_auto_fetch_alerts/README.md).

GitHub ka schedule der karta hai ya chhod deta hai, isliye server khud bhi site dekhta hai (app khuli ho ya /api/tick ko ping mile).
Line d ke result (IST): FB d 18:20, GB d 22:15, GL d+1 00:15, DS d+1 05:30 (tab line poori)."""
import datetime as dt

from . import data

GAP = 600                      # do koshish ke beech kam se kam 10 minute
TIMES = (("FB", 0, 18, 20), ("GB", 0, 22, 15), ("GL", 1, 0, 15), ("DS", 1, 5, 30))      # user ke bataye time (26 Nov 2026)


def khatra(now, rows, rep, pstate):
    """App ke upar bade laal box ke liye: aaj ke pattern / tokri / card sach me bane ya nahi. now = IST. -> {"kyun","baat"} ya None.
    DS subah ~5:30 aata hai; 6:30 tak intezaar, tokri ke liye 7:30 tak."""
    now = now.replace(tzinfo=None)
    need = now.date() - dt.timedelta(days=1 if (now.hour, now.minute) >= (6, 30) else 2)
    while data.is_last_day(need):
        need -= dt.timedelta(days=1)
    last, play = rows[-1][0], data.play_date(rows)
    if last < need:
        return {"kyun": "ds", "title": "DS UPDATE NAHI HUA", "baat": [
            f"{need:%d-%m} ka DS abhi nahi aaya. Data sirf {last:%d-%m} tak hai.",
            "Aaj ke naye pattern, 30 jodi, Naksha aur card NAHI bane. Neeche jo dikh raha hai wo PURANA hai, use aaj ka mat samjho.",
            "App har 10 minute me khud koshish kar rahi hai; DS aate hi sab apne aap banega."]}
    if not rep or rep.get("asof") != last.isoformat() or rep.get("errors"):
        why = "scan me galti aayi" if rep and rep.get("errors") else "scan abhi nahi hua"
        return {"kyun": "scan", "title": "PATTERN SCAN NAHI HUA", "baat": [
            f"Data {last:%d-%m} tak aa gaya par pattern {why}.", "Pattern, 30 jodi aur card purane ho sakte hain. Active tab me 'Abhi scan karo' dabao."]}
    if now >= dt.datetime.combine(play, dt.time(7, 30)) and play.isoformat() not in (pstate or {}).get("days", {}):
        return {"kyun": "tokri", "title": "AAJ KI TOKRI LOCK NAHI HUI", "baat": [
            f"{play:%d-%m} ki tokri aur card abhi nahi bane.", "Active tab me 'Abhi scan karo' dabao; phir bhi na bane to Ruflo ko batao."]}
    return None


def overdue(now, rows, part=None, hours=2):
    """Itne ghante baad bhi jo result nahi aaya (ghanti / email ke liye)."""
    return due(now - dt.timedelta(hours=hours), rows, part)


def due(now, rows, part=None):
    """now = IST datetime. rows = poori lines, part = aadhi line (lab.partial) ya None. -> baaki results ['FB', ...]."""
    d = data.play_date(rows)
    have = set((part or {}).get("results") or {}) if (part or {}).get("date") == d.isoformat() else set()
    now = now.replace(tzinfo=None)
    return [g for g, plus, h, m in TIMES if now >= dt.datetime.combine(d + dt.timedelta(days=plus), dt.time(h, m)) and g not in have]
