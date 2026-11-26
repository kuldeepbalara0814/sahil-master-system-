"""Ek pattern ke saare items ek saath download: PDF / JPG / Excel (har pattern 'Pattern 01', 'Pattern 02'...)
aur kisi pattern ko Pattern paint window ke board me badalna (edit karne ke liye)."""
import calendar
import datetime as dt
import io
import os
import zipfile

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from PIL import Image, ImageDraw, ImageFont

from . import scan_view
from .scanner import GAMES

KEYS = {"naksha": "Naksha_pattern", "naksha2": "Naksha_Rashi_pattern", "copy": "Copy_pattern", "family": "Family_pattern", "dana": "Dana_Farak_pattern", "steps": "Puzzle_Steps_pattern"}
MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

PW, PH, M = 1240, 1754, 40                      # A4 portrait 150 dpi, margin
CONTENT_W, CONTENT_H = PW - 2 * M, PH - 2 * M
CW0, CW, RH = 90, 46, 24                        # tarikh column, cell column, row height
BW = CW0 + 4 * CW                               # ek block ki chaudai
PATW = 560                                      # ek pattern ki chaudai (do ek page par aate hain)

_FONTS = {}
_DIRS = ["/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/dejavu", "/usr/share/fonts/TTF", "/Library/Fonts", "C:/Windows/Fonts"]


def font(size, bold=False, italic=False):
    key = (size, bold, italic)
    if key not in _FONTS:
        name = "DejaVuSans" + ("-Bold" if bold and not italic else "") + ("-Oblique" if italic and not bold else "") + ("-BoldOblique" if bold and italic else "") + ".ttf"
        f = None
        for d in _DIRS:
            try:
                f = ImageFont.truetype(os.path.join(d, name), size)
                break
            except OSError:
                continue
        _FONTS[key] = f or ImageFont.load_default(size=size)
    return _FONTS[key]


def dtext(iso):
    """'2026-11-17' -> '17 Nov' ('... chhuti' wali tarikh bhi chalti hai)."""
    if not iso:
        return ""
    try:
        d = dt.date.fromisoformat(iso[:10])
    except ValueError:
        return iso
    return f"{d.day} {MON[d.month - 1]}" + (" chhuti" if len(iso) > 10 else "")


def wrap(draw, text, f, width):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=f) <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def collect(rep, key, status="all", limit=120):
    """-> (items [(no, item)], total) ; no = poori list me 1-based jagah."""
    ents = [p for p in rep["patterns"] if p["key"] == key]
    if not ents:
        raise ValueError("Ye pattern nahi mila: " + str(key))
    full = list(enumerate(ents[0]["items"], 1))
    if status == "aaj":
        full = [x for x in full if x[1].get("status") == "aaj"]
    return full[:limit], len(full)


def safe_view(rows, it):
    try:
        return scan_view.view(rows, it["id"])
    except (ValueError, IndexError, KeyError) as e:
        return {"id": it["id"], "title": it.get("title", ""), "note": "Chart nahi ban paya: " + (str(e) or "galti"), "blocks": []}


def target_text(it):
    if it.get("target") and not it["target"].get("numbers") and it["target"].get("games"):
        return "Aaj ka andaza: " + it["target"]["games"]
    t = it.get("target")
    if not t:
        return ""
    return f"Aaj ka andaza: {t['games']} me " + " ".join(f"{int(x):02d}" for x in t["numbers"])


def heading(no, it, v):
    return f"Pattern {no:02d} - {it.get('name', '')} - {it.get('title') or v['title']}"


