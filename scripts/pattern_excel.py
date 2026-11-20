"""Pattern ki Excel copy: record chart + aap ke nishaan rang me (blue = pichla mahina, yellow = is mahine) + 'Padho' sheet.

Chalao:  python scripts/pattern_excel.py patterns/001_copy_pattern  [output.xlsx]
Folder me examples.csv (date,game,number,color,role) aur README.md chahiye. Nishaan ka number data se mila kar jaancha jaata hai.
"""
import csv
import datetime as dt
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from openpyxl import load_workbook                      # noqa: E402
from openpyxl.styles import Font, PatternFill            # noqa: E402

from lab import data, export_xlsx                        # noqa: E402

COLORS = {"blue": "00B0F0", "yellow": "FFC000"}
GAMECOL = {"FD": 0, "FB": 0, "GB": 1, "GL": 2, "DS": 3}


def check(examples, rows):
    """Nishaan wale number data se milte hain? (galat padhne par yahan pakad lo). -> samasyaon ki list"""
    by = {r[0]: r[1] for r in rows}
    bad = []
    for e in examples:
        if not e["number"]:
            continue
        d = dt.date.fromisoformat(e["date"])
        if d not in by or by[d][GAMECOL[e["game"]]] != int(e["number"]):
            bad.append(f"{e['date']} {e['game']}: likha {e['number']}, data me {by.get(d)}")
    return bad


def build(folder, out=None):
    ex = list(csv.DictReader(open(os.path.join(folder, "examples.csv"), encoding="utf-8")))
    rows = data.load()
    probs = check(ex, rows)
    if probs:
        raise SystemExit("Nishaan data se nahi milte:\n" + "\n".join(probs))
    dates = [dt.date.fromisoformat(e["date"]) for e in ex]
    first = dt.date(min(dates).year, min(dates).month, 1) - dt.timedelta(days=62)      # 2 mahine pehle se
    wb = load_workbook(io.BytesIO(export_xlsx.build(rows, first.replace(day=1), max(r[0] for r in rows))))
    ws = wb["Record"]
    # month -> column block, day -> row  (export_xlsx ka layout: har saal ka block 36 row, date 1..31 = row 3+d)
    blocks = {}
    r0 = 1
    for y in sorted({r[0].year for r in rows if r[0] >= first.replace(day=1)}):
        months = sorted({r[0].month for r in rows if r[0].year == y and r[0] >= first.replace(day=1)})
        blocks[y] = (r0, months)
        r0 += 36
    for e in ex:
        d = dt.date.fromisoformat(e["date"])
        r0, months = blocks[d.year]
        if d.month not in months:
            months.append(d.month)
            raise SystemExit(f"{d} ka mahina chart me nahi")
        base = 2 + 4 * months.index(d.month)
        cols = range(4) if e["game"] == "ALL" else [GAMECOL[e["game"]]]
        for g in cols:
            c = ws.cell(r0 + 2 + d.day, base + g)
            c.fill = PatternFill("solid", fgColor=COLORS[e["color"]])
            c.font = Font(bold=True, color="000000")
    p = wb.create_sheet("Padho", 0)
    readme = open(os.path.join(folder, "README.md"), encoding="utf-8").read().splitlines()
    p.column_dimensions["A"].width = 120
    for i, line in enumerate(readme, 1):
        p.cell(i, 1, line.lstrip("# ").rstrip())
    wb.active = 1
    out = out or os.path.join(folder, os.path.basename(folder) + ".xlsx")
    wb.save(out)
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    print(build(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None))
