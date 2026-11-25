#!/usr/bin/env python3
"""Sahil Lab khud-jaanch. JSON report banata hai; padho, theek karo, --clean se report mita do. Kuch badalta nahi, sirf padhta hai.

  python scripts/selfcheck.py            # data + files
  python scripts/selfcheck.py --live     # saath me live app (Render) aur GitHub Action
  python scripts/selfcheck.py --tests    # saath me saare tests
  python scripts/selfcheck.py --data --no-file   # sirf data (GitHub Action ka pehredaar)
  python scripts/selfcheck.py --clean    # report mitao
Exit code 1 = koi 'error' mila."""
import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from lab import data, partial, tick  # noqa: E402

REPORT = os.path.join(ROOT, "selfcheck_report.json")
LIVE = "https://sahil-lab.onrender.com"
REPO = "kuldeepbalara0814/sahil-master-system-"
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
TESTS = ["tests.test_lab", "tests.test_core", "tests.test_fetcher", "tests.test_paper", "tests.test_server"]
problems, info = [], {}


def add(level, area, msg):
    problems.append({"level": level, "area": area, "msg": str(msg)[:400]})


def check_data(folder):
    try:
        rows = data.load(os.path.join(folder, "results.csv"))
    except Exception as e:
        add("error", "data", f"results.csv padhi nahi gayi: {type(e).__name__}: {e}")
        return None
    for p in data.validate(rows)[:10]:
        add("error", "data", p)
    dates = [r[0] for r in rows]
    if any(b <= a for a, b in zip(dates, dates[1:])):
        add("error", "data", "tarikh dohri ya ulti")
    for a, b in zip(dates[-200:], dates[-199:]):
        if (b - a).days > 3:
            add("warn", "data", f"beech me din gayab: {a} ke baad {b}")
    info["data"] = {"din": len(rows), "aakhri": dates[-1].isoformat()}
    for name in sorted(os.listdir(folder)):
        p = os.path.join(folder, name)
        if name.endswith(".json"):
            try:
                with open(p, encoding="utf-8") as f:
                    obj = json.load(f)
            except (OSError, ValueError) as e:
                add("error", "files", f"{name} kharab JSON: {e}")
                continue
            if name == "patterns_today.json":
                for e in obj.get("errors") or []:
                    add("error", "scan", f"{e.get('pattern')}: {e.get('error')}")
            if name == "partial_results.json" and obj.get("results") and not partial.clean(obj, dates[-1]):
                add("warn", "partial", "purani aadhi line padi hai (nuksan nahi)")
        if os.path.getsize(p) > 900_000 and name.endswith(".json"):
            add("warn", "size", f"{name} {os.path.getsize(p) // 1024} KB: 1 MB se bada hua to GitHub sync dheema hoga")
    try:
        with open(os.path.join(folder, "partial_results.json"), encoding="utf-8") as f:
            part = partial.clean(json.load(f), dates[-1])
    except (OSError, ValueError):
        part = None
    baaki = tick.due(dt.datetime.now(IST), rows, part)
    info["baaki_result"] = baaki
    return rows


def get(url, timeout=90):
    t = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": "sahil-selfcheck"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(), time.time() - t
    except urllib.error.HTTPError as e:
        return e.code, e.read(), time.time() - t
    except Exception as e:
        return 0, str(e).encode(), time.time() - t


def check_live():
    code, body, sec = get(LIVE + "/api/health")
    if code != 200:
        add("error", "live", f"app nahi khula (code {code}): {body[:150]!r}")
        return
    h = json.loads(body)
    info["live"] = {k: h.get(k) for k in ("last_date", "expected_last", "due", "partial", "auto_last", "now_ist")}
    info["live"]["jagne_sec"] = round(sec, 1)
    if h.get("behind_days"):
        add("error", "live", f"app ka data {h['behind_days']} din peeche")
    if h.get("due"):
        add("warn", "live", f"ye result aane chahiye the, abhi nahi aaye: {h['due']}")
    for e in (h.get("auto_last") or {}).get("errors") or []:
        add("error", "auto-fetch", e)
    for e in h.get("scan_errors") or []:
        add("error", "live-scan", e)
    if h.get("github") and not h.get("can_write"):
        add("error", "live", "GITHUB_TOKEN nahi: app kuch save nahi kar sakta")
    for path in ("/", "/static/app.js", "/static/alerts.js", "/static/tabs_window.js", "/api/status", "/api/alerts", "/api/window", "/api/yaad", "/api/rank", "/api/active", "/api/scanner"):
        code, body, sec = get(LIVE + path)
        if code != 200:
            add("error", "live", f"{path} code {code}")
        elif sec > 20:
            add("warn", "live", f"{path} bahut dheema: {sec:.0f} sec")


