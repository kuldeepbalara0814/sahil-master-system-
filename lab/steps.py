"""007 Puzzle-Steps: 3 mahine ek lambi sheet par step 1 / step 2 / step 3 ka design (patterns/007_puzzle_steps/README.md).

Step 1 = (current mahine - 2) ki boundary, Step 2 = (current mahine - 1) ki boundary, Step 3 = current mahine ki boundary (abhi adhuri).
Boundary = design ke pehle cell se aakhri cell tak box (row) ginti, dono sire samet; har step me wahi boundary (L box).
Link = (repeat: wahi number ya palat, boundary ke pehle cell se i-ve box ki location a  ->  j-ve box ki location b). Jo link step 1 me wahi step 2 me, wahi jagah.
Ek link = ek rang. Indicator = ek hi number (laal), har boundary me kahin bhi. Sirf paas ka data; ye khoj hai, pakka pattern nahi.
"""
import datetime as dt

from . import data, partial as partial_mod

GAMES = ("FB", "GB", "GL", "DS")
COLS = ["FFB74D", "CE93D8", "80DEEA", "A5D6A7", "F48FB1", "FFF176", "90CAF9", "BCAAA4"]
RED = "FF5252"
LS = (8, 10, 12)


def cls(n):
    if n is None:                       # aadhi line me abhi na aaya hua game: kisi se mel nahi khata
        return -1
    return min(n, (n % 10) * 10 + n // 10)


def pal(n):
    return (n % 10) * 10 + n // 10


def _keyed(vals, s, L):
    """boundary [s, s+L) ke repeat link: {(i, a, j, b): ((row1, a), (row2, b))}. Sirf jaha dono cell maujood."""
    out, N = {}, len(vals)
    for i in range(L):
        if s + i >= N:
            break
        for j in range(i, L):
            if s + j >= N:
                break
            for a in range(4):
                for b in range(4):
                    if i == j and a >= b:
                        continue
                    if cls(vals[s + i][a]) == cls(vals[s + j][b]):
                        out[(i, a, j, b)] = ((s + i, a), (s + j, b))
    return out


def future_days(last, until):
    """last ke baad ke kaam ke din until tak (mahine ka aakhri din chhuti)."""
    out, d = [], last
    while True:
        d += dt.timedelta(days=1)
        if d > until:
            return out
        if not data.is_last_day(d):
            out.append(d)


def _month_end(d):
    return (d.replace(day=28) + dt.timedelta(days=4)).replace(day=1) - dt.timedelta(days=1)


def _prev_ym(ym):
    return (ym[0] - (ym[1] == 1), 12 if ym[1] == 1 else ym[1] - 1)


def _months(D, ym=None):
    cur = ym or (D[-1].year, D[-1].month)
    prev1 = _prev_ym(cur)
    prev2 = _prev_ym(prev1)
    idx = lambda m: [i for i, d in enumerate(D) if (d.year, d.month) == m]
    return idx(prev2), idx(prev1), idx(cur)


FUT_EXTRA = 16      # din: Step 3 ki boundary mahine ke aakhir ke baad agle mahine tak bhi chal sakti hai (12 box ~ 14 din)


def _fut(last):
    """last ke baad ke kaam ke din: mahine ke aakhir ke baad agle mahine me bhi (boundary aage chalti rahe)."""
    return future_days(last, _month_end(last) + dt.timedelta(days=FUT_EXTRA))


def _indicator(vals, a, b, c, L, N, avoid):
    """Teeno boundary me aaya ek hi number (class). Har boundary me sirf EK cell (pehla). -> (cls, [cell, cell, cell]) ya None."""
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
                if cls(vals[r][g]) == k:
                    if (r, g) not in avoid:
                        pick = (r, g)
                        break
                    pick = pick or (r, g)
            if pick and pick not in avoid:
                break
        cells.append(pick)
    return k, cells


def analyse(vals, D, a, b, c, L, part=False):
    """Ek (a, b, c, L) ka poora hisaab."""
    N = len(vals)
    ka, kb = _keyed(vals, a, L), _keyed(vals, b, L)
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
        if first == -1:                                          # pehla cell aadhi line ka abhi-na-aaya game: dono cell aage
            pend2.append(k)
            continue
        hit = None                                               # Step 3: wahi number boundary ke andar KISI BHI location me aa jaye (user ne tay kiya)
        if i == j:                                               # flat link (usi din doosri location): usi row me aage ki location bhi boundary ke andar hai
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
        elif (c + L - 1 >= N - 1) if part else (c + L - 1 > N - 1):      # boundary abhi khuli (aadhi line ho to uski tarikh par bhi)
            pend.append((k, first))
    link_cells = set()
    for n, k in enumerate(common):
        i, aa, j, bb = k
        for s in (a, b):
            link_cells |= {(s + i, aa), (s + j, bb)}
        if k in present:
            link_cells |= {(c + i, aa), found[k]}
    ind = _indicator(vals, a, b, c, L, N, link_cells)
    end_idx = c + L - 1
    return {"L": L, "a": a, "b": b, "c": c, "common": common, "present": present, "found": found, "pend": pend, "pend2": pend2, "ind": ind, "end_idx": end_idx}


def _windows(rows):
    D = [r[0] for r in rows]
    vals = [list(r[1]) for r in rows]
    i2, i1, i0 = _months(D)
    return D, vals, i2, i1, i0


def _search(vals, D, N, rem, ym, Ls, only, part):
    """Ek window (Step 1/2/3 = ym ke pichle se pichla, pichla, ym) ke saare design: {(L, x, y): (score, r)}."""
    i2, i1, i0 = _months(D, ym)
    if len(i2) < 12 or len(i1) < 12 or len(i0) < 1:
        return {}
    best = {}
    for L in Ls:
        if only and only[0] != L:
            continue
        A = [x for x in range(i2[0], i2[-1] - L + 2)]
        B = [x for x in range(i1[0], i1[-1] - L + 2)]
        lk_b = {y: _keyed(vals, y, L) for y in B}
        for x in A:
            lx = _keyed(vals, x, L)
            if len(lx) < 2:
                continue
            for y in B:
                if only and (only[1], only[2]) != (x, y):
                    continue
                if len(set(lx) & set(lk_b[y])) < 2:
                    continue
                for c in range(i0[0], i0[-1] + 1):                       # Step 3 ki shuruat usi window ke 'current' mahine ke andar
                    if c + L - 1 < N - 1 or c + L - 1 > N - 1 + len(rem):
                        continue
                    r = analyse(vals, D, x, y, c, L, part)
                    if not r or not (r["present"] or r["pend"] or r["pend2"]):
                        continue
                    ended = c + L - 1 < N - 1 if part else c + L - 1 <= N - 1
                    sc = (len(r["common"]), not ended, len(r["present"]) + len(r["pend"]), r["ind"] is not None)
                    key = (L, x, y)
                    if key not in best or sc > best[key][0]:
                        best[key] = (sc, r)
    return best


def _pick(best, top, only):
    out = []
    for sc, r in sorted(best.values(), key=lambda t: t[0], reverse=True):
        if only:
            return [r]
        if all(r["L"] != q["L"] or abs(r["a"] - q["a"]) > 3 or abs(r["b"] - q["b"]) > 3 for q in out):
            out.append(r)
        if len(out) >= top:
            break
    return out


CARRY = 8           # mahina badalne par purani window ke (abhi khule) design jo naye mahine me chal rahe hain (top jitne, taaki beech me gayab na hon)


def find(rows, Ls=LS, top=8, only=None, part=False):
    """-> list of analyse() dict (sabse achhe). Current window ke `top` design + purani window (pichhla mahina 'current' tha) ke wo design
    jinki Step 3 boundary abhi khuli hai aur naye mahine me chal rahi hai (CARRY tak) - taaki PASS/FAIL ka pata lagta rahe."""
    D, vals, i2, i1, i0 = _windows(rows)
    N = len(vals)
    rem = _fut(D[-1])
    cur = (D[-1].year, D[-1].month)
    out = _pick(_search(vals, D, N, rem, cur, Ls, only, part), top, only)
    if only and out:
        return out
    return out + _pick(_search(vals, D, N, rem, _prev_ym(cur), Ls, only, part), CARRY, only)


def pid(r, D):
    return f"steps:{r['L']}:{D[r['a']].isoformat()}:{D[r['b']].isoformat()}"


def parse_pid(p, rows):
    _, L, da, db = p.split(":")
    D = [r[0] for r in rows]
    return int(L), D.index(dt.date.fromisoformat(da)), D.index(dt.date.fromisoformat(db))


def status_of(r, N, part=False):
    ended = r["end_idx"] < N - 1 if part else r["end_idx"] <= N - 1      # aadhi line (DS baaki) ho to boundary uski tarikh par bhi khuli maani jaati hai
    if not ended:
        return "aaj"
    return "pass" if len(r["present"]) == len(r["common"]) else "fail"


def _cd(D, idx, N, fut):
    return D[idx] if idx < N else fut[idx - N]


def item(r, rows, today, part=False):
    D = [x[0] for x in rows]
    vals = [list(x[1]) for x in rows]
    N = len(vals)
    L = r["L"]
    fut = _fut(D[-1])
    st = status_of(r, N, part)
    end_d = _cd(D, r["end_idx"], N, fut)
    lines = [f"Boundary {L} box: Step 1 {D[r['a']]:%d %b} se {D[r['a'] + L - 1]:%d %b}, Step 2 {D[r['b']]:%d %b} se {D[r['b'] + L - 1]:%d %b}, Step 3 {D[r['c']]:%d %b} se {end_d:%d %b}.",
             f"{len(r['common'])} link (wahi number/palat, wahi jagah) Step 1 aur Step 2 dono me mile; Step 3 me (kisi bhi location) {len(r['present'])} mila."]
    tg, hint = [], []
    for k, cl in r["pend"]:
        i, aa, j, bb = k
        dd = _cd(D, r["c"] + j, N, fut)
        nums = sorted({cl, pal(cl)})
        tg.append({"game": GAMES[bb], "numbers": nums})
        unknown = r["c"] + j >= N or (r["c"] + j < N and vals[r["c"] + j][bb] is None)
        qtxt = f"; '?' box {dd:%d %b} {GAMES[bb]} par dikhaya" if unknown else "; (wo din beet chuka, '?' nahi, asli number dikh raha hai)"
        hint.append(f"{'/'.join(f'{x:02d}' for x in nums)} kisi bhi location me boundary ({end_d:%d %b}) tak aana chahiye (andar = PASS, bahar = FAIL)" + qtxt)
    if r["pend2"]:
        hint.append(f"{len(r['pend2'])} link ke dono cell abhi aage ki tarikh me (jamuni '?' box); jab pehla aaye to uska number aur palat agle box ki location me single khelne layak")
    lines += hint
    if r["ind"]:
        k, cells = r["ind"]
        lines.append(f"Indicator (laal): {k:02d}/{pal(k):02d} har boundary me aaya (ek hi cell mark).")
    else:
        lines.append("Indicator: koi ek number teeno boundary me nahi mila (zaroori nahi, pattern phir bhi ban sakta hai).")
    lines.append("Ye khoj hai, pakka pattern nahi: random data me bhi aise 3 link mil jate hai (patterns/007_puzzle_steps/README.md).")
    if st == "pass":
        lines.append("PASS: Step 3 ki boundary me saare link ban gaye.")
    elif st == "fail":
        lines.append("FAIL: boundary poori hui, saare link nahi bane.")
    return {"id": pid(r, D), "kind": "steps", "name": f"Steps-{D[r['a']]:%d%b}-{D[r['b']]:%d%b}-{L}box", "status": st, "strength": "info",
            "title": f"{L} box | {len(r['common'])} link | 3 mahine ({D[r['a']]:%d %b} / {D[r['b']]:%d %b} / {D[r['c']]:%d %b})",
            "lines": lines, "end": end_d.isoformat() if st != "aaj" else None, "targets": tg if st == "aaj" else [],
            "target": {"date": today.isoformat(), "games": ", ".join(sorted({t["game"] for t in tg})) or "jamuni box (aage)", "numbers": sorted({x for t in tg for x in t["numbers"]})} if st == "aaj" and (tg or r["pend2"]) else None}


def scan(rows, asof, partial=None):
    """partial = lab.partial ka dict (aaj ke aa chuke FB/GB/GL) ya None. Aadhi line sirf is scan ke liye judti hai, record me nahi."""
    today = data.play_date(rows)
    part = partial_mod.clean(partial, rows[-1][0]) if partial else None
    prow = [partial_mod.as_row(part)] if part else []
    rows2 = list(rows) + prow
    res = find(rows2, part=bool(prow))
    items = [item(r, rows2, today, bool(prow)) for r in res]
    live = sum(1 for i in items if i["status"] == "aaj")
    extra = f" Aadhi line judi hai ({', '.join(part['results'])} aa chuke)." if part else ""
    summary = (f"3 mahine ek sheet par step 1 (pichle se pichla mahina), step 2 (pichla mahina), step 3 (current): {len(items)} design mile, {live} abhi chal rahe. "
               "Ye khoj hai; random data me bhi aise milan aate hai, isliye pass/fail se parkho." + extra)
    return {"summary": summary, "items": items}


# ---------------------------------------------------------------- view (3 block + ek sheet)
def view(rows, p, partial=None):
    from .scan_view import _row, _lt
    part = partial_mod.clean(partial, rows[-1][0]) if partial else None
    if part:
        try:
            return _view(list(rows) + [partial_mod.as_row(part)], p, True)
        except ValueError:                                       # aadhi line ke saath nahi mila: poori lines se
            pass
    return _view(rows, p, False)


def _view(rows, p, part):
    from .scan_view import _row, _lt
    L, a, b = parse_pid(p, rows)
    res = find(rows, only=(L, a, b), part=part)
    if not res:
        raise ValueError("Ye steps pattern ab nahi mila")
    r = res[0]
    D = [x[0] for x in rows]
    vals = [list(x[1]) for x in rows]
    N = len(vals)
    fut = _fut(D[-1])
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
    for n, (k, cl) in enumerate(r["pend"]):
        col = COLS[r["common"].index(k) % len(COLS)]
        i, aa, j, bb = k
        colour[2][(r["c"] + i, aa)] = col
        if r["c"] + j >= N or vals[r["c"] + j][bb] is None:    # beet chuki tarikh par asli number ke upar '?' nahi likhna
            pend[(r["c"] + j, bb)] = (col, "%02d?" % cl if cl == pal(cl) else "%02d/%02d?" % (cl, pal(cl)))
    for k in r["pend2"]:
        col = COLS[r["common"].index(k) % len(COLS)]
        i, aa, j, bb = k
        pend[(r["c"] + i, aa)] = (col, "?")
        pend[(r["c"] + j, bb)] = (col, "?")
    indc = set()
    if r["ind"]:
        for cell in r["ind"][1]:
            if cell:
                indc.add(cell)

    def rowfor(idx, w):
        known = idx < N
        dd = D[idx] if known else fut[idx - N]
        c, kind, txt = [None] * 4, [None] * 4, [None] * 4
        ind = [False] * 4
        half = part and idx == N - 1                              # aadhi line: jo aaye wo txt me, baaki khali
        for g in range(4):
            cell = (idx, g)
            if cell in colour[w]:
                c[g], kind[g] = colour[w][cell], "step"
            if w == 2 and cell in pend:
                c[g], kind[g], txt[g] = _lt(pend[cell][0]), "light", pend[cell][1]
            if cell in indc and known:
                ind[g] = True
                if c[g] is None:
                    c[g], kind[g] = RED, "step"
        if half:
            for g in range(4):
                if vals[idx][g] is not None:
                    txt[g] = "%02d" % vals[idx][g]
        return dd, (None if half else (vals[idx] if known else None)), c, kind, txt, ind

    blocks = []
    for w, nm in enumerate(("STEP 1", "STEP 2", "STEP 3 (adhura)")):
        rr = []
        for i in range(L):
            dd, v, c, kind, txt, ind = rowfor(starts[w] + i, w)
            rr.append(_row(dd.isoformat(), v, c, kind, txt))
        blocks.append({"label": f"{nm}: {D[starts[w]]:%d %b} se (boundary {L} box)", "rows": rr})
    # ek sheet: teeno mahine upar-neeche
    first_month = (D[r["a"]].year, D[r["a"]].month)
    srows = []
    stepof = {}
    for w in range(3):
        for i in range(L):
            stepof[starts[w] + i] = (w + 1, i)
    idxs = [i for i, d in enumerate(D) if (d.year, d.month) >= first_month]
    last_idx = max(idxs[-1], r["c"] + L - 1)
    for idx in range(idxs[0], last_idx + 1):
        w = stepof.get(idx)
        dd, v, c, kind, txt, ind = rowfor(idx, (w[0] - 1) if w else 2)
        edge = ""
        if w:
            edge = "startend" if L == 1 else ("start" if w[1] == 0 else ("end" if w[1] == L - 1 else ""))
        srows.append({"date": dd.isoformat(), "v": v, "c": c, "kind": kind, "txt": txt, "step": w[0] if w else 0, "edge": edge, "ind": ind})
    # baaki mahine ke baache hue future din (mahine ke aakhir tak)
    for dd in [d for d in fut[max(0, last_idx - (N - 1)):] if d <= _month_end(D[-1])]:         # baaki mahine ke din (agle mahine ke sirf utne jo boundary ko chahiye)
        srows.append({"date": dd.isoformat(), "v": None, "c": [None] * 4, "kind": [None] * 4, "txt": [None] * 4, "step": 0, "edge": "", "ind": [False] * 4})
    legend = [{"color": COLS[n % len(COLS)], "text": f"Link {n + 1}: boundary ke {k[0] + 1}-ve box ki {GAMES[k[1]]} -> {k[2] - k[0]} box baad {GAMES[k[3]]} (wahi number/palat)"} for n, k in enumerate(r["common"])]
    if r["ind"]:
        legend.append({"color": RED, "text": f"Indicator {r['ind'][0]:02d}/{pal(r['ind'][0]):02d} (har boundary me ek cell)"})
    note = ("Step 1 (upar), Step 2 (beech), Step 3 (niche, adhura) ek lambi sheet me. Moti border = boundary (%d box, pehle se aakhri cell, dono sire samet). "
            "Ek link = ek rang. Laal = indicator (ek cell). Halka rang '?' = aane wala cell.") % L
    title = f"Puzzle-Steps: {L} box, {len(r['common'])} link"
    if r["pend"] or r["pend2"]:
        legend.append({"color": "#9e9e9e", "text": "'?' = aane wale din ka box (abhi result nahi). Beet chuki tarikh par '?' nahi likhte: wahan asli number dikhta hai."})
    return {"id": p, "title": title, "note": note, "blocks": blocks, "stack": {"rows": srows, "legend": legend, "note": note}}
