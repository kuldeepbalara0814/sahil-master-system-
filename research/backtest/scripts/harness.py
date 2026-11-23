"""Walk-forward harness: har din t par pattern ka ASLI scan code sirf rows[:t] par chalta hai (aage ka row kabhi nahi),
phir andaze ko din t (ya pattern ki window ke aage ke din) ke asli result se milata hai.
Usage: python harness.py run --tag real [--shuffle row|col --seed 1] [--blocks 200] [--procs 3] [--light-step 1]
Output: ../cache/<tag>_{light,heavy,ens}.csv.gz  (analysis.py inhe padhta hai)
"""
import argparse, csv, gzip, os, sys, time, random, datetime as dt
from multiprocessing import Pool
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ROOT)
from lab import data, scanner, steps, dana_farak, baar  # noqa: E402

CACHE = os.path.join(HERE, "..", "cache")
OUT = os.path.join(HERE, "..", "out")
COLS = ["grp", "pat", "t", "date", "id", "sub", "s", "cells", "cellhits", "hit", "p", "L", "rank", "z", "strength", "kind", "shape", "g", "amb",
        "nlink", "ind", "ltype", "wlen", "loc_n", "loc_hit", "loc_p", "loc_win", "alt_cells", "alt_cellhits", "nums"]
T0 = 500            # itni purani history ke baad hi andaza (naksha ko history chahiye)
GAMES = ("FB", "GB", "GL", "DS")
TOK_DAYS = (365, 730, 1095, 1825, 0)
TOK_K = (1, 2, 3, 4, 6, 8, 12)


def pal(n):
    return (n % 10) * 10 + n // 10


def pr(s, cells):
    return 1 - (1 - s / 100.0) ** cells


# ------------------------------------------------------------------ data (real / shuffled)
def make_data(shuffle=None, seed=0):
    rows = data.load()
    if not shuffle:
        return rows
    rng = np.random.default_rng(seed)
    V = np.array([r[1] for r in rows])
    if shuffle == "row":
        V = V[rng.permutation(len(V))]
    elif shuffle == "col":
        V = np.stack([V[rng.permutation(len(V)), g] for g in range(4)], axis=1)
    else:
        raise ValueError(shuffle)
    return [(r[0], [int(x) for x in V[i]], "shuf") for i, r in enumerate(rows)]


G = {}   # worker global: full rows, tokri cum


def init(shuffle, seed):
    full = make_data(shuffle, seed)
    G["full"] = full
    G["dates"] = [r[0] for r in full]
    V = np.array([r[1] for r in full])
    G["V"] = V
    N = len(full)
    wd = np.array([d.weekday() for d in G["dates"]])
    G["wd"] = wd
    cum = np.zeros((7, N + 1, 100), dtype=np.int16)
    for w in range(7):
        c = np.zeros((N, 100), dtype=np.int16)
        for i in range(N):
            if wd[i] == w:
                for v in V[i]:
                    c[i, v] += 1
        cum[w, 1:] = np.cumsum(c, axis=0)
    G["cum"] = cum


def valid_ts(full):
    """t jiske liye rows[:t] ka play_date == full[t] ki tarikh (data me gap nahi), aur aage 40 row bache (window ke liye)."""
    N = len(full)
    return [t for t in range(T0, N - 40) if data.play_date(full[:t]) == full[t][0]]


# ------------------------------------------------------------------ record helpers
def rec(**kw):
    r = {c: "" for c in COLS}
    r.update(kw)
    return r


def finish(r, res_rows, S, extra_window_rows=None):
    """res_rows: list of 4-lists (window ke din). S: set of numbers. -> cellhits, p."""
    cells = 4 * len(res_rows) if extra_window_rows is None else extra_window_rows
    ch = sum(1 for row in res_rows for v in row if v in S)
    r.update(s=len(S), cells=cells, cellhits=ch, hit=int(ch > 0), p=round(pr(len(S), cells), 6), nums=" ".join(f"{x:02d}" for x in sorted(S)))
    return r