def draw_pattern(no, it, v):
    """Ek pattern ki image (PATW chaudai)."""
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    fh, fn, fc = font(15, True), font(13), font(14, True)
    pw = max(PATW, len(v["blocks"]) * (BW + 12))              # 3 block (steps) ho to chaudai badhao
    head = wrap(tmp, heading(no, it, v), fh, pw - 8)
    note = wrap(tmp, v["note"], fn, pw - 8)
    tgt = wrap(tmp, target_text(it), font(13, True), pw - 8)
    nb = max([len(b["rows"]) for b in v["blocks"]] or [0])
    h = 6 + len(head) * 20 + len(note) * 17 + len(tgt) * 18 + 8 + (22 + RH + nb * RH if v["blocks"] else 0) + 14
    im = Image.new("RGB", (pw, h), "white")
    d = ImageDraw.Draw(im)
    y = 6
    for ln in head:
        d.text((4, y), ln, font=fh, fill="black")
        y += 20
    for ln in note:
        d.text((4, y), ln, font=fn, fill="#444444")
        y += 17
    for ln in tgt:
        d.text((4, y), ln, font=font(13, True), fill="#B00040")
        y += 18
    y += 8
    x0 = 0
    for b in v["blocks"]:
        d.text((x0 + 2, y), b["label"], font=font(12, True), fill="#222222")
        ty = y + 22
        for j, hd in enumerate(["Tarikh", *GAMES]):
            x = x0 + (0 if j == 0 else CW0 + (j - 1) * CW)
            w = CW0 if j == 0 else CW
            d.rectangle([x, ty, x + w, ty + RH], fill="#37474F", outline="#888888")
            d.text((x + w / 2, ty + RH / 2), hd, font=fc, fill="white", anchor="mm")
        for i, r in enumerate(b["rows"]):
            ry = ty + RH * (i + 1)
            d.rectangle([x0, ry, x0 + CW0, ry + RH], outline="#888888")
            d.text((x0 + CW0 / 2, ry + RH / 2), dtext(r["date"]), font=font(12), fill="black", anchor="mm")
            for g in range(4):
                x = x0 + CW0 + g * CW
                col = r["c"][g]
                d.rectangle([x, ry, x + CW, ry + RH], fill="#" + col if col else "white", outline="#888888")
                val = r["txt"][g] if r["txt"][g] else (None if r["v"] is None else f"{r['v'][g]:02d}")
                if val:
                    d.text((x + CW / 2, ry + RH / 2), val, font=font(14 if len(val) <= 3 else 10, True, r["kind"][g] == "light"), fill="black" if col else "#333333", anchor="mm")
                if r["kind"][g] == "pass":
                    d.rectangle([x, ry, x + CW, ry + RH], outline="black", width=3)
        x0 += BW + 12
    return im


def index_pages(key, items, total, limit):
    """Pehla page(en): Pattern no., naam, title, status."""
    pages = []
    fh, f, fb = font(22, True), font(15), font(15, True)
    per = (CONTENT_H - 130) // 26
    chunks = [items[i:i + per] for i in range(0, len(items), per)] or [[]]
    for ci, ch in enumerate(chunks):
        im = Image.new("RGB", (PW, PH), "white")
        d = ImageDraw.Draw(im)
        y = M
        d.text((M, y), f"{KEYS[key].replace('_', ' ')} - index" + (f" (page {ci + 1})" if len(chunks) > 1 else ""), font=fh, fill="black")
        y += 36
        msg = f"Kul {total} pattern" + (f", pehle {limit} liye (baaki chhode)." if total > len(items) and len(items) >= limit else ".")
        d.text((M, y), msg, font=f, fill="#444444")
        y += 34
        for x, t in ((M, "Pattern"), (M + 130, "Naam"), (M + 400, "Title"), (PW - M - 110, "Status")):
            d.text((x, y), t, font=fb, fill="black")
        y += 24
        d.line([M, y, PW - M, y], fill="#888888")
        y += 4
        for no, it in ch:
            d.text((M, y + 2), f"Pattern {no:02d}", font=f, fill="black")
            d.text((M + 130, y + 2), str(it.get("name", ""))[:28], font=f, fill="black")
            t = str(it.get("title", ""))
            while d.textlength(t, font=f) > PW - M - 110 - (M + 400) - 10 and len(t) > 4:
                t = t[:-2]
            d.text((M + 400, y + 2), t, font=f, fill="black")
            d.text((PW - M - 110, y + 2), str(it.get("status", "")), font=f, fill="#B00040" if it.get("status") == "aaj" else "black")
            y += 26
        pages.append(im)
    return pages


