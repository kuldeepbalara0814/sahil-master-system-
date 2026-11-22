"""Pattern Scan: sikhaye hue har pattern ko roz apne aap chalata hai aur batata hai ki aaj kya ban raha hai.

001 Jodi-Copy  : copy pattern (patterns/001_copy_pattern). 002 Naksha: mapping pattern (patterns/002_mapping_pattern).
Har pattern ki alag scan_xxx(rows) hai. run(rows) sab chalata hai; ek me galti ho to baaki chalte hain aur galti 'errors' me dikhti hai.
Sirf paas ka data dekhta hai (aage ka kuch nahi). Ye khoj hai, pakka pattern nahi.
"""
import datetime as dt
import time
import traceback
import zlib
from typing import Any

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

from . import band, dana_farak, data

GAMES = ("FB", "GB", "GL", "DS")
PATTERNS = [
    {"id": "001", "key": "copy", "naam": "Jodi-Copy", "pushti": False, "about": "Ek game me do number jinme 1 ya 10 ka farak (palat samet). Din 1, din 2 (ya 3), din 4 par set ka number aaye to PASS."},
    {"id": "002", "key": "naksha", "naam": "Naksha", "pushti": False, "about": "Naye mahine ke jodon (same/palat) ka naksha purane 13 saal me kahin ban chuka hai? Jahan mila wahan aage kya hua wo aaj ka andaza hai."},
    {"id": "002b", "key": "naksha2", "naam": "Naksha-Rashi", "pushti": False, "about": "Naksha ka part 2: link same number nahi, same rashi (family). Naye mahine ki rashi ki movement purane 13 saal me kahin same duri/gap se bani? Jahan mili wahan aage kya hua wo aaj ka andaza."},
    {"id": "003", "key": "family", "naam": "Family", "pushti": False, "about": "Ek rashi (family) 3 baar: din d, d+1 (ya d+2), phir d+3. Do step ban gaye to 3rd step ke din poori family (8 jodi) khelte hain. Jitne bane ya shuru huye sab yahan dikhte hain."},
    {"id": "005", "key": "dana", "naam": "Dana-Farak", "pushti": False, "about": "4 din ke box me do number jinme dana 10/01 ka farak (palat samet). Pair banne ke baad box ke aakhri DS tak pair ke number khelte hain; series ke agle/pichle number spot. Ek se zyada pair ho to confusion note."},
]
WORDS = ["Mor", "Sher", "Chita", "Hans", "Baaz", "Hathi", "Ghoda", "Tota", "Machhli", "Cheel", "Bagula", "Kachua", "Hiran", "Bhalu", "Lomdi", "Nilgai",
         "Titli", "Koyal", "Bulbul", "Garud", "Sarus", "Gainda", "Panda", "Sambhar", "Chakor", "Morni", "Bakri", "Uloo", "Kabutar", "Ghariyal",
         "Suraj", "Chanda", "Tara", "Badal", "Bijli", "Nadi", "Pahad", "Jharna", "Sagar", "Hawa"]
# random jagah par bhi best z kitna aata hai (120 random mahine, 13 saal): L -> (median, max). Isse 'mazboot/theek/kamzor' tay hota hai.
BASE = {10: (6.5, 9.4), 12: (6.0, 9.7), 15: (5.8, 10.8), 18: (5.5, 7.8)}
BASE_R = {10: (5.0, 8.9), 12: (5.0, 7.3), 15: (4.9, 6.2), 18: (4.5, 6.5)}   # rashi wala: 60 random jagah (13 saal)
LENS = (10, 12, 15, 18)
TOP = 12                                                 # har lambai ke itne milan dikhao
PAL = ["FF9800", "AB47BC", "66BB6A", "EF5350", "26C6DA", "F06292", "8D6E63", "9CCC65"]


def pal(n):
    return (n % 10) * 10 + n // 10


def name_for(kind, key):
    """Har pattern ka apna naam, hamesha wahi (jaise Naksha-Mor-47)."""
    h = zlib.crc32(f"{kind}|{key}".encode())
    return f"{kind}-{WORDS[h % len(WORDS)]}-{(h >> 8) % 90 + 10}"


RKEYS = sorted(band.RASHIS)
RID = np.zeros(100, dtype=int)                               # number -> rashi (0..14)
for _i, _k in enumerate(RKEYS):
    for _n in band.RASHIS[_k]:
        RID[_n] = _i
RPAL = ["FF9800", "AB47BC", "66BB6A", "EF5350", "26C6DA", "F06292", "8D6E63", "9CCC65", "FFB74D", "CE93D8", "80DEEA", "A5D6A7", "EF9A9A", "FFF176", "90CAF9"]


