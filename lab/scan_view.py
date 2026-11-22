"""Pattern Scan: ek pattern ka saaf rang wala chart (app me dikhane ke liye) aur wahi Excel me."""
import datetime as dt
import io

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

from . import data, scanner
from .scanner import GAMES, pal

LIGHT = {"FF9800": "FFE0B2", "AB47BC": "E1BEE7", "66BB6A": "C8E6C9", "EF5350": "FFCDD2", "26C6DA": "B2EBF2", "F06292": "F8BBD0", "8D6E63": "D7CCC8", "9CCC65": "DCEDC8",
         "00E676": "C8F7DC", "FF4FA3": "FFD0E6"}


def _row(date, v=None, c=None, kind=None, txt=None):
    return {"date": date, "v": v, "c": c or [None] * 4, "kind": kind or [None] * 4, "txt": txt or [None] * 4}


def view(rows, pid):
    """pid: 'naksha:L:YYYY-MM-DD' ya 'copy:shape:g:YYYY-MM-DD'."""
    parts = pid.split(":")
    D = [r[0] for r in rows]
    N = len(rows)
    if parts[0] == "naksha":
        L, so = int(parts[1]), D.index(dt.date.fromisoformat(parts[2]))
        sc, F = N - L, 8
        info = scanner.match_info(rows, so, sc, L)
        colour = {}
        for k in info["comps"]:
            for x in k["cells"]:
                colour[x] = k["color"]
        olds, news = [], []
        for i in range(L + F):
            po = so + i
            if po < N:
                c = [None] * 4
                kind = [None] * 4
                for g in range(4):
                    if i < L and 4 * i + g in colour:
                        c[g], kind[g] = colour[4 * i + g], "step"
                    elif i >= L:
                        for k in info["comps"]:
                            if info["C"][po, g] == k["old_class"]:
                                c[g], kind[g] = LIGHT[k["color"]], "light"
                olds.append(_row(D[po].isoformat(), [int(x) for x in rows[po][1]], c, kind))
            else:
                olds.append(_row(""))
            if i < L:
                c, kind = [None] * 4, [None] * 4
                for g in range(4):
                    if 4 * i + g in colour:
                        c[g], kind[g] = colour[4 * i + g], "step"
                news.append(_row(D[sc + i].isoformat(), [int(x) for x in rows[sc + i][1]], c, kind))
            else:
                c, kind, txt = [None] * 4, [None] * 4, [None] * 4
                if po < N:
                    for g in range(4):
                        for k in info["comps"]:
                            if info["C"][po, g] == k["old_class"]:
                                c[g], kind[g], txt[g] = LIGHT[k["color"]], "light", "?"
                news.append(_row("aage", None, c, kind, txt))
        tg = "; ".join(f"{t['game']} me {' / '.join(f'{x:02d}' for x in t['numbers'])}" for t in info["targets"]) or "koi andaza nahi"
        return {"id": pid, "title": f"{scanner.name_for('Naksha', f'{L}:{D[so].isoformat()}')}: {D[so]:%b %Y} jaisa naksha",
                "note": f"Same rang = mile hue jode (same/palat, same jagah). Halka rang = purane me wahi class wapas aayi, naye me wahi jagah '?'. Aaj ka andaza: {tg}.",
                "blocks": [{"label": f"PURANA {D[so]:%d %b %Y} se", "rows": olds}, {"label": f"NAYA {D[sc]:%d %b %Y} se (ab tak)", "rows": news}]}
    if parts[0] == "copy":
        shape, g, d0 = parts[1], int(parts[2]), dt.date.fromisoformat(parts[3])
        last = D[-1]
        today = data.play_date(rows)
        ev = [e for e in scanner.copy_events(rows, d0, d0, today) if e["shape"] == shape and e["g"] == g]
        if not ev:
            raise ValueError("Ye copy jodi nahi mili")
        e = ev[0]
        i0 = D.index(e["d"])
        out = []
        for k in range(i0, i0 + 4):
            if k < N:
                d = D[k]
                c, kind = [None] * 4, [None] * 4
                if d in (e["d"], e["j"]):
                    c[g], kind[g] = "00E676", "step"
                if d == e["t"]:
                    for kk, _ in e["hit"]:
                        c[kk], kind[kk] = "FF4FA3", "pass"
                out.append(_row(d.isoformat(), [int(x) for x in rows[k][1]], c, kind))
            else:
                out.append(_row(e["t"].isoformat(), None, [LIGHT["FF4FA3"]] * 4, ["light"] * 4, ["?"] * 4))
        sets = " ".join(f"{s:02d}" for s in e["S"])
        return {"id": pid, "title": f"{scanner.name_for('Copy', f'{shape}:{g}:{d0.isoformat()}')}: {shape} {GAMES[g]} {e['x']:02d}/{e['y']:02d}",
                "note": f"Hara = jodi ({GAMES[g]} me {e['x']:02d} aur {e['y']:02d}). Gulabi = din 4 par set ka number aaya (PASS). Set: {sets}.",
                "blocks": [{"label": "Din 1 se din 4", "rows": out}]}
    raise ValueError("Pattern id samajh nahi aayi")


def xlsx(rows, pid):
    v = view(rows, pid)
    wb = Workbook()
    ws = wb.active
    ws.title = "Pattern"
    thin = Side(style="thin", color="888888")
    box = Border(left=thin, right=thin, top=thin, bottom=thin)
    cen = Alignment(horizontal="center", vertical="center")
    ws["A1"] = v["title"]
    ws["A1"].font = Font(bold=True, size=13)
    ws["A2"] = v["note"]
    ws["A2"].alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=5 * len(v["blocks"]) + len(v["blocks"]) - 1)
    ws.row_dimensions[2].height = 48
    col = 1
    for b in v["blocks"]:
        ws.cell(3, col, b["label"]).font = Font(bold=True)
        for j, h in enumerate(["Tarikh", *GAMES]):
            c = ws.cell(4, col + j, h)
            c.font, c.alignment = Font(bold=True, color="FFFFFF"), cen
            c.fill = PatternFill("solid", fgColor="37474F")
        for i, r in enumerate(b["rows"]):
            rr = 5 + i
            ws.cell(rr, col, r["date"] and (dt.date.fromisoformat(r["date"]).strftime("%d-%b-%y") if r["date"] != "aage" else "(aage)")).alignment = cen
            for g in range(4):
                val = r["txt"][g] if r["txt"][g] else (None if r["v"] is None else r["v"][g])
                c = ws.cell(rr, col + 1 + g, val)
                c.alignment, c.border, c.number_format = cen, box, "00"
                c.font = Font(bold=True, color="000000" if r["c"][g] else "333333", italic=r["kind"][g] == "light")
                if r["c"][g]:
                    c.fill = PatternFill("solid", fgColor=r["c"][g])
                if r["kind"][g] == "pass":
                    s = Side(style="thick", color="000000")
                    c.border = Border(left=s, right=s, top=s, bottom=s)
        for j in range(5):
            ws.column_dimensions[ws.cell(1, col + j).column_letter].width = 11 if j == 0 else 6
        col += 6
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue(), v["title"]
