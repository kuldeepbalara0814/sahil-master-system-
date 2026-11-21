"""Record ka Excel: aap ki 'ANNUAL RESULT CHART' wali sheet jaisa (har saal ka block, mahine side-by-side, FB GB GL DS).

Sheet 1 'Record' = wahi chart (kaala background, safed number). Sheet 2 'Sada Table' = seedhi list (filter/sort ke liye).
Number asli number hain (00 dikhta hai), isliye Excel me jod/ginti/filter chalte hain.
"""
import calendar
import datetime as dt
import io

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

LABELS = ("FB", "GB", "GL", "DS")
NAVY, CYAN, BLACK, GOLD, WHITE = "1F2A44", "00B0F0", "111111", "FFC000", "FFFFFF"
thin = Side(style="thin", color="555555")
BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
CENTER = Alignment(horizontal="center", vertical="center")
DAYS = ["Somvar", "Mangalvar", "Budhvar", "Guruvar", "Shukravar", "Shanivar", "Ravivar"]


def select(rows, d_from=None, d_to=None):
    return [r for r in rows if (d_from is None or r[0] >= d_from) and (d_to is None or r[0] <= d_to)]


def _fill(c):
    return PatternFill("solid", fgColor=c)


FRAME = Side(style="medium", color="E0E0E0")


def _frame(ws, r_top, r_bot, c_left, c_right):
    """Mahine ke block ke charon taraf moti border (mahine aapas me na milen)."""
    for r in range(r_top, r_bot + 1):
        for c in range(c_left, c_right + 1):
            cell = ws.cell(r, c)
            b = cell.border
            cell.border = Border(left=FRAME if c == c_left else b.left, right=FRAME if c == c_right else b.right,
                                 top=FRAME if r == r_top else b.top, bottom=FRAME if r == r_bot else b.bottom)


def _apply_marks(ws, pos, marks):
    """Gap filter ke nishan: step = rang, 3rd step (pass) = rang + moti border, due = rang + 'NN?' (aane wala)."""
    from openpyxl.comments import Comment
    for m in marks or []:
        d = dt.date.fromisoformat(m["date"])
        if (d.year, d.month) not in pos:
            continue
        r0, c0 = pos[(d.year, d.month)]
        cell = ws.cell(r0 + 2 + d.day, c0 + m["g"])
        cell.fill = _fill(m["color"])
        cell.font = Font(bold=True, color="000000")
        if m["kind"] == "pass":
            side = Side(style="thick", color="FFFFFF")
            cell.border = Border(left=side, right=side, top=side, bottom=side)
        if m["kind"] == "due":
            cell.value = m["text"]
            cell.comment = Comment(m["tip"], "Sahil Lab")


def _chains_sheet(wb, res):
    t = wb.create_sheet("Gap Filter")
    t.append(["Rang", "Number/palat", "Gap (din)", "Step", "Kaise bane", "3rd step", "Haal"])
    for c in t[1]:
        c.font, c.fill, c.alignment = Font(bold=True, color=WHITE), _fill(NAVY), CENTER
    for ch in res["chains"]:
        a, b = ch["cls"]
        how = " → ".join(f"{dt.date.fromisoformat(s['date']).strftime('%d-%b')} " + "/".join(f"{h['game']} {h['n']:02d}" for h in s["hits"]) for s in ch["steps"])
        third = ch["due"] or ch["next_due"] or (ch["steps"][2]["date"] if ch["len"] >= 3 else "-")
        t.append(["", f"{a:02d}" if a == b else f"{a:02d} / {b:02d}", ch["gap"], ch["len"], how, third, ch["status_text"]])
        t.cell(t.max_row, 1).fill = _fill(ch["color"])
    for col, w in zip("ABCDEFG", (7, 14, 10, 7, 56, 13, 12)):
        t.column_dimensions[col].width = w
    t.freeze_panes = "A2"


