"""Copy pattern (patterns/001) ko kisi bhi range par dhoondh kar Excel me rang se dikhao.
Chalao: python scripts/copy_pattern_demo.py 2026-05-01 2026-08-31 out.xlsx
Hara = jodi ke do number, gulabi = din4 par set ka number aaya (PASS). Fail wali jodi sirf hari rehti hai."""
import datetime as dt, io, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT)
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill
from lab import data, export_xlsx
G = ["FB", "GB", "GL", "DS"]
pal = lambda n: (n % 10) * 10 + n // 10
def nb(v): return {x for x in (v-1, v+1, v-10, v+10) if 0 <= x <= 99}
def copy(x, y): return y not in (x, pal(x)) and (y in nb(x) or y in nb(pal(x)))

def find(rows, a, b):
    D = [r[0] for r in rows]; R = [r[1] for r in rows]; ev = []
    for d in range(len(rows)):
        if not (a <= D[d] <= b): continue
        for shape, off in (("seedha", 1), ("ulta", 2)):
            j, t = d + off, d + 3
            if t >= len(rows) or D[t] > b: continue
            if not all(data.adjacent(D[k], D[k+1]) for k in range(d, t)): continue
            for g in range(4):
                x, y = R[d][g], R[j][g]
                if copy(x, y):
                    S = {x, y, pal(x), pal(y)}
                    hit = [(k, R[t][k]) for k in range(4) if R[t][k] in S]
                    ev.append(dict(shape=shape, d=D[d], j=D[j], t=D[t], g=g, x=x, y=y, S=sorted(S), hit=hit))
    return ev

def build(a, b, out):
    rows = data.load()
    ev = find(rows, a, b)
    wb = load_workbook(io.BytesIO(export_xlsx.build(rows, a, b)))
    ws = wb["Record"]
    pos, r0 = {}, 1
    for y in sorted({r[0].year for r in rows if a <= r[0] <= b}):
        ms = sorted({r[0].month for r in rows if r[0].year == y and a <= r[0] <= b})
        for m in ms: pos[(y, m)] = (r0, 2 + 4 * ms.index(m))
        r0 += 36
    def paint(d, g, color):
        r, c = pos[(d.year, d.month)]
        cell = ws.cell(r + 2 + d.day, c + g); cell.fill = PatternFill("solid", fgColor=color); cell.font = Font(bold=True, color="000000")
    for e in ev:
        paint(e["d"], e["g"], "00E676"); paint(e["j"], e["g"], "00E676")
        for k, _ in e["hit"]: paint(e["t"], k, "FF4FA3")
    L = wb.create_sheet("Pattern list", 0)
    L.append(["Rang: HARA = jodi ke 2 number (ek hi game), GULABI = din4 par set ka number aaya (PASS). Sirf hara = FAIL."]); L.append([])
    L.append(["Shape", "Din1", "Din2/3", "Din4", "Game", "Jodi", "Set (4 jodi)", "Din4 par aaya", "Natija"])
    for e in ev:
        L.append([e["shape"], e["d"].isoformat(), e["j"].isoformat(), e["t"].isoformat(), G[e["g"]], f"{e['x']:02d} & {e['y']:02d}",
                  " ".join(f"{s:02d}" for s in e["S"]), ", ".join(f"{G[k]}:{n:02d}" for k, n in e["hit"]) or "-", "PASS" if e["hit"] else "fail"])
    for col, w in zip("ABCDEFGHI", (9, 12, 12, 12, 7, 10, 18, 22, 8)): L.column_dimensions[col].width = w
    L.column_dimensions["A"].width = 12
    wb.active = 1; wb.save(out)
    ps = sum(1 for e in ev if e["hit"]); print(len(ev), "bane,", ps, "PASS,", len(ev) - ps, "fail ->", out)

if __name__ == "__main__":
    build(dt.date.fromisoformat(sys.argv[1]), dt.date.fromisoformat(sys.argv[2]), sys.argv[3])


def one(ev, out, title):
    """Ek hi pattern, sirf us ke mahine, saaf rang. (aap ki maang: chhote tukde, ek ya do pattern per Excel)"""
    import calendar
    rows = data.load()
    a = ev["d"].replace(day=1); last = ev["t"]
    b = last.replace(day=calendar.monthrange(last.year, last.month)[1])
    wb = load_workbook(io.BytesIO(export_xlsx.build(rows, a, b)))
    ws = wb["Record"]
    ms = sorted({(r[0].year, r[0].month) for r in rows if a <= r[0] <= b})
    pos = {m: (1 + 36 * [y for y in sorted({k[0] for k in ms})].index(m[0]), 2 + 4 * [k[1] for k in ms if k[0] == m[0]].index(m[1])) for m in ms}
    def paint(d, g, color):
        r, c = pos[(d.year, d.month)]
        cell = ws.cell(r + 2 + d.day, c + g); cell.fill = PatternFill("solid", fgColor=color); cell.font = Font(bold=True, color="000000")
    paint(ev["d"], ev["g"], "00E676"); paint(ev["j"], ev["g"], "00E676")
    for k, _ in ev["hit"]: paint(ev["t"], k, "FF4FA3")
    L = wb.create_sheet("Samjho", 0)
    L.column_dimensions["A"].width = 110
    lines = [title, "", f"Shape: {ev['shape']}  |  Game: {G[ev['g']]}",
             f"HARA: {ev['d']} aur {ev['j']} ko {G[ev['g']]} me {ev['x']:02d} aur {ev['y']:02d} (jodi, copy)",
             "Set (4 jodi): " + " ".join(f"{s:02d}" for s in ev["S"]) + "  (dono number + dono ke palat)",
             f"Din4 = {ev['t']}: " + (("GULABI = set ka number aaya -> PASS: " + ", ".join(f"{G[k]} {n:02d}" for k, n in ev["hit"])) if ev["hit"] else "set ka koi number nahi aaya -> FAIL (kuch gulabi nahi)")]
    for l in lines: L.append([l])
    wb.active = 1; wb.save(out)
