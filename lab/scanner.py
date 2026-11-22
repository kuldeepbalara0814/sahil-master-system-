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

from . import data

GAMES = ("FB", "GB", "GL", "DS")
PATTERNS = [
    {"id": "001", "key": "copy", "naam": "Jodi-Copy", "pushti": False, "about": "Ek game me do number jinme 1 ya 10 ka farak (palat samet). Din 1, din 2 (ya 3), din 4 par set ka number aaye to PASS."},
    {"id": "002", "key": "naksha", "naam": "Naksha", "pushti": False, "about": "Naye mahine ke jodon (same/palat) ka naksha purane 13 saal me kahin ban chuka hai? Jahan mila wahan aage kya hua wo aaj ka andaza hai."},
]
WORDS = ["Mor", "Sher", "Chita", "Hans", "Baaz", "Hathi", "Ghoda", "Tota", "Machhli", "Cheel", "Bagula", "Kachua", "Hiran", "Bhalu", "Lomdi", "Nilgai",
         "Titli", "Koyal", "Bulbul", "Garud", "Sarus", "Gainda", "Panda", "Sambhar", "Chakor", "Morni", "Bakri", "Uloo", "Kabutar", "Ghariyal",
         "Suraj", "Chanda", "Tara", "Badal", "Bijli", "Nadi", "Pahad", "Jharna", "Sagar", "Hawa"]
# random jagah par bhi best z kitna aata hai (120 random mahine, 13 saal): L -> (median, max). Isse 'mazboot/theek/kamzor' tay hota hai.
BASE = {10: (6.5, 9.4), 12: (6.0, 9.7), 15: (5.8, 10.8), 18: (5.5, 7.8)}
LENS = (10, 12, 15, 18)
PAL = ["FF9800", "AB47BC", "66BB6A", "EF5350", "26C6DA", "F06292", "8D6E63", "9CCC65"]


def pal(n):
    return (n % 10) * 10 + n // 10


def name_for(kind, key):
    """Har pattern ka apna naam, hamesha wahi (jaise Naksha-Mor-47)."""
    h = zlib.crc32(f"{kind}|{key}".encode())
    return f"{kind}-{WORDS[h % len(WORDS)]}-{(h >> 8) % 90 + 10}"


def _arrays(rows):
    D = [r[0] for r in rows]
    V = np.array([r[1] for r in rows])
    C = np.minimum(V, (V % 10) * 10 + V // 10)
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


def match_info(rows, so, sc, L):
    """Purana (so se) aur naya (sc se) L line ka naksha: milte jode, unke rang aur aaj ka andaza."""
    D, V, C = _arrays(rows)
    N = len(rows)
    comp, ncommon = _comps(_links(C[sc:sc + L]), _links(C[so:so + L]), 4 * L)
    flatc, flato = C[sc:sc + L].reshape(-1), C[so:so + L].reshape(-1)
    comps = []
    for k, g in enumerate(comp):
        comps.append({"color": PAL[k % len(PAL)], "cells": g, "new_class": int(flatc[g[0]]), "old_class": int(flato[g[0]])})
    targets = []
    if so + L < N and so + L < sc:
        for c in comps:
            for g in range(4):
                if C[so + L, g] == c["old_class"]:
                    targets.append({"game": GAMES[g], "g": g, "numbers": sorted({c["new_class"], pal(c["new_class"])}), "color": c["color"]})
    return {"D": D, "V": V, "C": C, "comps": comps, "targets": targets, "ncommon": ncommon, "N": N}


def scan_naksha(rows, asof):
    D, V, C = _arrays(rows)
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
        so = int(np.argmax(np.where(valid, z, -9)))
        zb = float(z[so])
        med, mx = BASE[L]
        strength = "mazboot" if zb >= mx else ("theek" if zb >= (med + mx) / 2 else "kamzor")
        info = match_info(rows, so, sc, L)
        key = f"{L}:{D[so].isoformat()}"
        today = data.play_date(rows)
        tg = info["targets"]
        lines = [f"Naya {D[sc]:%d %b} se {D[-1]:%d %b} ({L} line) ka naksha purane {D[so]:%d %b %Y} se {D[so + L - 1]:%d %b %Y} me mila. {len(info['comps'])} jode milte hain (step), z={zb:.1f}.",
                 f"Random jagah par bhi best z ~{med:.1f} aata hai (max {mx:.1f}). Isliye: {strength}."]
        if tg:
            lines.append(f"Aaj {today:%d %b} ka andaza: " + "; ".join(f"{t['game']} me {' / '.join(f'{x:02d}' for x in t['numbers'])}" for t in tg))
        else:
            lines.append(f"Aaj {today:%d %b} ke liye purane me koi andaza wali jagah nahi.")
        items.append({"id": f"naksha:{L}:{D[so].isoformat()}", "kind": "naksha", "name": name_for("Naksha", key),
                      "status": "aaj" if tg else "dekho", "strength": strength, "steps": len(info["comps"]), "z": round(zb, 1),
                      "title": f"{D[so]:%b %Y} jaisa ({L} line)", "lines": lines,
                      "target": {"date": today.isoformat(), "games": ", ".join(sorted({t['game'] for t in tg})), "numbers": sorted({x for t in tg for x in t["numbers"]})} if tg else None})
    return {"summary": "Naye mahine ke naksha ko 13 saal me khoja. 'mazboot' tabhi jab z random ke best se bhi upar ho; baaki random jaisa.", "items": items}


SCANNERS = {"copy": scan_copy, "naksha": scan_naksha}


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