def compose(rows, key, items, total, limit):
    """-> [(file_label, PIL page)] : index page(en) + pattern pages."""
    pages = [("Index", im) for im in index_pages(key, items, total, limit)]
    cur, cur_nos = None, []
    x = y = rowh = 0
    done = []

    def flush():
        if cur is not None:
            done.append((f"Pattern_{cur_nos[0]:02d}-{cur_nos[-1]:02d}" if len(cur_nos) > 1 else f"Pattern_{cur_nos[0]:02d}", cur))
    for no, it in items:
        pim = draw_pattern(no, it, safe_view(rows, it))
        if cur is not None and x + pim.width > CONTENT_W:        # nayi line
            x, y, rowh = 0, y + rowh + 12, 0
        if cur is None or y + pim.height > CONTENT_H:             # nayi page (pattern beech me nahi kat'ta)
            flush()
            cur, cur_nos = Image.new("RGB", (PW, PH), "white"), []
            x = y = rowh = 0
        cur.paste(pim, (M + x, M + y))
        cur_nos.append(no)
        x += pim.width + 10
        rowh = max(rowh, pim.height)
    flush()
    return pages + done


def to_pdf(pages):
    buf = io.BytesIO()
    ims = [p for _, p in pages]
    ims[0].save(buf, "PDF", save_all=True, append_images=ims[1:], resolution=150.0)
    return buf.getvalue()


def to_jpg(pages):
    """Ek page -> (bytes, 'image/jpeg', None); zyada -> ZIP."""
    def jb(im):
        b = io.BytesIO()
        im.save(b, "JPEG", quality=88)
        return b.getvalue()
    if len(pages) == 1:
        return jb(pages[0][1]), "image/jpeg", "jpg"
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w", zipfile.ZIP_DEFLATED) as z:
        for name, im in pages:
            z.writestr(name + ".jpg", jb(im))
    return b.getvalue(), "application/zip", "zip"


def to_xlsx(rows, key, items, total, limit):
    wb = Workbook()
    ix = wb.active
    ix.title = "Index"
    ix["A1"] = KEYS[key].replace("_", " ") + " - index"
    ix["A1"].font = Font(bold=True, size=13)
    ix["A2"] = f"Kul {total} pattern" + (f", pehle {limit} liye (baaki chhode)." if total > len(items) and len(items) >= limit else ".")
    for j, h in enumerate(["Pattern", "Sheet", "Naam", "Title", "Status"], 1):
        c = ix.cell(4, j, h)
        c.font, c.fill = Font(bold=True, color="FFFFFF"), PatternFill("solid", fgColor="37474F")
    for i, (no, it) in enumerate(items):
        v = safe_view(rows, it)
        sh = f"P{no:02d}"
        ws = wb.create_sheet(sh)
        scan_view.fill_sheet(ws, v)
        if it.get("target"):
            ws["A2"] = v["note"] + " " + target_text(it)
        r = 5 + i
        ix.cell(r, 1, f"Pattern {no:02d}")
        ix.cell(r, 2, sh).hyperlink = f"#'{sh}'!A1"
        ix.cell(r, 3, it.get("name", ""))
        ix.cell(r, 4, it.get("title", ""))
        ix.cell(r, 5, it.get("status", ""))
    for col, w in zip("ABCDE", (12, 8, 26, 50, 10)):
        ix.column_dimensions[col].width = w
    ix.cell(1, 1).alignment = Alignment(horizontal="left")
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def pages_of(images, label):
    """Taiyar pattern images -> A4 jaise page (pattern beech me nahi kat'ta)."""
    pages, cur = [], None
    x = y = rowh = 0
    for im in images:
        if cur is not None and x + im.width > CONTENT_W:
            x, y, rowh = 0, y + rowh + 12, 0
        if cur is None or y + im.height > CONTENT_H:
            if cur is not None:
                pages.append((label, cur))
            cur = Image.new("RGB", (PW, PH), "white")
            x = y = rowh = 0
        cur.paste(im, (M + x, M + y))
        x += im.width + 10
        rowh = max(rowh, im.height)
    if cur is not None:
        pages.append((label, cur))
    return pages