def single_day(it, res, t, date, pat, grp, **kw):
    """ek item jiske targets 'aaj' (agle din) ke liye hain."""
    tg = it.get("targets") or []
    if not tg:
        return None
    S = set()
    bygame = {}
    for x in tg:
        S |= set(int(n) for n in x["numbers"])
        if x["game"] in GAMES:
            bygame.setdefault(GAMES.index(x["game"]), set()).update(int(n) for n in x["numbers"])
    r = rec(grp=grp, pat=pat, t=t, date=date, id=it["id"], **kw)
    finish(r, [res], S)
    if bygame:
        r["loc_n"] = sum(len(v) for v in bygame.values())
        r["loc_win"] = sum(1 for g, v in bygame.items() if res[g] in v)
        r["loc_hit"] = int(r["loc_win"] > 0)
        q = 1.0
        for g, v in bygame.items():
            q *= 1 - len(v) / 100.0
        r["loc_p"] = round(1 - q, 6)
    return r


# ------------------------------------------------------------------ tokri (fast, real baar.tokri se milaya jata hai: check_nolookahead.py)
def tokri_fast(t, days, k):
    full, dates, cum, wd = G["full"], G["dates"], G["cum"], G["wd"]
    asof = dates[t]
    w = asof.weekday()
    if days:
        lo = asof - dt.timedelta(days=days)
        i0 = next(i for i, d in enumerate(dates) if d >= lo) if lo > dates[0] else 0
    else:
        i0 = 0
    cnt = cum[w, t].astype(int) - cum[w, i0].astype(int)
    order = sorted(range(100), key=lambda n: (-cnt[n], n))
    top = order[:k]
    return sorted({n for n in top} | {pal(n) for n in top}), top, cnt


# ------------------------------------------------------------------ dana events (naye, c2 usi row me)
def dana_new(rows, last):
    tail = rows[-8:]
    ev = dana_farak.events(tail, last - dt.timedelta(days=3), last)
    return [e for e in ev if e["c2"][0] == last]


def dana_records(full, t, rows, res, date, grp):
    out = []
    last = rows[-1][0]
    for e in dana_new(rows, last):
        c2g = e["c2"][1]
        end = e["end"]
        fut = []
        for i in range(t, len(full)):
            if full[i][0] > end:
                break
            fut.append(full[i][1])
        same_day_rest = list(rows[-1][1][c2g + 1:])
        cells_sd = len(same_day_rest) + 4 * len(fut)
        cells_st = 4 * len(fut)
        okrem = int(cells_sd == e["rem"])
        eid = f"dana:{e['kind']}:{e['c1'][0].isoformat()}-{e['c1'][1]}:{e['c2'][0].isoformat()}-{e['c2'][1]}"
        for sub, S in (("core", set(e["core"])), ("core+series", set(e["core"]) | set(e["series"]))):
            if not S:
                continue
            allc = same_day_rest + [v for row in fut for v in row]
            strict = [v for row in fut for v in row]
            ch = sum(1 for v in allc if v in S)
            ch2 = sum(1 for v in strict if v in S)
            r = rec(grp=grp, pat="dana", t=t, date=date, id=eid, sub=sub, s=len(S), cells=cells_sd, cellhits=ch, hit=int(ch > 0),
                    p=round(pr(len(S), cells_sd), 6), kind=e["kind"], amb=int(e["amb"]), alt_cells=cells_st, alt_cellhits=ch2,
                    wlen=okrem, nums=" ".join(f"{x:02d}" for x in sorted(S)))
            out.append(r)
    return out


def dana_live(rows):
    """Number-Rank/Hit-map ke liye aaj ke live dana map (scan_dana jaisa): [(id, core)]"""
    last = rows[-1][0]
    ev = dana_farak.events(rows[-8:], last - dt.timedelta(days=3), last)
    live = [e for e in ev if e["status"] == "chalu"]
    live.sort(key=lambda e: (e["amb"], e["c2"][0], e["c2"][1]))
    seen, out = set(), []
    for e in live:
        k = (tuple(e["core"]), e["end"], e["amb"])
        if k in seen:
            continue
        seen.add(k)
        out.append((f"dana:{e['kind']}:{e['c1'][0].isoformat()}-{e['c1'][1]}:{e['c2'][0].isoformat()}-{e['c2'][1]}", set(e["core"]), e))
    return out[:40]


