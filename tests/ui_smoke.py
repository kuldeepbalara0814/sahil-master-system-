"""Asli browser (Playwright) me app kholo: main tab bina JS galti ke khulein. GitHub Action me chalta hai (phone par bhari).
  pip install playwright && python -m playwright install --with-deps chromium && python tests/ui_smoke.py"""
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 5088
BASE = f"http://127.0.0.1:{PORT}"
TABS = ["active", "aaj", "scan", "paper", "meri", "rank", "dost", "record", "data", "guide"]


def main():
    tmp = tempfile.mkdtemp()
    shutil.copytree(os.path.join(ROOT, "data"), tmp, dirs_exist_ok=True)           # asli data ko na chhede
    env = dict(os.environ, LAB_DATA_DIR=tmp, LAB_SYNC="0")
    srv = subprocess.Popen([sys.executable, "-c", f"import lab_server; lab_server.app.run(port={PORT}, threaded=True)"], cwd=ROOT, env=env)
    problems = []
    try:
        for _ in range(60):
            try:
                urllib.request.urlopen(BASE + "/api/healthz", timeout=2)
                break
            except Exception:
                time.sleep(1)
        with sync_playwright() as p:
            b = p.chromium.launch()
            page = b.new_page(viewport={"width": 390, "height": 840})               # phone jaisa
            page.on("pageerror", lambda e: problems.append(f"JS galti: {e}"))
            page.on("response", lambda r: r.status >= 500 and problems.append(f"{r.status} {r.url}"))
            page.goto(BASE, wait_until="load")
            for t in TABS:
                page.evaluate("t => go(t)", t)
                page.wait_for_function("() => !document.querySelector('#main > .load')", timeout=90000)
                if len(page.inner_text("#main")) < 20:
                    problems.append(f"tab {t} khali")
                wide = page.evaluate("() => document.documentElement.scrollWidth - window.innerWidth")
                print(f"tab {t}: ok (side scroll {wide}px)")
            page.evaluate("() => go('meri')")
            page.wait_for_selector(".wn-yaad", timeout=120000)
            os.makedirs(os.path.join(ROOT, "ui_shots"), exist_ok=True)
            page.screenshot(path=os.path.join(ROOT, "ui_shots", "meri_window.png"))
            b.close()
    finally:
        srv.terminate()
        shutil.rmtree(tmp, ignore_errors=True)
    for x in problems:
        print("DIKKAT:", x)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