def naksha_aaj(rows, yd):
    """Meri Window: aaj ki tarikh par jin Naksha 1 maps ka box hai (naye aur pehle bane). yd = yaad.view(...)["aaj"].
    Har map us din ke data se banta hai jis din bana tha; aaj ka box laal karke jodi likhi jati hai. -> [(item, view)]"""
    target = yd["date"]
    maps = {}
    for e in yd["items"]:
        maps.setdefault((e["asof"], e["id"]), []).append(e)
    out = []
    for (asof, pid), entries in sorted(maps.items(), key=lambda kv: (kv[0][0], kv[0][1]), reverse=True):
        rs = [r for r in rows if r[0].isoformat() <= asof]
        v = safe_view(rs, {"id": pid, "title": entries[0]["title"]})
        marks = {}
        for e in entries:
            marks.setdefault(GAMES.index(e["game"]), set()).update(e["numbers"])
        if len(v["blocks"]) == 2:
            for r in v["blocks"][1]["rows"]:
                if r["date"][:10] == target:
                    for g, nums in marks.items():
                        r["c"][g], r["kind"][g], r["txt"][g] = "FF5252", "step", "/".join(f"{n:02d}" for n in sorted(nums))
        says = "; ".join(f"{GAMES[g]} me {' / '.join(f'{n:02d}' for n in sorted(nums))}" for g, nums in sorted(marks.items()))
        v["note"] = f"Bana: {dt.date.fromisoformat(asof):%d %b} tak ke data se. Laal box = {dt.date.fromisoformat(target):%d %b} ka andaza."
        item = {"name": entries[0]["name"], "title": entries[0]["title"],
                "target": {"games": says, "numbers": []}}
        out.append((item, v))
    return out


def steps_aaj(rows, rep, part=None):
    """Card 007 ke wo pattern jinme aaj (play date) ke andaze hain. -> [(item, view)]"""
    out = []
    for p in rep.get("patterns", []):
        if p.get("key") != "steps":
            continue
        for it in p.get("items", []):
            if it.get("status") != "aaj" or not it.get("targets"):
                continue
            try:
                v = scan_view.view(rows, it["id"], part)
            except (ValueError, IndexError, KeyError):
                continue
            says = "; ".join(f"{t['game']} me {' / '.join(f'{n:02d}' for n in t['numbers'])}" for t in it["targets"])
            out.append(({"name": it.get("name"), "title": it.get("title"), "target": {"games": says, "numbers": []}}, v))
    return out


def aaj_pdf(parts, date):
    """parts = [(heading, [(item, view)])] -> ek PDF (bytes). Har hissa naye page se."""
    pages = []
    for head, items in parts:
        title = Image.new("RGB", (CONTENT_W, 44), "white")
        ImageDraw.Draw(title).text((4, 8), f"{head} - {date} ({len(items)} map)", font=font(22, True), fill="black")
        if not items:
            ImageDraw.Draw(title).text((4, 30), "Aaj koi map nahi.", font=font(13), fill="black")
        pages += pages_of([title] + [draw_pattern(no, it, v) for no, (it, v) in enumerate(items, 1)], head)
    return to_pdf(pages)


def build(rows, rep, key, fmt, status="all", limit=120):
    """-> (bytes, mimetype, filename)"""
    if key not in KEYS:
        raise ValueError("key galat: naksha / naksha2 / copy / family / dana me se ek")
    if fmt not in ("pdf", "jpg", "xlsx"):
        raise ValueError("fmt galat: pdf / jpg / xlsx")
    if status not in ("all", "aaj"):
        raise ValueError("status galat: all ya aaj")
    limit = max(1, min(int(limit), 200))
    items, total = collect(rep, key, status, limit)
    base = f"{KEYS[key]}_{rep.get('play_date') or rep.get('asof')}"
    if fmt == "xlsx":
        return to_xlsx(rows, key, items, total, limit), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", base + ".xlsx"
    pages = compose(rows, key, items, total, limit)
    if fmt == "pdf":
        return to_pdf(pages), "application/pdf", base + ".pdf"
    blob, mime, ext = to_jpg(pages)
    return blob, mime, base + "." + ext