def _arrays(rows, mode="n"):
    """mode n: number ya uska palat ek class. mode r: poori rashi (15 me se ek) ek class."""
    D = [r[0] for r in rows]
    V = np.array([r[1] for r in rows])
    C = RID[V] if mode == "r" else np.minimum(V, (V % 10) * 10 + V // 10)
    return D, V, C


# ---------------------------------------------------------------- 001 copy
def _nb(v):
    return {x for x in (v - 1, v + 1, v - 10, v + 10) if 0 <= x <= 99}


def is_copy(x, y):
    return y not in (x, pal(x)) and (y in _nb(x) or y in _nb(pal(x)))


def copy_events(rows, a, b, today=None):
    """a..b ke beech copy pattern ki jodi. Din 4 'today' ho sakta hai (abhi aaya nahi)."""
    D = [r[0] for r in rows]
    R = [r[1] for r in rows]
    n = len(rows)
    ev = []
    for d in range(n):
        if not (a <= D[d] <= b):
            continue
        for shape, off in (("seedha", 1), ("ulta", 2)):
            j, t = d + off, d + 3
            if j >= n or t > n:
                continue
            known = t < n
            if not all(data.adjacent(D[k], D[k + 1]) for k in range(d, min(t, n - 1))):
                continue
            if not known and (today is None or not data.adjacent(D[n - 1], today)):
                continue
            for g in range(4):
                x, y = R[d][g], R[j][g]
                if is_copy(x, y):
                    S = sorted({x, y, pal(x), pal(y)})
                    hit = [(k, R[t][k]) for k in range(4) if known and R[t][k] in S]
                    ev.append({"shape": shape, "d": D[d], "j": D[j], "t": D[t] if known else today, "g": g, "x": x, "y": y, "S": S,
                               "hit": hit, "status": ("pass" if hit else "fail") if known else "aaj"})
    return ev


def scan_copy(rows, asof):
    today = data.play_date(rows)
    last = rows[-1][0]
    ev = copy_events(rows, last - dt.timedelta(days=8), last, today)
    stat = copy_events(rows, last - dt.timedelta(days=92), last)
    done = [e for e in stat if e["status"] != "aaj"]
    ps = sum(1 for e in done if e["status"] == "pass")
    items = []
    for e in sorted(ev, key=lambda e: (e["status"] != "aaj", e["t"]), reverse=False):
        if e["status"] != "aaj" and (today - e["t"]).days > 3:
            continue
        key = f"{e['shape']}:{e['g']}:{e['d'].isoformat()}"
        sets = " ".join(f"{s:02d}" for s in e["S"])
        items.append({"id": f"copy:{key}", "kind": "copy", "name": name_for("Copy", key), "status": e["status"],
                      "strength": "info",
                      "title": f"{e['shape']} | {GAMES[e['g']]} me {e['x']:02d} aur {e['y']:02d} ({e['d']:%d %b} se)",
                      "lines": [f"Set (4 jodi): {sets} (dono number + palat)",
                                (f"Aaj {today:%d %b} (din 4): is set ka koi number kisi bhi game me aaye to PASS." if e["status"] == "aaj" else
                                 f"Din 4 ({e['t']:%d %b}): " + (", ".join(f"{GAMES[k]} {v:02d}" for k, v in e["hit"]) if e["hit"] else "set ka number nahi aaya") + (" - PASS" if e["hit"] else " - FAIL"))],
                      "target": {"date": today.isoformat(), "games": "FB GB GL DS (chaaron)", "numbers": e["S"]} if e["status"] == "aaj" else None})
    return {"summary": f"Pichle 3 mahine: {len(done)} jodi poori huin, {ps} PASS (random me bhi ~15% pass hota hai).", "items": items}


# ---------------------------------------------------------------- 002 naksha
def _links(c):
    f = c.reshape(-1)
    n = len(f)
    return [(a, b) for a in range(n) for b in range(a + 1, n) if f[a] == f[b]]


def _scores(C, Lk, L):
    W = sliding_window_view(C, (L, 4))[:, 0].reshape(-1, 4 * L)
    m = np.zeros(len(W), dtype=int)
    for a, b in Lk:
        m += W[:, a] == W[:, b]
    return m


def _comps(cur_links, old_links, n):
    common = set(cur_links) & set(old_links)
    par = list(range(n))

    def f(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    for a, b in common:
        par[f(a)] = f(b)
    g: dict = {}
    for a, b in common:
        g.setdefault(f(a), set()).update((a, b))
    return sorted((sorted(v) for v in g.values()), key=lambda v: v[0]), len(common)


def match_info(rows, so, sc, L, mode="n"):
    """Purana (so se) aur naya (sc se) L line ka naksha: milte jode, unke rang aur aaj ka andaza."""
    D, V, C = _arrays(rows, mode)
    colors = RPAL if mode == "r" else PAL
    N = len(rows)
    comp, ncommon = _comps(_links(C[sc:sc + L]), _links(C[so:so + L]), 4 * L)
    flatc, flato = C[sc:sc + L].reshape(-1), C[so:so + L].reshape(-1)
    comps = []
    for k, g in enumerate(comp):
        comps.append({"color": colors[k % len(colors)], "cells": g, "new_class": int(flatc[g[0]]), "old_class": int(flato[g[0]])})
    targets = []
    if so + L < N and so + L < sc:
        for c in comps:
            for g in range(4):
                if C[so + L, g] == c["old_class"]:
                    nums = sorted(band.RASHIS[RKEYS[c["new_class"]]]) if mode == "r" else sorted({c["new_class"], pal(c["new_class"])})
                    targets.append({"game": GAMES[g], "g": g, "numbers": nums, "color": c["color"]})
    return {"D": D, "V": V, "C": C, "comps": comps, "targets": targets, "ncommon": ncommon, "N": N}


def scan_naksha(rows, asof, mode="n"):
    D, V, C = _arrays(rows, mode)
    N = len(rows)
    items = []
    for L in LENS:
        sc = N - L
        Lk = _links(C[sc:sc + L])
        if len(Lk) < 4:
            continue
        m = _scores(C, Lk, L)
        valid = np.zeros(len(m), bool)
        valid[:max(0, sc - L - 1)] = True
        z = (m - m[valid].mean()) / (m[valid].std() + 1e-9)
        zz = np.where(valid, z, -9)
        picks = []
        for i in np.argsort(-zz):                        # sabse achhe milan, ek dusre se kam se kam 20 din door
            if zz[i] < 0 or len(picks) >= TOP:
                break
            if all(abs(int(i) - j) >= 20 for j in picks):
                picks.append(int(i))
        for rank, so in enumerate(picks, 1):
            items.append(_naksha_item(rows, D, C, so, sc, L, float(z[so]), rank, int(m[so]), mode))
    return {"summary": "Naye mahine ke naksha ko 13 saal me khoja; har lambai (10/12/15/18 line) ke sabse achhe %d milan dikhaye (ek dusre se 20 din door). Sirf wahi link ginta hoon jahan same ya palat number same jagah par ho; rashi ya sirf rang wale link abhi nahi ginta, isliye aap ki aankh se kam milte hain. 'mazboot' tabhi jab z random ke best se bhi upar ho, baaki random jaisa." % TOP, "items": items}


def _naksha_item(rows, D, C, so, sc, L, zb, rank, nlinks, mode="n"):
    if True:
        med, mx = (BASE_R if mode == "r" else BASE)[L]
        strength = "mazboot" if zb >= mx else ("theek" if zb >= (med + mx) / 2 else "kamzor")
        info = match_info(rows, so, sc, L, mode)
        key = f"{L}:{D[so].isoformat()}"
        pid, nm = ("naksha2", "Naksha-Rashi") if mode == "r" else ("naksha", "Naksha")
        today = data.play_date(rows)
        tg = info["targets"]
        lines = [f"Naya {D[sc]:%d %b} se {D[-1]:%d %b} ({L} line) ka naksha purane {D[so]:%d %b %Y} se {D[so + L - 1]:%d %b %Y} me mila. {len(info['comps'])} jode milte hain (step), z={zb:.1f}.",
                 f"Random jagah par bhi best z ~{med:.1f} aata hai (max {mx:.1f}). Isliye: {strength}."]
        if tg:
            lines.append(f"Aaj {today:%d %b} ka andaza: " + "; ".join(f"{t['game']} me {' / '.join(f'{x:02d}' for x in t['numbers'])}" for t in tg))
        else:
            lines.append(f"Aaj {today:%d %b} ke liye purane me koi andaza wali jagah nahi.")
        return ({"id": f"{pid}:{L}:{D[so].isoformat()}", "kind": pid, "name": name_for(nm, key),
                      "status": "aaj" if tg else "dekho", "strength": strength, "steps": len(info["comps"]), "z": round(zb, 1), "rank": rank,
                      "title": f"#{rank} {D[so]:%b %Y} jaisa ({L} line)", "lines": lines,
                      "target": {"date": today.isoformat(), "games": ", ".join(sorted({t['game'] for t in tg})), "numbers": sorted({x for t in tg for x in t["numbers"]})} if tg else None})


# ---------------------------------------------------------------- 003 family
def family_events(rows, d_from, d_to, today=None):
    """Rashi family ke design: step 1 din d (d_from..d_to), seedha (d, d+1, d+3) ya ulta (d, d+2, d+3). Din d+3 'today' ho sakta hai."""
    D = [r[0] for r in rows]
    R = [r[1] for r in rows]
    n = len(rows)
    ev = []
    for d in range(n):
        if not (d_from <= D[d] <= d_to):
            continue
        for shape, off in (("seedha", 1), ("ulta", 2)):
            j, t = d + off, d + 3
            if j >= n or t > n:
                continue
            known = t < n
            if not all(data.adjacent(D[k], D[k + 1]) for k in range(d, min(t, n - 1))):
                continue
            if not known and (today is None or not data.adjacent(D[n - 1], today)):
                continue
            for k, nums in band.RASHIS.items():
                st = set(nums)
                c1 = [g for g, v in enumerate(R[d]) if v in st]
                c2 = [g for g, v in enumerate(R[j]) if v in st]
                if not c1 or not c2:
                    continue
                hit = [(g, R[t][g]) for g in range(4) if known and R[t][g] in st]
                amb = len(c1) > 1 or len(c2) > 1
                loc = [] if amb else sorted(set(c1 + c2))
                ev.append({"rashi": nums[0], "numbers": sorted(nums), "shape": shape, "d": D[d], "j": D[j], "t": D[t] if known else today,
                           "c1": c1, "c2": c2, "amb": amb, "loc": loc, "hit": hit,
                           "status": ("pass" if hit else "fail") if known else "aaj"})
    return ev


def scan_family(rows, asof):
    today = data.play_date(rows)
    last = rows[-1][0]
    ev = family_events(rows, last - dt.timedelta(days=10), last, today)
    stat = [e for e in family_events(rows, last - dt.timedelta(days=95), last) if e["status"] != "aaj"]
    s8 = [e for e in stat if len(e["numbers"]) == 8]
    s4 = [e for e in stat if len(e["numbers"]) == 4]
    pas = lambda L: sum(1 for e in L if e["status"] == "pass")
    items = []
    for e in sorted(ev, key=lambda e: (e["status"] != "aaj", e["t"], e["rashi"]), reverse=False):
        if e["status"] != "aaj" and (today - e["t"]).days > 3:
            continue
        key = f"{e['rashi']}:{e['shape']}:{e['d'].isoformat()}"
        cells = lambda day, cols: ", ".join(f"{GAMES[g]} {[v for gg, v in enumerate([r for dd, r, _ in rows if dd == day][0]) if gg == g][0]:02d}" for g in cols)
        fam = " ".join(f"{x:02d}" for x in e["numbers"])
        loc_txt = ("ek se zyada jagah ban raha hai, location aap tay karo" if e["amb"] else
                   "location (zyada paise): " + ", ".join(GAMES[g] for g in e["loc"]) + " | baaki halka")
        lines = [f"Step 1 ({e['d']:%d %b}): {cells(e['d'], e['c1'])}. Step 2 ({e['j']:%d %b}): {cells(e['j'], e['c2'])}.",
                 f"Family {e['rashi']:02d} rashi: {fam}", loc_txt]
        if e["status"] == "aaj":
            lines.append(f"Aaj {today:%d %b} (3rd step): family ka koi bhi number kisi bhi game me aaye to PASS. Paper: har number 10 Rs, location par 20 Rs.")
        else:
            if e["hit"]:
                inloc = bool(e["loc"]) and any(g in e["loc"] for g, _ in e["hit"])
                kind = "with location" if inloc else ("out of location" if e["loc"] else "location tay nahi")
                lines.append(f"3rd step ({e['t']:%d %b}): " + ", ".join(f"{GAMES[g]} {v:02d}" for g, v in e["hit"]) + f" - PASS ({kind})")
            else:
                lines.append(f"3rd step ({e['t']:%d %b}): family ka koi number nahi aaya - FAIL")
        items.append({"id": f"family:{key}", "kind": "family", "name": name_for("Family", key), "status": e["status"], "strength": "info",
                      "ambiguous": e["amb"], "loc": [GAMES[g] for g in e["loc"]],
                      "title": f"{e['rashi']:02d} rashi | {e['shape']} | {e['d']:%d %b} se" + (" | jodi rashi" if len(e["numbers"]) == 4 else ""),
                      "lines": lines,
                      "target": {"date": today.isoformat(), "games": ("chaaron (aap tay karo)" if e["amb"] else ", ".join(GAMES[g] for g in e["loc"]) + " zyada"), "numbers": e["numbers"]} if e["status"] == "aaj" else None})
    summary = (f"Pichle 3 mahine: 8-number rashi {pas(s8)}/{len(s8)} pass ({100 * pas(s8) / max(1, len(s8)):.0f}%, random ~28%), "
               f"jodi rashi {pas(s4)}/{len(s4)} ({100 * pas(s4) / max(1, len(s4)):.0f}%, random ~15%). Aaj {sum(1 for i in items if i['status'] == 'aaj')} design 3rd step ki taraf, "
               f"{sum(1 for i in items if i['status'] != 'aaj')} pichle 3 din me poore huye.")
    return {"summary": summary, "items": items}


def scan_dana(rows, asof):
    today = data.play_date(rows)
    last = rows[-1][0]
    ev = dana_farak.events(rows, last - dt.timedelta(days=180), last)
    st = dana_farak.stats(ev, ("same", "farak"))
    s, c = st["saaf"], st["confusion"]
    live = [e for e in ev if e["status"] == "chalu"]
    live.sort(key=lambda e: (e["amb"], e["c2"][0], e["c2"][1]), reverse=False)
    recent = [e for e in ev if e["status"] != "chalu" and (last - e["end"]).days <= 2]
    items = [dana_farak.item(e, today) for e in (live + recent)[:40]]
    summary = (f"Pichle 6 mahine (same + farak pair): saaf box {s['pass']}/{s['n']} pass (random ~{s['random']:.0f}), "
               f"confusion box {c['pass']}/{c['n']} (random ~{c['random']:.0f}). Abhi {len(live)} box chalu.")
    return {"summary": summary, "items": items}


def scan_naksha2(rows, asof):
    out = scan_naksha(rows, asof, "r")
    out["summary"] = ("Naksha ka part 2: link number ka nahi, **rashi** ka. Purane 13 saal me wahi design (same duri, same jagah) jahan naye mahine ki rashi ki movement milti hai; "
                      "har lambai ke sabse achhe %d milan. Rashi ke 15 hi group hain, isliye random me bhi zyada milan aate hain; 'mazboot' tabhi jab z random ke best se upar ho." % TOP)
    return out


SCANNERS = {"copy": scan_copy, "naksha": scan_naksha, "naksha2": scan_naksha2, "family": scan_family, "dana": scan_dana}
COPY_COLORS = ["FFB74D", "CE93D8", "80DEEA", "A5D6A7", "EF9A9A", "FFF176", "90CAF9", "BCAAA4", "F48FB1", "C5E1A5", "FFCC80", "B39DDB"]   # kaale ank saaf dikhen


def ids_for_month(rows, key, year, month, cap=24):
    """Is mahine ke saare pattern ke id (step 1 is mahine me). -> (ids, kul sankhya)"""
    a = dt.date(year, month, 1)
    b = min(rows[-1][0], (a.replace(day=28) + dt.timedelta(days=4)).replace(day=1) - dt.timedelta(days=1))
    today = data.play_date(rows)
    if key == "family":
        ev = family_events(rows, a, b, today)
        ids = sorted({(e["d"], f"family:{e['rashi']}:{e['shape']}:{e['d'].isoformat()}") for e in ev})
    elif key == "copy":
        ev = copy_events(rows, a, b, today)
        ids = sorted({(e["d"], f"copy:{e['shape']}:{e['g']}:{e['d'].isoformat()}") for e in ev})
    else:
        raise ValueError("Is pattern ki mahine wali copy nahi banti")
    out = [i for _, i in ids]
    return out[:cap], len(out)


def run(rows, only=None) -> dict[str, Any]:
    """Sab pattern chalao. Ek me galti ho to baaki chalte hain. -> report"""
    t0 = time.time()
    asof = rows[-1][0].isoformat()
    rep: dict[str, Any] = {"asof": asof, "play_date": data.play_date(rows).isoformat(), "time": dt.datetime.now().isoformat(timespec="seconds"),
                           "patterns": [], "errors": []}
    for p in PATTERNS:
        if only and p["key"] != only:
            continue
        entry = {**p, "items": [], "summary": ""}
        try:
            out = SCANNERS[p["key"]](rows, asof)
            entry.update(out)
        except Exception as e:                               # ek pattern ki galti baaki ko na roke
            tb = traceback.format_exc().strip().splitlines()
            rep["errors"].append({"pattern": p["naam"], "error": f"{type(e).__name__}: {e}", "trace": " | ".join(tb[-3:])})
        rep["patterns"].append(entry)
    rep["seconds"] = round(time.time() - t0, 1)
    return rep