def check_github():
    code, body, _ = get(f"https://api.github.com/repos/{REPO}/actions/runs?per_page=10", 30)
    if code != 200:
        add("warn", "github", f"Actions ki jankari nahi mili (code {code})")
        return
    runs = json.loads(body).get("workflow_runs", [])
    info["actions"] = [f"{r['created_at']} {r['name']} {r['head_sha'][:7]} {r['conclusion']}" for r in runs[:6]]
    for name in {r["name"] for r in runs}:
        done = [r for r in runs if r["name"] == name and r["status"] == "completed"]
        if done and done[0]["conclusion"] != "success":
            add("error", "github", f"{name} ki pichli run {done[0]['conclusion']}: {done[0]['html_url']}")
    daily = [r for r in runs if r["name"] == "daily-update"]
    if daily:
        age = (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(daily[0]["created_at"].replace("Z", "+00:00"))).total_seconds() / 3600
        info["action_ghante_pehle"] = round(age, 1)
        if age > 14:
            add("warn", "github", f"daily-update {age:.0f} ghante se nahi chali (GitHub schedule chhod raha hai)")
    code, body, _ = get(f"https://api.github.com/repos/{REPO}", 30)
    if code == 200:
        info["repo_mb"] = round(json.loads(body).get("size", 0) / 1024, 1)
        if info["repo_mb"] > 500:
            add("warn", "github", f"repo {info['repo_mb']} MB (1 GB se neeche rakho)")


def git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True).stdout.strip()


def check_git():
    if not os.path.isdir(os.path.join(ROOT, ".git")):
        return
    dirty = git("status", "--porcelain")
    if dirty:
        add("warn", "git", "bina commit ke badlav: " + ", ".join(x[3:] for x in dirty.splitlines()[:8]))
    ahead = git("log", "--oneline", "@{u}..HEAD")
    if ahead:
        add("warn", "git", f"push nahi hue commit: {ahead.splitlines()[:5]}")
    info["head"] = git("log", "-1", "--format=%h %s")[:90]


def check_tests():
    r = subprocess.run([sys.executable, "-m", "unittest", *TESTS], cwd=ROOT, capture_output=True, text=True)
    tail = r.stderr.strip().splitlines()
    info["tests"] = tail[-3:]
    if r.returncode:
        for line in [x for x in tail if x.startswith(("FAIL:", "ERROR:"))][:10]:
            add("error", "tests", line)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Sahil Lab khud-jaanch")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--tests", action="store_true")
    ap.add_argument("--data", action="store_true", help="sirf data aur files")
    ap.add_argument("--dir", default=os.path.join(ROOT, "data"))
    ap.add_argument("--no-file", action="store_true")
    ap.add_argument("--clean", action="store_true")
    a = ap.parse_args(argv)
    if a.clean:
        if os.path.exists(REPORT):
            os.remove(REPORT)
        print("report mita di")
        return 0
    problems.clear()
    info.clear()
    check_data(a.dir)
    if not a.data:
        check_git()
        if a.live:
            check_live()
            check_github()
        if a.tests:
            check_tests()
    errors = sum(p["level"] == "error" for p in problems)
    rep = {"time": dt.datetime.now(IST).isoformat(timespec="seconds"), "ok": not errors, "errors": errors, "warnings": len(problems) - errors,
           "problems": problems, "info": info}
    if not a.no_file:
        with open(REPORT, "w", encoding="utf-8") as f:
            json.dump(rep, f, ensure_ascii=False, indent=1)
        print("report:", REPORT)
    print(f"{'THEEK' if not errors else 'DIKKAT'}: {errors} error, {len(problems) - errors} warning")
    for p in problems:
        print(f"  [{p['level']}] {p['area']}: {p['msg']}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
