"""Har game ka alag record: FB, GB, GL (2013 se) aur DS (1966 se). Sab 'sab ek me' results.csv se bante hain, isliye wo update hota hai to ye bhi apne aap.

DS ka purana hissa (1966-2012) data/ds_1966_2012.csv me hai (doosri site se, scripts/fetch_ds_history.py).
DS hamare record me 'pichli tarikh ki line' me likha jata hai (line = Desawar khulne ki tarikh - 1 din). basis="khula" me site jaisi tarikh.
"""
import csv
import datetime as dt
import io
import os

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

from . import data

GAMES = {"FB": 0, "GB": 1, "GL": 2, "DS": 3}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _old_ds(path=None):
    path = path or os.path.join(os.path.dirname(data.DATA_FILE), "ds_1966_2012.csv")
    out = []
    try:
        with open(path, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                out.append((dt.date.fromisoformat(r["line_date"]), int(r["ds"])))
    except OSError:
        pass
    return out


def series(rows, game, basis="line"):
    """[(tarikh, number)] tarikh ke order me. DS: purana (1966-2012) + results.csv. basis='khula': DS ki tarikh +1 din (site jaisi)."""
    g = GAMES[game]
    cur = [(d, int(v[g])) for d, v, _ in rows]
    out = cur
    if game == "DS":
        first = rows[0][0] if rows else dt.date(2013, 1, 1)
        out = [(d, v) for d, v in _old_ds() if d < first and d.year >= 1966] + cur
        if basis == "khula":
            out = [(d + dt.timedelta(days=1), v) for d, v in out]
    return out


def grid(ser, year):
    """31 din x 12 mahine ka chart (jaisa site par): grid[din-1][mahina-1] = number ya None."""
    gr = [[None] * 12 for _ in range(31)]
    for d, v in ser:
        if d.year == year:
            gr[d.day - 1][d.month - 1] = v
    return gr


def years(ser):
    return sorted({d.year for d, _ in ser})


def csv_bytes(rows, game, basis="line"):
    buf = io.StringIO()
    w = csv.writer(buf)
    ser = series(rows, game, basis)
    if game == "DS":
        w.writerow(["date" if basis == "line" else "khula_date", "ds"])
    else:
        w.writerow(["date", game.lower()])
    for d, v in ser:
        w.writerow([d.isoformat(), f"{v:02d}"])
    return buf.getvalue().encode("utf-8")


THIN = Side(style="thin", color="777777")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
CEN = Alignment(horizontal="center", vertical="center")


def xlsx_bytes(rows, game, basis="line"):
    """Ek workbook: har saal ki alag sheet (din upar-niche 1-31, mahine side me). Sabse naya saal pehle."""
    ser = series(rows, game, basis)
    wb = Workbook()
    wb.remove(wb.active)
    note = {"FB": "FB (Faridabad)", "GB": "GB (Ghaziabad)", "GL": "GL (Gali)",
            "DS": "DS (Desawar) - us tarikh ki line me (agli subah ka)" if basis == "line" else "DS (Desawar) - khulne ki tarikh (site jaisi)"}[game]
    for y in sorted(years(ser), reverse=True):
        ws = wb.create_sheet(str(y))
        ws.merge_cells("A1:M1")
        c = ws["A1"]
        c.value = f"{note} - {y}"
        c.font, c.fill, c.alignment = Font(bold=True, size=13, color="FFFFFF"), PatternFill("solid", fgColor="1F3A5F"), CEN
        ws.cell(2, 1, "Din").font = Font(bold=True)
        for m in range(12):
            h = ws.cell(2, 2 + m, MONTHS[m])
            h.font, h.fill, h.alignment, h.border = Font(bold=True, color="FFFFFF"), PatternFill("solid", fgColor="44546A"), CEN, BOX
        gr = grid(ser, y)
        for dday in range(31):
            dc = ws.cell(3 + dday, 1, dday + 1)
            dc.font, dc.alignment, dc.border = Font(bold=True, color="0B5394"), CEN, BOX
            for m in range(12):
                c = ws.cell(3 + dday, 2 + m, gr[dday][m])
                c.number_format, c.alignment, c.border, c.font = "00", CEN, BOX, Font(bold=True)
        ws.column_dimensions["A"].width = 6
        for m in range(12):
            ws.column_dimensions[chr(66 + m)].width = 7
        ws.freeze_panes = "B3"
    bio = io.BytesIO()
    wb.save(bio)
    return bio.getvalue()


def write_files(rows, data_dir):
    """data/game_fb.csv, game_gb.csv, game_gl.csv, game_ds.csv (git me alag-alag file). Update ke baad chalta hai."""
    names = []
    for game in GAMES:
        p = os.path.join(data_dir, f"game_{game.lower()}.csv")
        tmp = p + ".tmp"
        with open(tmp, "wb") as f:
            f.write(csv_bytes(rows, game))
        os.replace(tmp, p)
        names.append(os.path.basename(p))
    return names
