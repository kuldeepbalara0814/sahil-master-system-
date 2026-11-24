"""Pattern Scan: ek pattern ka saaf rang wala chart (app me dikhane ke liye) aur wahi Excel me."""
import calendar
import datetime as dt
import io

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

from . import band, data, scanner
from .scanner import GAMES, pal

LIGHT = {"FF9800": "FFE0B2", "AB47BC": "E1BEE7", "66BB6A": "C8E6C9", "EF5350": "FFCDD2", "26C6DA": "B2EBF2", "F06292": "F8BBD0", "8D6E63": "D7CCC8", "9CCC65": "DCEDC8",
         "00E676": "C8F7DC", "FF4FA3": "FFD0E6"}


def _lt(c):
    """Rang ka halka roop (safed me milakar)."""
    if c in LIGHT:
        return LIGHT[c]
    r, g, b = (int(c[i:i + 2], 16) for i in (0, 2, 4))
    return "%02X%02X%02X" % tuple(int(x + (255 - x) * 0.6) for x in (r, g, b))


def _row(date, v=None, c=None, kind=None, txt=None):
    return {"date": date, "v": v, "c": c or [None] * 4, "kind": kind or [None] * 4, "txt": txt or [None] * 4}


def view(rows, pid, partial=None):
    """pid: 'naksha:L:YYYY-MM-DD' ya 'copy:shape:g:YYYY-MM-DD'."""
    parts = pid.split(":")
    D = [r[0] for r in rows]
    N = len(rows)
    if parts[0] == "ank":
        raise ValueError("009 Ank-Chal ka rang wala chart nahi banta (ye ank ka pattern hai); iska card Active tab me hai")
    if parts[0] == "steps":
        from . import steps
        return steps.view(rows, pid, partial)
    if parts[0] in ("naksha", "naksha2"):
        mode = "r" if parts[0] == "naksha2" else "n"
        L, so = int(parts[1]), D.index(dt.date.fromisoformat(parts[2]))
        sc, F = N - L, 8
        info = scanner.match_info(rows, so, sc, L, mode)
        colour = {}
        for k in info["comps"]:
            for x in k["cells"]:
                colour[x] = k["color"]
        olds, news = [], []
        fut, dd = [], D[-1]                                  # naye mahine ke aane wale din (chhuti chhodkar)
        while len(fut) < F:
            dd += dt.timedelta(days=1)
            if not data.is_last_day(dd):
                fut.append(dd)
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
                                c[g], kind[g] = _lt(k["color"]), "light"
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
                                c[g], kind[g], txt[g] = _lt(k["color"]), "light", "?"
                news.append(_row(fut[i - L].isoformat(), None, c, kind, txt))   # aage ki jagah asli tarikh
        tg = "; ".join(f"{t['game']} me {' / '.join(f'{x:02d}' for x in t['numbers'])}" for t in info["targets"]) or "koi andaza nahi"
        return {"id": pid, "title": f"{scanner.name_for('Naksha-Rashi' if mode == 'r' else 'Naksha', f'{L}:{D[so].isoformat()}')}: {D[so]:%b %Y} jaisa naksha" + (" (rashi)" if mode == "r" else ""),
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
    if parts[0] == "family":
        rashi, shape, d0 = int(parts[1]), parts[2], dt.date.fromisoformat(parts[3])
        today = data.play_date(rows)
        ev = [e for e in scanner.family_events(rows, d0, d0, today) if e["rashi"] == rashi and e["shape"] == shape]
        if not ev:
            raise ValueError("Ye family pattern nahi mili")
        e = ev[0]
        st = set(e["numbers"])
        i0 = D.index(e["d"])
        out = []
        for k in range(i0, i0 + 4):
            if k < N:
                c, kind = [None] * 4, [None] * 4
                for g in range(4):
                    if rows[k][1][g] in st:
                        if D[k] in (e["d"], e["j"]):
                            c[g], kind[g] = "FF9800", "step"
                        elif D[k] == e["t"]:
                            c[g], kind[g] = "FF4FA3", "pass"
                out.append(_row(D[k].isoformat(), [int(x) for x in rows[k][1]], c, kind))
            else:
                out.append(_row(e["t"].isoformat(), None, [LIGHT["FF4FA3"]] * 4, ["light"] * 4, ["?"] * 4))
        fam = " ".join(f"{x:02d}" for x in e["numbers"])
        key = f"{rashi}:{shape}:{d0.isoformat()}"
        return {"id": pid, "title": f"{scanner.name_for('Family', key)}: {rashi:02d} rashi {shape}",
                "note": f"Narangi = step 1 aur 2 (family ke cell). Gulabi = 3rd step par family ka number aaya (PASS). '?' = 3rd step ka din abhi baaki. Family: {fam}.",
                "blocks": [{"label": "Step 1 se 3rd step", "rows": out}]}
    if parts[0] == "dana":
        from . import dana_farak as dfk
        kind = parts[1]
        (d1, g1), (d2, g2) = [(dt.date.fromisoformat(x[:10]), int(x[11:])) for x in parts[2:4]]
        ev = [e for e in dfk.events(rows, d1, d1) if e["kind"] == kind and e["c1"][:2] == (d1, g1) and e["c2"][:2] == (d2, g2)]
        if not ev:
            raise ValueError("Ye dana-farak pair nahi mila")
        e = ev[0]
        byd = {r[0]: r[1] for r in rows}
        out = []
        for k in range(4):
            d = d1 + dt.timedelta(days=k)
            if d in byd:
                c, kd = [None] * 4, [None] * 4
                for g in range(4):
                    cell = (d, g)
                    if cell in ((d1, g1), (d2, g2)):
                        c[g], kd[g] = "00E676", "step"
                    elif (d, g) > (d2, g2) and byd[d][g] in e["core"]:
                        c[g], kd[g] = "FF4FA3", "pass"
                    elif (d, g) > (d2, g2) and byd[d][g] in e["series"]:
                        c[g], kd[g] = "40C4FF", "pass"
                out.append(_row(d.isoformat(), [int(x) for x in byd[d]], c, kd))
            elif not data.is_last_day(d):
                out.append(_row(d.isoformat(), None, [LIGHT["FF4FA3"]] * 4, ["light"] * 4, ["?"] * 4))
            else:
                out.append(_row(d.isoformat() + " chhuti"))
        core = " ".join(f"{x:02d}" for x in e["core"])
        sr = " ".join(f"{x:02d}" for x in e["series"])
        return {"id": pid, "title": f"Dana-Farak {e['c1'][2]:02d} + {e['c2'][2]:02d} ({e['kind']}): 4 din box",
                "note": f"Hara = pair ke do number. Gulabi = khelne ka number aaya (PASS). Neela = series ka number (part 2). Khelo: {core}. Series spot: {sr or '-'}." + (" " + dfk.NOTE if e["amb"] else ""),
                "blocks": [{"label": f"Din 1 ({d1:%d %b}) se din 4", "rows": out}]}
    raise ValueError("Pattern id samajh nahi aayi")


def fill_sheet(ws, v):
    """view() ka chart ek worksheet me bharo (rang, border, 'pass' moti border)."""
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
            ws.cell(rr, col, r["date"] and (dt.date.fromisoformat(r["date"][:10]).strftime("%d-%b-%y") + (" chhuti" if len(r["date"]) > 10 else ""))).alignment = cen
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
            ws.column_dimensions[ws.cell(1, col + j).column_letter].width = 15 if j == 0 else 6
        col += 6


def xlsx(rows, pid):
    v = view(rows, pid)
    wb = Workbook()
    ws = wb.active
    ws.title = "Pattern"
    fill_sheet(ws, v)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue(), v["title"]


FAM_COLORS = ["FFB74D", "CE93D8", "80DEEA", "A5D6A7", "EF9A9A", "FFF176", "90CAF9", "BCAAA4", "F48FB1", "C5E1A5", "FFCC80", "B39DDB", "80CBC4", "E6EE9C", "B0BEC5"]


def family_month(rows, pid):
    """Family pattern ka poora mahina: har rashi family alag rang, is pattern ke cell bold. Saath me 'ye kaise bana' ki baat."""
    parts = pid.split(":")
    if parts[0] != "family":
        raise ValueError("Ye sirf family pattern ke liye hai")
    rashi, shape, d0 = int(parts[1]), parts[2], dt.date.fromisoformat(parts[3])
    today = data.play_date(rows)
    ev = [e for e in scanner.family_events(rows, d0, d0, today) if e["rashi"] == rashi and e["shape"] == shape]
    if not ev:
        raise ValueError("Ye family pattern nahi mili")
    e = ev[0]
    by = {d: v for d, v, _ in rows}
    fams = []
    fam_idx = {}
    for i, (k, nums) in enumerate(sorted(band.RASHIS.items(), key=lambda kv: kv[1][0])):
        for n in nums:
            fam_idx[n] = i
        fams.append({"rashi": nums[0], "name": f"{nums[0]:02d} rashi" + (" (jodi)" if len(nums) == 4 else ""), "numbers": sorted(nums), "color": FAM_COLORS[i % len(FAM_COLORS)]})
    yms = sorted({x.strftime("%Y-%m") for x in (e["d"], e["j"], e["t"])})
    months, cellfam = {}, {}
    for ym in yms:
        y, m = int(ym[:4]), int(ym[5:])
        days = []
        for d in range(1, calendar.monthrange(y, m)[1] + 1):
            dd = dt.date(y, m, d)
            v = by.get(dd)
            days.append([dd.isoformat(), v])
            if v:
                for g in range(4):
                    cellfam[f"{dd.isoformat()}|{g}"] = fam_idx[v[g]]
        months[ym] = {"label": f"{calendar.month_abbr[m]} {y}", "days": days}
    sel = []
    for day, cols in ((e["d"], e["c1"]), (e["j"], e["c2"])):
        for g in cols:
            sel.append({"date": day.isoformat(), "g": g, "kind": "step", "text": ""})
    if e["status"] == "aaj":
        for g in range(4):
            sel.append({"date": e["t"].isoformat(), "g": g, "kind": "target", "text": "?"})
    else:
        for g, _ in e["hit"]:
            sel.append({"date": e["t"].isoformat(), "g": g, "kind": "pass", "text": ""})
    nums = set(e["numbers"])
    seen = [(d, [(GAMES[g], v) for g, v in enumerate(by[d]) if v in nums]) for d in sorted(by) if e["d"] - dt.timedelta(days=e["d"].day - 1) <= d <= rows[-1][0] and any(v in nums for v in by[d])]
    timeline = [f"{d:%d %b}: " + ", ".join(f"{g} {v:02d}" for g, v in hs) for d, hs in seen]
    gap = (e["j"] - e["d"]).days
    expl = [f"{rashi:02d} rashi ki family: " + " ".join(f"{x:02d}" for x in e["numbers"]) + ".",
            f"Step 1: {e['d']:%d %b} ({', '.join(GAMES[g] for g in e['c1'])}). Step 2: {e['j']:%d %b} ({', '.join(GAMES[g] for g in e['c2'])}), step 1 se {gap} din baad.",
            f"Design {e['shape']}: din 0, +{gap}, +3. Isliye 3rd step {e['t']:%d %b} par banta hai" + (" (aaj, abhi baaki)." if e["status"] == "aaj" else f" ({'PASS' if e['hit'] else 'FAIL'})."),
            ]
    if e["amb"]:
        expl.append("Step ke din family ke ek se zyada cell hain, isliye location software tay nahi karta, aap tay karo.")
    expl.append("Is mahine ye rashi in dino me aayi (neeche list), isliye ye design bana:")
    return {"id": pid, "title": f"{scanner.name_for('Family', f'{rashi}:{shape}:{d0.isoformat()}')}: {rashi:02d} rashi {shape}",
            "months": months, "families": fams, "cellfam": cellfam, "sel": sel, "sel_family": fam_idx[rashi], "explain": expl, "timeline": timeline,
            "status": e["status"]}


def family_month_xlsx(rows, pid):
    v = family_month(rows, pid)
    wb = Workbook()
    ws = wb.active
    ws.title = "Pattern"
    thin = Side(style="thin", color="888888")
    box = Border(left=thin, right=thin, top=thin, bottom=thin)
    cen = Alignment(horizontal="center", vertical="center")
    ws["A1"] = v["title"]
    ws["A1"].font = Font(bold=True, size=13)
    for i, t in enumerate(v["explain"], 2):
        ws.cell(i, 1, t)
    r0 = len(v["explain"]) + 3
    selk = {(c["date"], c["g"]): c for c in v["sel"]}
    col = 1
    for ym, mo in v["months"].items():
        ws.cell(r0, col, mo["label"].upper()).font = Font(bold=True, size=14)
        for j, h in enumerate(["Tarikh", *GAMES]):
            c = ws.cell(r0 + 1, col + j, h)
            c.font, c.alignment, c.fill = Font(bold=True, color="FFFFFF"), cen, PatternFill("solid", fgColor="37474F")
        for i, (iso, vals) in enumerate(mo["days"]):
            rr = r0 + 2 + i
            ws.cell(rr, col, dt.date.fromisoformat(iso).strftime("%d-%b-%y")).alignment = cen
            for g in range(4):
                sc = selk.get((iso, g))
                cell = ws.cell(rr, col + 1 + g, (sc["text"] if sc and sc["text"] else (None if vals is None else vals[g])))
                cell.alignment, cell.border, cell.number_format = cen, box, "00"
                fi = v["cellfam"].get(f"{iso}|{g}")
                if fi is not None:
                    cell.fill = PatternFill("solid", fgColor=v["families"][fi]["color"])
                cell.font = Font(bold=bool(sc), color="000000" if fi is not None or sc else "333333")
                if sc:
                    s2 = Side(style="thick", color="000000")
                    cell.border = Border(left=s2, right=s2, top=s2, bottom=s2)
        col += 6
    lr = r0 + 2 + max(len(m["days"]) for m in v["months"].values()) + 1
    ws.cell(lr, 1, "Family ke rang:").font = Font(bold=True)
    for i, f in enumerate(v["families"]):
        c = ws.cell(lr + 1 + i, 1, f["name"])
        c.fill = PatternFill("solid", fgColor=f["color"])
        ws.cell(lr + 1 + i, 2, " ".join(f"{x:02d}" for x in f["numbers"]))
    for j in range(2, 16):
        ws.column_dimensions[ws.cell(1, j).column_letter].width = 7
    ws.column_dimensions["A"].width = 14
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue(), v["title"]
