"""Roz ka kaam (ek command):  python -m lab.update

  1. site se nayi lines laao (kabhi duplicate nahi, purani line nahi badlegi)
  2. paper trading: jo bet ka result aa gaya use jeet/haar likho, aaj ki nayi bet lagao
  3. dost list ka snapshot lo aur purane se milao  ->  "10 par pehle 93 tha ab 94" (drift log)
  4. strategy monitor (hit % vs break-even) dobara banao
"""
import argparse
import datetime as dt
import json
import os
import sys

from . import data, fetcher, friends, monitor, paper

KEEP_LOG = 90


def _path(data_dir, name):
    return os.path.join(data_dir, name)


def _load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def _save_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def run(fetch=True, today=None, stake=5, auto_bets=True, data_dir=None, fetch_fn=fetcher.fetch_month, pause=1.5):
    data_dir = data_dir or os.path.dirname(data.DATA_FILE)
    csv_path = _path(data_dir, "results.csv")
    rep = {"time": dt.datetime.now().isoformat(timespec="seconds"), "added": [], "skipped": [], "conflicts": [], "errors": [], "problems": []}
    rows = data.load(csv_path)
    # 1) fetch
    if fetch:
        new, info = fetcher.new_lines(rows, today=today, fetch=fetch_fn, pause=pause)
        rep["errors"] = info["errors"]
        merged, added, skipped, conflicts = data.merge_new(rows, new)
        rep["added"] = [d.isoformat() for d in added]
        rep["skipped"] = [(d.isoformat(), why) for d, why in skipped]
        rep["conflicts"] = [(d.isoformat(), a, b) for d, a, b in conflicts]
        if added:
            data.save(merged, csv_path)
            rows = merged
    rep["problems"] = data.validate(rows)
    rep["last_date"] = rows[-1][0].isoformat()
    rep["days"] = len(rows)
    # 2) paper trading
    ledger = _load_json(_path(data_dir, "paper_ledger.json"), None) or paper.new_ledger()
    rep["settled"] = paper.settle(ledger, rows)
    rep["new_bets"] = paper.auto_place(ledger, rows, stake) if auto_bets else 0
    _save_json(_path(data_dir, "paper_ledger.json"), ledger)
    # 3) dost list drift
    fr = friends.Friends(rows)
    snap = fr.snapshot()
    prev = _load_json(_path(data_dir, "friends_snapshot.json"), None)
    changes = friends.drift(prev, snap) if prev and prev.get("asof") != snap["asof"] else []
    log = _load_json(_path(data_dir, "drift_log.json"), [])
    if changes:
        log.append({"asof": snap["asof"], "changes": [c for c in changes if c["period"] != "poora"] + [c for c in changes if c["period"] == "poora"]})
    _save_json(_path(data_dir, "drift_log.json"), log[-KEEP_LOG:])
    _save_json(_path(data_dir, "friends_snapshot.json"), snap)
    rep["drift_changes"] = len(changes)
    # 4) monitor
    _save_json(_path(data_dir, "monitor.json"), monitor.health(rows))
    # 4b) har game ka alag record file (git me: game_fb.csv, game_gb.csv, game_gl.csv, game_ds.csv)
    try:
        from . import gamefiles
        gamefiles.write_files(rows, data_dir)
    except Exception as e:
        rep.setdefault("scan_errors", []).append(f"game files nahi bani: {type(e).__name__}: {e}")
    # 5) pattern scan (sikhaye hue pattern: aaj kya ban raha hai). Galti ho to baaki kaam na ruke.
    try:
        from . import scanner
        srep = scanner.run(rows)
        try:
            from . import active
            lp = _path(data_dir, "active_log.json")
            _save_json(lp, active.merge(_load_json(lp, None) or active.new_log(), srep, source="auto"))
        except Exception as e:
            rep["scan_errors"] = [f"active log nahi bana: {type(e).__name__}: {e}"]
        _save_json(_path(data_dir, "patterns_today.json"), srep)      # merge ke baad: items par "new" nishan
        rep.setdefault("scan_errors", [])
        rep["scan_errors"] += [f"{e['pattern']}: {e['error']}" for e in srep["errors"]]
    except Exception as e:
        rep["scan_errors"] = [f"scan chala hi nahi: {type(e).__name__}: {e}"]
    # log
    flog = _load_json(_path(data_dir, "fetch_log.json"), [])
    flog.append({k: rep[k] for k in ("time", "added", "errors", "settled", "new_bets", "last_date")})
    _save_json(_path(data_dir, "fetch_log.json"), flog[-KEEP_LOG:])
    return rep


def main(argv=None):
    ap = argparse.ArgumentParser(description="Sahil Lab roz ka update")
    ap.add_argument("--no-fetch", action="store_true", help="site se mat laao, sirf baaki update karo")
    ap.add_argument("--stake", type=int, default=5, help="paper bet ka stake (5 ke multiple)")
    ap.add_argument("--no-auto-bets", action="store_true")
    a = ap.parse_args(argv)
    paper.check_stake(a.stake)
    r = run(fetch=not a.no_fetch, stake=a.stake, auto_bets=not a.no_auto_bets)
    print(f"Aakhri line: {r['last_date']} | kul {r['days']} din")
    print(f"Nayi lines: {', '.join(r['added']) or 'koi nahi'}")
    if r["errors"]:
        print("Dikkat:", *r["errors"], sep="\n  ")
    if r["conflicts"]:
        print("Site aur file me farak (file nahi badli):", r["conflicts"])
    if r["problems"]:
        print("Data me samasya:", *r["problems"], sep="\n  ")
    print(f"Paper: {r['settled']} bet ka result likha, {r['new_bets']} nayi bet lagi | dost badlaav: {r['drift_changes']}")
    return 1 if (r["problems"] or (r["errors"] and not r["added"] and r["errors"])) else 0


if __name__ == "__main__":
    sys.exit(main())
