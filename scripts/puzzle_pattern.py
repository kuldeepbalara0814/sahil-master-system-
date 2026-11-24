#!/usr/bin/env python3
"""Puzzle-Steps: EK FILE ki script (copy-paste karke kisi bhi jagah chala sakte ho, Termux me bhi).

Ye ek puzzle-logic R&D ka hissa hai (sirf paper, asli paisa nahi). Kaam: 3 mahine ek ke neeche ek lambi sheet maan kar
  Step 1 = (current mahina - 2) ki boundary,  Step 2 = (current mahina - 1) ki boundary,  Step 3 = current mahine ki boundary (adhuri)
me wahi design dhundhna, aur Excel + PDF me rang ke saath dikhana. Poora tarika: patterns/007_puzzle_steps/README.md

Chalane ka tarika (Termux):
    pip install openpyxl pillow
    python puzzle_pattern.py data/results.csv --out ~/storage/downloads
CSV: header  date,fd,gb,gl,ds   (date = YYYY-MM-DD; DS usi tarikh ki line me, mahine ka aakhri din chhuti = line nahi)
Option: --top 8 (kitne design), --L 8,10,12 (boundary ki lambai, box)
"""
import argparse
import csv
import datetime as dt
import os
import sys

GAMES = ("FB", "GB", "GL", "DS")
COLS = ["FFB74D", "CE93D8", "80DEEA", "A5D6A7", "F48FB1", "FFF176", "90CAF9", "BCAAA4"]
RED = "FF5252"