def build(rows, d_from=None, d_to=None, gap=None):
    """rows = [(date,[fd,gb,gl,ds],src)] -> xlsx bytes. gap = gapchain.find() ka natija (rang ke nishan ke liye)."""
    sel = select(rows, d_from, d_to)
    pos = {}
    wb = Workbook()
    ws = wb.active
    ws.title = "Record"
    by = {r[0]: r[1] for r in sel}
    years = sorted({d.year for d in by})
    r0 = 1
    for y in years:
        months = sorted({d.month for d in by if d.year == y})
        ncol = 1 + 4 * len(months)
        ws.merge_cells(start_row=r0, start_column=1, end_row=r0, end_column=ncol)
        c = ws.cell(r0, 1, f"YEAR {y} — ANNUAL RESULT CHART ({' | '.join(LABELS)})")
        c.font, c.fill, c.alignment = Font(bold=True, size=14, color=GOLD), _fill(NAVY), CENTER
        ws.row_dimensions[r0].height = 26
        ws.merge_cells(start_row=r0 + 1, start_column=1, end_row=r0 + 2, end_column=1)
        for rr in (r0 + 1, r0 + 2):
            ws.cell(rr, 1).fill = _fill(CYAN)
        c = ws.cell(r0 + 1, 1, "Date")
        c.font, c.alignment = Font(bold=True, color=WHITE), CENTER
        for k, m in enumerate(months):
            c0 = 2 + 4 * k
            pos[(y, m)] = (r0, c0)
            ws.merge_cells(start_row=r0 + 1, start_column=c0, end_row=r0 + 1, end_column=c0 + 3)
            c = ws.cell(r0 + 1, c0, f"{calendar.month_abbr[m]}-{str(y)[2:]}")
            c.font, c.alignment = Font(bold=True, size=12, color=WHITE), CENTER
            for j in range(4):
                ws.cell(r0 + 1, c0 + j).fill = _fill(CYAN)
                h = ws.cell(r0 + 2, c0 + j, LABELS[j])
                h.font, h.fill, h.alignment, h.border = Font(bold=True, color=WHITE), _fill(CYAN), CENTER, BOX
        for day in range(1, 32):
            rr = r0 + 2 + day
            a = ws.cell(rr, 1, day)
            a.font, a.fill, a.alignment, a.border = Font(bold=True, color=CYAN), _fill(BLACK), CENTER, BOX
            for k, m in enumerate(months):
                v = None
                if day <= calendar.monthrange(y, m)[1]:
                    v = by.get(dt.date(y, m, day))
                for j in range(4):
                    cell = ws.cell(rr, 2 + 4 * k + j, None if v is None else int(v[j]))
                    cell.number_format = "00"
                    cell.font, cell.fill, cell.alignment, cell.border = Font(bold=True, color=WHITE), _fill(BLACK), CENTER, BOX
        for k in range(len(months)):
            _frame(ws, r0 + 1, r0 + 33, 2 + 4 * k, 5 + 4 * k)
        r0 += 36
    if gap:
        from lab import gapchain
        _apply_marks(ws, pos, gapchain.marks(gap))
    ws.column_dimensions["A"].width = 7
    for ci in range(2, 2 + 4 * 12):
        ws.column_dimensions[get_column_letter(ci)].width = 6.2
    ws.freeze_panes = "B1"

    t = wb.create_sheet("Sada Table")
    t.append(["Date", "Din", *LABELS])
    for d, v, _ in sel:
        t.append([d, DAYS[d.weekday()], *[int(x) for x in v]])
    for c in t[1]:
        c.font, c.fill, c.alignment = Font(bold=True, color=WHITE), _fill(NAVY), CENTER
    for row in t.iter_rows(min_row=2):
        row[0].number_format = "dd-mmm-yyyy"
        for c in row[2:]:
            c.number_format = "00"
            c.alignment = CENTER
    t.freeze_panes = "A2"
    t.auto_filter.ref = f"A1:F{max(len(sel) + 1, 2)}"
    t.column_dimensions["A"].width = 14
    t.column_dimensions["B"].width = 12
    if gap:
        _chains_sheet(wb, gap)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