# ---------------- pattern -> Pattern paint window board ----------------
def _month_board(label, cells, name):
    """cells {iso|g: HEX} -> board (from = pehle cell ke mahine ki 1 tarikh, months <= 12)."""
    ds = sorted({k.split("|")[0] for k in cells})
    if not ds:
        d0 = dt.date.today().replace(day=1)
        return {"label": label, "from": d0.isoformat(), "months": 1, "name": name, "cells": {}}
    a, b = dt.date.fromisoformat(ds[0]), dt.date.fromisoformat(ds[-1])
    start = a.replace(day=1)
    months = min(12, (b.year - a.year) * 12 + b.month - a.month + 1)
    k = start.year * 12 + start.month - 1 + months
    end = dt.date(k // 12, k % 12 + 1, 1)                      # (months ke baad ka pehla din)
    keep = {key: c for key, c in cells.items() if start <= dt.date.fromisoformat(key.split("|")[0]) < end}
    return {"label": f"{label}: {MON[a.month - 1]} {a.year}", "from": start.isoformat(), "months": months, "name": name, "cells": keep}


def _cells(block):
    out = {}
    for r in block["rows"]:
        if not r["date"]:
            continue
        iso = r["date"][:10]
        for g in range(4):
            if r["c"][g]:
                out[f"{iso}|{g}"] = str(r["c"][g]).upper()
    return out


def to_board(rows, pid, name=""):
    v = scan_view.view(rows, pid)
    key = pid.split(":")[0]
    nm = (name or v["title"])[:60]
    if key in ("naksha", "naksha2") and len(v["blocks"]) == 2:
        return [_month_board("Purana", _cells(v["blocks"][0]), nm), _month_board("Naya", _cells(v["blocks"][1]), nm)]
    cells = {}
    for b in v["blocks"]:
        cells.update(_cells(b))
    return [_month_board("Pattern", cells, nm)]


def board_xlsx(rows, board):
    """Save kiya hua board -> Excel: mahine ek ke neeche, tarikh neeche, FB GB GL DS, rang bhare cell."""
    from openpyxl.styles import Border, Side
    by = {d: v for d, v, *_ in rows}
    y, m = int(board["from"][:4]), int(board["from"][5:7])
    n = max(1, min(int(board.get("months", 1)), 12))
    cells = board.get("cells") or {}
    wb = Workbook()
    ws = wb.active
    ws.title = "Pattern"
    thin = Side(style="thin", color="888888")
    box = Border(left=thin, right=thin, top=thin, bottom=thin)
    cen = Alignment(horizontal="center", vertical="center")
    ws["A1"] = board.get("name", "Pattern")
    ws["A1"].font = Font(bold=True, size=14)
    r = 3
    for _ in range(n):
        ws.cell(r, 1, f"{calendar.month_name[m].upper()} {y}").font = Font(bold=True, size=13)
        r += 1
        for j, h in enumerate(["Tarikh", "Din", *GAMES], 1):
            c = ws.cell(r, j, h)
            c.font, c.alignment, c.border = Font(bold=True, color="FFFFFF"), cen, box
            c.fill = PatternFill("solid", fgColor="37474F")
        r += 1
        for day in range(1, calendar.monthrange(y, m)[1] + 1):
            d = dt.date(y, m, day)
            ws.cell(r, 1, d.strftime("%d-%b-%Y")).alignment = cen
            ws.cell(r, 2, d.strftime("%a")).alignment = cen
            for c0 in (1, 2):
                ws.cell(r, c0).border = box
            v = by.get(d)
            for g in range(4):
                c = ws.cell(r, 3 + g, None if v is None else int(v[g]))
                c.alignment, c.border, c.number_format = cen, box, "00"
                col = cells.get(f"{d.isoformat()}|{g}")
                c.font = Font(bold=bool(col), color="000000")
                if col:
                    c.fill = PatternFill("solid", fgColor=str(col).upper())
            r += 1
        r += 2
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    ws.column_dimensions["A"].width = 14
    ws.column_dimensions["B"].width = 7
    for col in "CDEF":
        ws.column_dimensions[col].width = 7
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
