"""App ki apni ghadi: kaun sa result ab tak aa jana chahiye tha par nahi aaya (patterns/013_auto_fetch_alerts/README.md).

GitHub ka schedule der karta hai ya chhod deta hai, isliye server khud bhi site dekhta hai (app khuli ho ya /api/tick ko ping mile).
Line d ke result (IST): FB d 18:35, GB d 22:35, GL d+1 00:20, DS d+1 05:40 (tab line poori)."""
import datetime as dt

from . import data

GAP = 600                      # do koshish ke beech kam se kam 10 minute
TIMES = (("FB", 0, 18, 35), ("GB", 0, 22, 35), ("GL", 1, 0, 20), ("DS", 1, 5, 40))


def overdue(now, rows, part=None, hours=2):
    """Itne ghante baad bhi jo result nahi aaya (ghanti / email ke liye)."""
    return due(now - dt.timedelta(hours=hours), rows, part)


def due(now, rows, part=None):
    """now = IST datetime. rows = poori lines, part = aadhi line (lab.partial) ya None. -> baaki results ['FB', ...]."""
    d = data.play_date(rows)
    have = set((part or {}).get("results") or {}) if (part or {}).get("date") == d.isoformat() else set()
    now = now.replace(tzinfo=None)
    return [g for g, plus, h, m in TIMES if now >= dt.datetime.combine(d + dt.timedelta(days=plus), dt.time(h, m)) and g not in have]