def cls(n):                      # number aur uska palat ek (28 aur 82)
    return min(n, (n % 10) * 10 + n // 10)


def pal(n):
    return (n % 10) * 10 + n // 10


def is_last_day(d):              # mahine ka aakhri din chhuti
    return (d + dt.timedelta(days=1)).day == 1


def load(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append((dt.date.fromisoformat(r["date"]), [int(r["fd"]), int(r["gb"]), int(r["gl"]), int(r["ds"])]))
    rows.sort()
    return rows


def month_end(d):
    return (d.replace(day=28) + dt.timedelta(days=4)).replace(day=1) - dt.timedelta(days=1)


def future_days(last, until):
    out, d = [], last
    while True:
        d += dt.timedelta(days=1)
        if d > until:
            return out
        if not is_last_day(d):
            out.append(d)


def keyed(vals, s, L):
    """Boundary [s, s+L) ke link: (i, a, j, b) = pehle cell (i-ve box, location a) aur doosra cell (j-ve box, location b) me wahi number/palat."""
    out, N = {}, len(vals)
    for i in range(L):
        if s + i >= N:
            break
        for j in range(i, L):
            if s + j >= N:
                break
            for a in range(4):
                for b in range(4):
                    if (i == j and a >= b) or cls(vals[s + i][a]) != cls(vals[s + j][b]):
                        continue
                    out[(i, a, j, b)] = 1
    return out


def indicator(vals, a, b, c, L, N, avoid):
    """Teeno boundary me aaya EK number (palat valid); har boundary me sirf ek cell."""
    wins = [range(a, a + L), range(b, b + L), range(c, min(N, c + L))]
    cnts = []
    for w in wins:
        d = {}
        for r in w:
            for v in vals[r]:
                d[cls(v)] = d.get(cls(v), 0) + 1
        cnts.append(d)
    common = set(cnts[0]) & set(cnts[1]) & set(cnts[2])
    if not common:
        return None
    k = sorted(common, key=lambda x: (sum(d[x] for d in cnts), x))[0]
    cells = []
    for w in wins:
        pick = None
        for r in w:
            for g in range(4):
                if cls(vals[r][g]) == k and (pick is None or pick in avoid) and (r, g) not in avoid:
                    pick = (r, g)
            if pick and pick not in avoid:
                break
        cells.append(pick)
    return k, cells


def analyse(vals, a, b, c, L):
    N = len(vals)
    ka, kb = keyed(vals, a, L), keyed(vals, b, L)
    common = sorted(set(ka) & set(kb))
    if len(common) < 2:
        return None
    present, pend, pend2, found = [], [], [], {}
    for k in common:
        i, aa, j, bb = k
        if c + i >= N:
            pend2.append(k)
            continue
        first = cls(vals[c + i][aa])
        hit = None                      # Step 3: wahi number boundary ke andar KISI BHI location me aa jaye
        if i == j:                      # flat link (usi din doosri location): usi row me aage ki location bhi boundary ke andar hai
            for g in range(aa + 1, 4):
                if cls(vals[c + i][g]) == first:
                    hit = (c + i, g)
                    break
        for rr in ([] if hit else range(c + i + 1, min(N - 1, c + L - 1) + 1)):
            for g in range(4):
                if cls(vals[rr][g]) == first:
                    hit = (rr, g)
                    break
            if hit:
                break
        if hit:
            present.append(k)
            found[k] = hit
        elif c + L - 1 > N - 1:
            pend.append((k, first))
    avoid = set()
    for k in common:
        i, aa, j, bb = k
        for s in (a, b):
            avoid |= {(s + i, aa), (s + j, bb)}
        if k in present:
            avoid |= {(c + i, aa), found[k]}
    return {"L": L, "a": a, "b": b, "c": c, "common": common, "present": present, "found": found, "pend": pend, "pend2": pend2,
            "ind": indicator(vals, a, b, c, L, N, avoid), "end_idx": c + L - 1}


def months_of(D):
    last = D[-1]
    cur = (last.year, last.month)
    p1 = (cur[0] - (cur[1] == 1), 12 if cur[1] == 1 else cur[1] - 1)
    p2 = (p1[0] - (p1[1] == 1), 12 if p1[1] == 1 else p1[1] - 1)
    idx = lambda ym: [i for i, d in enumerate(D) if (d.year, d.month) == ym]
    return idx(p2), idx(p1), idx(cur)


def find(rows, Ls=(8, 10, 12), top=8):
    D = [r[0] for r in rows]
    vals = [r[1] for r in rows]
    N = len(vals)
    i2, i1, i0 = months_of(D)
    if len(i2) < 12 or len(i1) < 12 or len(i0) < 3:
        return []
    rem = future_days(D[-1], month_end(D[-1]))
    best = {}
    for L in Ls:
        kb = {y: keyed(vals, y, L) for y in range(i1[0], i1[-1] - L + 2)}
        for x in range(i2[0], i2[-1] - L + 2):
            kx = keyed(vals, x, L)
            if len(kx) < 2:
                continue
            for y, ky in kb.items():
                if len(set(kx) & set(ky)) < 2:
                    continue
                for c in range(i0[0], N):
                    if c + L - 1 < N - 1 or c + L - 1 > N - 1 + len(rem):
                        continue
                    r = analyse(vals, x, y, c, L)
                    if not r or not (r["present"] or r["pend"] or r["pend2"]):
                        continue
                    sc = (len(r["common"]), c + L - 1 > N - 1, len(r["present"]) + len(r["pend"]), r["ind"] is not None)
                    if (L, x, y) not in best or sc > best[(L, x, y)][0]:
                        best[(L, x, y)] = (sc, r)
    out = []
    for sc, r in sorted(best.values(), key=lambda t: t[0], reverse=True):
        if all(r["L"] != q["L"] or abs(r["a"] - q["a"]) > 3 or abs(r["b"] - q["b"]) > 3 for q in out):
            out.append(r)
        if len(out) >= top:
            break
    return out


def paint(r, vals):
    """Rang: har window ke link cell ek rang; Step 3 ke adhure link ke '?' box; indicator (laal) ek cell."""
    starts = [r["a"], r["b"], r["c"]]
    colour = [{}, {}, {}]
    for n, k in enumerate(r["common"]):
        col = COLS[n % len(COLS)]
        i, aa, j, bb = k
        for w in range(2):
            colour[w][(starts[w] + i, aa)] = col
            colour[w][(starts[w] + j, bb)] = col
        if k in r["present"]:
            colour[2][(r["c"] + i, aa)] = col
            colour[2][r["found"][k]] = col
    pend = {}
    for k, cl in r["pend"]:
        col = COLS[r["common"].index(k) % len(COLS)]
        i, aa, j, bb = k
        colour[2][(r["c"] + i, aa)] = col
        if r["c"] + j >= len(vals):     # beet chuki tarikh par asli number ke upar '?' nahi likhna
            pend[(r["c"] + j, bb)] = (col, "%02d?" % cl if cl == pal(cl) else "%02d/%02d?" % (cl, pal(cl)))
    for k in r["pend2"]:
        col = COLS[r["common"].index(k) % len(COLS)]
        i, aa, j, bb = k
        pend[(r["c"] + i, aa)] = (col, "?")
        pend[(r["c"] + j, bb)] = (col, "?")
    ind = {c for c in (r["ind"][1] if r["ind"] else []) if c}
    return starts, colour, pend, ind


def light(c):
    r, g, b = (int(c[i:i + 2], 16) for i in (0, 2, 4))
    return "%02X%02X%02X" % tuple(int(x + (255 - x) * 0.6) for x in (r, g, b))


# ------------------------------------------------------------------ Excel (ek lambi sheet + har design ki alag sheet)
def to_excel(res, rows, path):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    thin = Side(style="thin", color="777777")
    box, cen = Border(left=thin, right=thin, top=thin, bottom=thin), Alignment(horizontal="center", vertical="center")
    thick = Side(style="medium", color="000000")
    D = [r[0] for r in rows]
    vals = [r[1] for r in rows]
    N = len(vals)
    fut = future_days(D[-1], month_end(D[-1]))
    wb = Workbook()
    wb.remove(wb.active)
    for no, r in enumerate(res, 1):
        ws = wb.create_sheet(f"Pattern {no}")
        starts, colour, pend, ind = paint(r, vals)
        L = r["L"]
        ws["A1"] = f"Pattern {no}: {L} box boundary. Step 1 upar, Step 2 beech, Step 3 neeche (adhura). Ek link = ek rang, laal = indicator, halka '?' = aane wala."
        ws["A1"].font = Font(bold=True)
        for j, h in enumerate(("Tarikh",) + GAMES + ("Step",)):
            c = ws.cell(3, 1 + j, h)
            c.font, c.fill, c.alignment, c.border = Font(bold=True, color="FFFFFF"), PatternFill("solid", fgColor="44546A"), cen, box
        stepof = {}
        for w in range(3):
            for i in range(L):
                stepof[starts[w] + i] = (w + 1, i)
        first_m = (D[r["a"]].year, D[r["a"]].month)
        idxs = [i for i, d in enumerate(D) if (d.year, d.month) >= first_m]
        last_idx = max(idxs[-1], r["c"] + L - 1)
        rr = 4
        for idx in range(idxs[0], last_idx + 1):
            known = idx < N
            dd = D[idx] if known else fut[idx - N]
            w = stepof.get(idx)
            ws.cell(rr, 1, dd.strftime("%d-%b-%Y")).font = Font(bold=True, color="0B5394")
            for g in range(4):
                c = ws.cell(rr, 2 + g)
                c.border, c.alignment = box, cen
                if known:
                    c.value, c.number_format, c.font = vals[idx][g], "00", Font(bold=True, color="000000")
                wi = (w[0] - 1) if w else 2
                if (idx, g) in colour[wi]:
                    c.fill = PatternFill("solid", fgColor=colour[wi][(idx, g)])
                if wi == 2 and (idx, g) in pend:
                    c.value, c.fill = pend[(idx, g)][1], PatternFill("solid", fgColor=light(pend[(idx, g)][0]))
                    c.font = Font(bold=True, italic=True, size=9)
                if (idx, g) in ind and known:
                    if c.fill.fill_type != "solid":
                        c.fill = PatternFill("solid", fgColor=RED)
                    else:
                        c.border = Border(left=Side(style="thick", color=RED), right=Side(style="thick", color=RED), top=Side(style="thick", color=RED), bottom=Side(style="thick", color=RED))
            if w:
                ws.cell(rr, 6, f"STEP {w[0]}" + (" (start)" if w[1] == 0 else " (end)" if w[1] == L - 1 else "")).font = Font(bold=True)
            ws.cell(rr, 1).border = box
            rr += 1
        ws.column_dimensions["A"].width = 14
        for col in "BCDE":
            ws.column_dimensions[col].width = 8
        ws.column_dimensions["F"].width = 16
        ws.freeze_panes = "A4"
    wb.save(path)


# ------------------------------------------------------------------ PDF (teen block side-by-side + link ki list)
def to_pdf(res, rows, path):
    from PIL import Image, ImageDraw, ImageFont

    def font(sz, bold=False):
        for d in ("/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/dejavu", "/system/fonts"):
            for nm in (("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), ("Roboto-Bold.ttf" if bold else "Roboto-Regular.ttf")):
                p = os.path.join(d, nm)
                if os.path.exists(p):
                    return ImageFont.truetype(p, sz)
        return ImageFont.load_default()
    D = [r[0] for r in rows]
    vals = [r[1] for r in rows]
    N = len(vals)
    fut = future_days(D[-1], month_end(D[-1]))
    pages = []
    for no, r in enumerate(res, 1):
        img = Image.new("RGB", (1240, 1754), "white")
        d = ImageDraw.Draw(img)
        starts, colour, pend, ind = paint(r, vals)
        L = r["L"]
        d.text((40, 30), f"Pattern {no}: Step 1 | Step 2 | Step 3 (adhura), boundary {L} box", font=font(26, True), fill="#111")
        ys = []
        for w in range(3):
            x0, y = 40 + w * 395, 90
            d.text((x0, y), ("STEP 1", "STEP 2", "STEP 3")[w], font=font(20, True), fill="#111")
            y += 34
            for i in range(L):
                idx = starts[w] + i
                known = idx < N
                dd = D[idx] if known else fut[idx - N]
                d.rectangle([x0, y, x0 + 92, y + 34], outline="#777")
                d.text((x0 + 6, y + 6), dd.strftime("%d %b"), font=font(18, True), fill="#0B5394")
                for g in range(4):
                    xx = x0 + 92 + g * 66
                    fill = "white"
                    if (idx, g) in colour[w]:
                        fill = "#" + colour[w][(idx, g)]
                    txt = "%02d" % vals[idx][g] if known else ""
                    if w == 2 and (idx, g) in pend:
                        fill, txt = "#" + light(pend[(idx, g)][0]), pend[(idx, g)][1]
                    d.rectangle([xx, y, xx + 66, y + 34], fill=fill, outline="#777")
                    if (idx, g) in ind and known:
                        d.rectangle([xx + 2, y + 2, xx + 64, y + 32], outline="#" + RED, width=4) if fill != "white" else d.rectangle([xx + 1, y + 1, xx + 65, y + 33], fill="#" + RED)
                    d.text((xx + 12, y + 7), txt, font=font(18, True), fill="black")
                y += 34
            ys.append(y)
        y = max(ys) + 30
        for n, k in enumerate(r["common"]):
            d.rectangle([40, y, 80, y + 30], fill="#" + COLS[n % len(COLS)], outline="#555")
            d.text((92, y + 4), f"Link {n + 1}: boundary ke {k[0] + 1}-ve box ki {GAMES[k[1]]} -> {k[2] - k[0]} box baad {GAMES[k[3]]} (wahi number/palat)", font=font(16), fill="#111")
            y += 34
        if r["ind"]:
            d.rectangle([40, y, 80, y + 30], fill="#" + RED, outline="#555")
            d.text((92, y + 4), f"Indicator {r['ind'][0]:02d}/{pal(r['ind'][0]):02d}: har boundary me ek cell", font=font(16), fill="#111")
        pages.append(img)
    if pages:
        pages[0].save(path, "PDF", save_all=True, append_images=pages[1:], resolution=150)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Puzzle-Steps: 3 mahine ek sheet par step 1/2/3 ka design (Excel + PDF)")
    ap.add_argument("csv")
    ap.add_argument("--out", default=".")
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--L", default="8,10,12")
    a = ap.parse_args(argv)
    rows = load(a.csv)
    res = find(rows, tuple(int(x) for x in a.L.split(",")), a.top)
    if not res:
        print("Koi design nahi mila (current mahine me kam din ya pichle 2 mahine poore nahi).")
        return 1
    os.makedirs(a.out, exist_ok=True)
    xp, pp = os.path.join(a.out, "puzzle_steps.xlsx"), os.path.join(a.out, "puzzle_steps.pdf")
    to_excel(res, rows, xp)
    to_pdf(res, rows, pp)
    print(len(res), "design ->", xp, pp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
