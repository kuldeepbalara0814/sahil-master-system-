"""005 Dana-Farak (4 Din Box): patterns/005_dana_farak_box/README.md.

Do number jinme dana 10/01 ka farak (palat laga ke) 4 din ke box me aaye = pair. Pair banne ke baad ke game se box ke
aakhri DS tak pair ke number (part 1) khelte hain; series ke agle/pichle number 'spot' (part 2).
Sirf paas ka data dekhta hai. Box me ek se zyada pair ho to 'confusion' (software skip nahi karta, sirf note).
"""
import datetime as dt

from . import data

GAMES = ("FB", "GB", "GL", "DS")
NOTE = "Is box me ek se zyada pair ban gaye, game saaf nahi bana, confusion hai. Khelne se pehle apne anubhav se soch-vichar karo. Skip karna uchit ho sakta hai."


def pal(n):
    return (n % 10) * 10 + n // 10


def _both(n):
    return (n, pal(n))


def relation(x, y):
    """-> None | ('same',) | ('farak', [(u, v, s)]) | ('gap', [(u, v, s)]); u<v, v-u = s (1/10), gap me 2s."""
    if y in _both(x):
        return ("same",)
    far, gap = set(), set()
    for u in _both(x):
        for v in _both(y):
            a, b = min(u, v), max(u, v)
            if b - a in (1, 10):
                far.add((a, b, b - a))
            elif b - a in (2, 20):
                gap.add((a, b, (b - a) // 2))
    if far:
        return ("farak", sorted(far))
    if gap:
        return ("gap", sorted(gap))
    return None


def _ok(n):
    return 0 <= n <= 99


def play_numbers(rel, x):
    """(core, series). core = part 1 ke khelne wale number; series = part 2 ke spot (series ke aage/peeche)."""
    core, series = set(), set()
    if rel[0] == "same":
        a = min(x, pal(x))
        for n in (a, a + 1, pal(a) - 1):
            if _ok(n):
                core.update(_both(n))
        if _ok(a + 10) and a + 10 == pal(a) + 1:
            core.add(a + 10)
    elif rel[0] == "farak":
        for u, v, s in rel[1]:
            core.update(_both(u) + _both(v))
            for n in (u - s, v + s):
                if _ok(n):
                    series.update(_both(n))
    else:
        for u, v, s in rel[1]:
            if _ok(u + s):
                core.update(_both(u + s))
    series -= core
    return sorted(core), sorted(series)


def _cells(rows):
    return [(d, g, int(n)) for d, v, _ in rows for g, n in enumerate(v)]


def _remaining(c2, end):
    """c2 ke baad ke game box ke aakhri DS tak (chhuti ke din ke game nahi)."""
    n, d = 0, c2[0]
    while d <= end:
        if not data.is_last_day(d):
            n += (3 - c2[1]) if d == c2[0] else 4
        d += dt.timedelta(days=1)
    return n


def events(rows, d_from, d_to):
    """Har pair (ya beech-khali) ka event. c1 ki tarikh d_from..d_to me."""
    cells = _cells(rows)
    last = rows[-1][0]
    ev = []
    for i, c1 in enumerate(cells):
        if not (d_from <= c1[0] <= d_to):
            continue
        end = c1[0] + dt.timedelta(days=3)
        span = []
        for c in cells[i:]:
            if c[0] > end:
                break
            span.append(c)
        for j in range(1, len(span)):
            c2 = span[j]
            rel = relation(c1[2], c2[2])
            if rel is None:
                continue
            rem = _remaining(c2, end)
            if rem == 0:
                continue                                    # pair box ke aakhri DS par bana: khelne ko kuch nahi
            core, series = play_numbers(rel, c1[2])
            part, other = span[:j + 1], 0                   # confusion: pair banne tak koi aur dana-pair
            for a in range(len(part)):
                for b in range(a + 1, len(part)):
                    if (a, b) != (0, j):
                        r2 = relation(part[a][2], part[b][2])
                        other += bool(r2 and r2[0] in ("same", "farak"))
            after = span[j + 1:]
            hit = next((c for c in after if c[2] in core), None)
            shit = next((c for c in after if c[2] in series), None)
            status = "pass" if hit else "pass2" if shit else "fail" if last >= end else "chalu"
            ev.append({"kind": rel[0], "c1": c1, "c2": c2, "end": end, "core": core, "series": series, "amb": other > 0, "other": other,
                       "hit": hit, "shit": shit, "status": status, "rem": rem, "t": 1 - (1 - len(core) / 100) ** rem})
    return ev


def stats(ev, kinds=("same", "farak", "gap")):
    out = {}
    for name, f in (("saaf", lambda e: not e["amb"]), ("confusion", lambda e: e["amb"])):
        L = [e for e in ev if f(e) and e["kind"] in kinds and e["status"] != "chalu"]
        out[name] = {"n": len(L), "pass": sum(e["status"] == "pass" for e in L),
                     "pass_series": sum(e["status"] in ("pass", "pass2") for e in L), "random": round(sum(e["t"] for e in L), 1),
                     "random_series": round(sum(1 - (1 - (len(e["core"]) + len(e["series"])) / 100) ** e["rem"] for e in L), 1)}
    return out


def cell_txt(c):
    return f"{c[0]:%d %b} {GAMES[c[1]]} {c[2]:02d}"


def item(e, today):
    kind = {"same": "ek hi number do baar", "farak": "dana 10/01 ka farak", "gap": "beech ka number gayab"}[e["kind"]]
    lines = [f"Pair: {cell_txt(e['c1'])} + {cell_txt(e['c2'])} ({kind}).",
             "Khelo: " + " ".join(f"{n:02d}" for n in e["core"]) + f" ({e['end']:%d %b} ke DS tak, {e['rem']} game baaki)."]
    if e["series"]:
        lines.append("Part 2 spot (series): " + " ".join(f"{n:02d}" for n in e["series"]) + " (khelna aap ki marzi)")
    if e["amb"]:
        lines.append(NOTE)
    if e["hit"]:
        lines.append(f"PASS: {cell_txt(e['hit'])}")
    elif e["shit"]:
        lines.append(f"Series ka number aaya: {cell_txt(e['shit'])} (part 2 pass)")
    elif e["status"] == "fail":
        lines.append("FAIL: box poora, koi number nahi aaya")
    key = f"dana:{e['kind']}:{e['c1'][0].isoformat()}-{e['c1'][1]}:{e['c2'][0].isoformat()}-{e['c2'][1]}"
    st = {"pass": "pass", "pass2": "pass", "fail": "fail", "chalu": "aaj"}[e["status"]]
    hit = e["hit"] or e["shit"]
    end = (hit[0] if hit else e["end"]).isoformat()
    return {"id": key, "kind": "dana", "end": end, "name": f"Dana-{e['kind']}-{e['c1'][0]:%d%b}", "status": st, "strength": "info", "ambiguous": e["amb"], "loc": [],
            "title": f"{e['core'][0]:02d} dana-farak | {e['c1'][0]:%d %b} se" + (" | confusion" if e["amb"] else ""),
            "lines": lines,
            "target": {"date": today.isoformat(), "games": f"baaki game, {e['end']:%d %b} DS tak", "numbers": e["core"]} if st == "aaj" else None,
            "targets": [{"game": "ALL", "numbers": e["core"]}] if st == "aaj" else []}
