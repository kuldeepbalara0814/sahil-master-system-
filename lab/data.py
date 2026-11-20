"""Result data: load / validate / merge (kabhi duplicate nahi).

Niyam (record ka):
  * FD GB GL usi tarikh ke. DS = agli subah (5:30) khula Desawar, jo usi tarikh ki line me likha hai.
  * Mahine ka aakhri din chhuti hai (us din ki line nahi hoti).
  * 00 ko 0 likha jata hai (file me).
"""
import csv
import datetime as dt
import os

GAMES = ("FD", "GB", "GL", "DS")
HERE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.environ.get("LAB_DATA_FILE", os.path.join(os.path.dirname(HERE), "data", "results.csv"))
HEADER = ["date", "fd", "gb", "gl", "ds", "source"]
BREAKEVEN_95 = 1 / 95          # 40 se kam number par 95 guna
BREAKEVEN_90 = 1 / 90


def parse_date(s):
    return dt.date.fromisoformat(s)


def is_last_day(d):
    return (d + dt.timedelta(days=1)).day == 1


def load(path=None):
    """[(date, [fd,gb,gl,ds], source)] tarikh ke order me."""
    path = path or DATA_FILE
    rows = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append((parse_date(r["date"]), [int(r["fd"]), int(r["gb"]), int(r["gl"]), int(r["ds"])], r.get("source", "")))
    rows.sort(key=lambda t: t[0])
    return rows


def save(rows, path=None):
    """Poori file dobara likho (pehle temp file, phir badlo - beech me toot-ne par bhi purani bachi rahe)."""
    path = path or DATA_FILE
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        for d, v, s in rows:
            w.writerow([d.isoformat(), *v, s])
    os.replace(tmp, path)


def validate(rows):
    """Samasyaon ki list (khaali = sab theek)."""
    probs = []
    dates = [d for d, _, _ in rows]
    if len(set(dates)) != len(dates):
        probs.append("duplicate tarikh mili")
    if dates != sorted(dates):
        probs.append("tarikh ka order galat")
    for d, v, _ in rows:
        if any(x < 0 or x > 99 for x in v):
            probs.append(f"{d}: number 0-99 se bahar")
    for i in range(1, len(rows)):
        if rows[i][1] == rows[i - 1][1] and (rows[i][0] - rows[i - 1][0]).days <= 2:
            probs.append(f"{rows[i][0]}: pichle din ki copy lagti hai")
    return probs


def adjacent(d0, d1):
    """Agla kaam ka din? (chhuti ke karan 30->1 me gap 2 hota hai)"""
    return 0 < (d1 - d0).days <= 2


def play_date(rows):
    """Wo tarikh jiska result abhi poora nahi (aakhri line ke baad ka agla kaam ka din)."""
    d = rows[-1][0] + dt.timedelta(days=1)
    if is_last_day(d):
        d += dt.timedelta(days=1)
    return d


def merge_new(rows, new_rows):
    """(merged, added, skipped, conflicts). Purani line kabhi nahi badalti; sirf nayi tarikh jodti hai."""
    have = {d: (v, s) for d, v, s in rows}
    merged = list(rows)
    added, skipped, conflicts = [], [], []
    for d, v, s in sorted(new_rows, key=lambda t: t[0]):
        if any(x < 0 or x > 99 for x in v):
            skipped.append((d, "number 0-99 se bahar"))
            continue
        if is_last_day(d):
            skipped.append((d, "mahine ka aakhri din (chhuti)"))
            continue
        if d in have:
            if have[d][0] != v:
                conflicts.append((d, have[d][0], v))
            continue
        prev = max((x for x in have if x < d), default=None)
        if prev is not None and adjacent(prev, d) and have[prev][0] == v:
            skipped.append((d, "pichle din ki copy"))
            continue
        have[d] = (v, s)
        merged.append((d, v, s))
        added.append(d)
    merged.sort(key=lambda t: t[0])
    return merged, added, skipped, conflicts