# ------------------------------------------------------------------ light din: copy, family, dana, tokri
def light_day(t):
    full = G["full"]
    rows = full[:t]
    target = full[t]
    assert len(rows) == t and rows[-1][0] < target[0] and data.play_date(rows) == target[0]
    res = target[1]
    date = target[0].isoformat()
    out = []
    for key, fn in (("copy", scanner.scan_copy), ("family", scanner.scan_family)):
        for it in fn(rows, rows[-1][0].isoformat())["items"]:
            if it["status"] != "aaj":
                continue
            p = it["id"].split(":")
            if key == "copy":
                kw = dict(sub=p[1], shape=p[1], g=int(p[2]))
            else:
                kw = dict(sub=p[2] + ("_8" if len(it["target"]["numbers"]) == 8 else "_4"), shape=p[2], kind=len(it["target"]["numbers"]),
                          amb=int(bool(it.get("ambiguous"))), g=len(it.get("loc") or []))
            r = single_day(it, res, t, date, key, "light", **kw)
            if r:
                out.append(r)
    out += dana_records(full, t, rows, res, date, "light")
    # dana live map (persistence): har live map ka aaj ka hit
    for mid, core, e in dana_live(rows):
        r = rec(grp="light", pat="danaD", t=t, date=date, id=mid, kind=e["kind"], amb=int(e["amb"]))
        out.append(finish(r, [res], core))
    # tokri
    for days in TOK_DAYS:
        for k in TOK_K:
            S, top, _ = tokri_fast(t, days, k)
            r = rec(grp="light", pat="tokri", t=t, date=date, id=f"tokri:{days}:{k}", sub=f"d{days}_k{k}", L=days, rank=k)
            out.append(finish(r, [res], set(S)))
    return out


# ------------------------------------------------------------------ heavy din: naksha, naksha2, steps (+ ensemble)
def heavy_day(t):
    full = G["full"]
    rows = full[:t]
    target = full[t]
    assert len(rows) == t and rows[-1][0] < target[0] and data.play_date(rows) == target[0]
    res = target[1]
    date = target[0].isoformat()
    asof = rows[-1][0].isoformat()
    out, maps = [], {"naksha": [], "naksha2": [], "family": [], "copy": [], "dana": [], "steps": []}
    for key in ("naksha", "naksha2"):
        for it in scanner.SCANNERS[key](rows, asof)["items"]:
            L = int(it["id"].split(":")[1])
            r = single_day(it, res, t, date, key, "heavy", sub=f"L{L}", L=L, rank=it["rank"], z=it["z"], strength=it["strength"], nlink=it["steps"])
            if r:
                out.append(r)
                maps[key].append(set(int(x) for x in r["nums"].split()))
    for it in scanner.scan_copy(rows, asof)["items"]:
        if it["status"] == "aaj" and it["targets"]:
            maps["copy"].append(set(it["targets"][0]["numbers"]))
    for it in scanner.scan_family(rows, asof)["items"]:
        if it["status"] == "aaj" and it["targets"]:
            maps["family"].append({n for x in it["targets"] for n in x["numbers"]})
    for mid, core, e in dana_live(rows):
        maps["dana"].append(core)
    # steps
    today = data.play_date(rows)
    N = len(rows)
    res_list = steps.find(rows, top=24)
    for rk, r in enumerate(res_list, 1):
        L, c = r["L"], r["c"]
        end_idx = c + L - 1
        pid = steps.pid(r, [x[0] for x in rows])
        if rk <= 8:
            it = steps.item(r, rows, today)
            tgt = {n for x in it["targets"] for n in x["numbers"]}
            if tgt:
                maps["steps"].append(tgt)
                out.append(finish(rec(grp="heavy", pat="stepsD", t=t, date=date, id=pid, sub=f"L{L}", L=L, rank=rk, nlink=len(r["common"]), ind=int(r["ind"] is not None)), [res], tgt))
        if end_idx >= len(full):
            continue
        win = [full[i][1] for i in range(t, end_idx + 1)]
        for k, first in r["pend"]:
            i, aa, j, bb = k
            S = {first, pal(first)}
            lt = "flat" if i == j else ("standing" if aa == bb else "diag")
            rr = rec(grp="heavy", pat="steps", t=t, date=date, id=pid + ":" + "-".join(map(str, k)), sub=f"L{L}", L=L, rank=rk, nlink=len(r["common"]),
                     ind=int(r["ind"] is not None), ltype=lt, wlen=len(win), kind=len(r["pend"]))
            out.append(finish(rr, win, S))
    # ensemble: har number par kitne alag map ne vote diya
    tok = set(baar.tokri(rows, today.weekday(), asof=today)["numbers"])
    V = {n: {k: 0 for k in maps} for n in range(100)}
    for k, lst in maps.items():
        for S in lst:
            for n in S:
                V[n][k] += 1
    ens = []
    resset = set(res)
    for n in range(100):
        v = V[n]
        if sum(v.values()) or n in tok:
            ens.append([t, date, n, v["naksha"], v["naksha2"], v["family"], v["copy"], v["dana"], v["steps"], int(n in tok), int(n in resset), sum(1 for x in res if x == n)])
    ens.append([t, date, -1, 0, 0, 0, 0, 0, 0, 0, len(resset), 0])
    return out, ens


# ------------------------------------------------------------------ driver
def write(path, cols, rows):
    with gzip.open(path, "wt", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in rows:
            w.writerow([r[c] for c in cols] if isinstance(r, dict) else r)


def run(args):
    tag = args.tag
    init(args.shuffle, args.seed)
    full = G["full"]
    ts = valid_ts(full)
    rng = random.Random(1234)           # sab run me wahi din (real aur shuffle ek jaise)
    starts = sorted(rng.sample(range(len(ts) - 4), args.blocks))
    heavy_ts = sorted({ts[s + j] for s in starts for j in range(4) if ts[s + j - 0] - ts[s] == j})
    light_ts = ts[::args.light_step]
    prog = os.path.join(OUT, f"progress_{tag}.txt")
    t0 = time.time()
    res = {}
    with Pool(args.procs, initializer=init, initargs=(args.shuffle, args.seed)) as pool:
        for name, fn, tl in (("light", light_day, light_ts), ("heavy", heavy_day, heavy_ts)):
            if name == "heavy" and args.no_heavy:
                continue
            allr, alle = [], []
            done = 0
            for out in pool.imap(fn, tl, chunksize=4):
                if name == "heavy":
                    allr += out[0]
                    alle += out[1]
                else:
                    allr += out
                done += 1
                if done % 50 == 0:
                    open(prog, "w").write(f"{tag} {name} {done}/{len(tl)} {time.time() - t0:.0f}s\n")
            write(os.path.join(CACHE, f"{tag}_{name}.csv.gz"), COLS, allr)
            if name == "heavy":
                write(os.path.join(CACHE, f"{tag}_ens.csv.gz"), ["t", "date", "n", "v_nak", "v_nak2", "v_fam", "v_copy", "v_dana", "v_steps", "tok", "hit", "cnt"], alle)
    open(prog, "w").write(f"{tag} DONE {time.time() - t0:.0f}s\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run"])
    ap.add_argument("--tag", default="real")
    ap.add_argument("--shuffle", default=None)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--blocks", type=int, default=200)
    ap.add_argument("--procs", type=int, default=3)
    ap.add_argument("--light-step", type=int, default=1)
    ap.add_argument("--no-heavy", action="store_true")
    a = ap.parse_args()
    os.makedirs(CACHE, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    run(a)
