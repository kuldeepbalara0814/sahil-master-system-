import datetime as dt
import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
TMP = tempfile.mkdtemp()
for f in os.listdir(os.path.join(ROOT, "data")):
    if f.endswith((".csv", ".json")):
        shutil.copy(os.path.join(ROOT, "data", f), TMP)
os.environ.update(LAB_DATA_DIR=TMP, LAB_SYNC="0", ADMIN_PIN="1234")
import lab_server  # noqa: E402

H = {"X-Admin-Pin": "1234"}


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = lab_server.app.test_client()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TMP, ignore_errors=True)

    def test_status_and_friends(self):
        s = self.c.get("/api/status").get_json()
        self.assertGreaterEqual(s["days"], 4905)
        f = self.c.get("/api/friends/30").get_json()
        self.assertEqual(set(f["friends"]), {"poora", "last3m", "month"})
        self.assertEqual(len(f["friends"]["poora"]), 10)
        self.assertEqual(self.c.get("/api/friends/100").status_code, 400)

    def test_today_lists(self):
        t = self.c.get("/api/today").get_json()
        self.assertEqual(len(t["dost"]), 4)
        self.assertEqual(set(t["dost"][0]["top"]), {"poora", "last3m", "month"})
        self.assertEqual(t["single"]["games"], ["FD", "GL", "DS"])
        self.assertEqual(len(t["list10_static"]["GB"]), 10)
        t2 = self.c.get("/api/today?known=12,47").get_json()
        self.assertIsNotNone(t2["list10"]["GL"])
        self.assertIsNone(t2["list10"]["DS"])
        self.assertEqual(self.c.get("/api/today?known=1,2,3,4").status_code, 400)

    def test_write_needs_pin_and_valid_stake(self):
        led = os.path.join(lab_server.DATA_DIR, "paper_ledger.json")      # lab_server ek hi baar import hota hai (pehle wale test ka dir)
        if os.path.exists(led):
            os.remove(led)                                              # test alag-alag rahe
        r = self.c.post("/api/paper/place", json={"strategy": "auto", "stake": 5})
        self.assertEqual(r.status_code, 401)
        r = self.c.post("/api/paper/place", json={"strategy": "auto", "stake": 7}, headers=H)
        self.assertEqual(r.status_code, 400)
        r = self.c.post("/api/paper/place", json={"strategy": "auto", "stake": 5}, headers=H)
        self.assertEqual(r.status_code, 200)
        added = r.get_json()["added"]
        self.assertGreater(added, 0)
        r2 = self.c.post("/api/paper/place", json={"strategy": "auto", "stake": 5}, headers=H).get_json()
        self.assertEqual(r2["added"], 0)                              # dobara nahi
        p = self.c.get("/api/paper").get_json()
        self.assertGreater(p["summary"]["single"]["pending"], 0)
        m = self.c.post("/api/paper/place", json={"strategy": "manual", "numbers": [7, 70], "games": ["FD", "GB"], "stake": 10}, headers=H).get_json()
        self.assertEqual(m["added"], 4)

    def test_monitor_and_drift_and_overview(self):
        m = self.c.get("/api/monitor").get_json()
        self.assertEqual(set(m["strategies"]), {"single", "list10s", "list10"})
        self.assertEqual(self.c.get("/api/drift").status_code, 200)
        o = self.c.get("/api/overview/month").get_json()
        self.assertEqual(len(o), 100)
        self.assertEqual(self.c.get("/api/overview/xx").status_code, 400)

    def test_fetch_uses_fake_site(self):
        from lab import fetcher, update
        fx = os.path.join(ROOT, "tests", "fixtures")

        def fake(y, m):
            p = os.path.join(fx, f"chart_{y}-{m:02d}.html")
            if not os.path.exists(p):
                raise fetcher.FetchError("fixture nahi")
            return open(p, encoding="utf-8").read()
        rep = update.run(today=dt.date(2026, 11, 21), data_dir=TMP, fetch_fn=fake, pause=0)     # abhi ki file par: kuch naya nahi
        self.assertEqual(rep["added"], [])
        self.assertEqual(self.c.post("/api/fetch", headers={"X-Admin-Pin": "bad"}).status_code, 401)

    def test_download_and_404(self):
        r = self.c.get("/api/download/results.csv")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.data.startswith(b"date,fd,gb,gl,ds"))
        self.assertEqual(self.c.get("/api/nope").status_code, 404)


if __name__ == "__main__":
    unittest.main()


class NoTokenSyncTests(unittest.TestCase):
    def test_write_refused_without_token_when_sync_on(self):
        from lab import gh
        import time
        lab_server.SYNC = gh.Sync(TMP, "o/r", "main", "")
        lab_server.SYNC.last = time.time()            # pull chhod do (test me internet nahi)
        try:
            r = lab_server.app.test_client().post("/api/paper/place", json={"strategy": "manual", "numbers": [1], "games": ["FD"], "stake": 5}, headers=H)
            self.assertEqual(r.status_code, 502)
            self.assertIn("GITHUB_TOKEN", r.get_json()["error"])
        finally:
            lab_server.SYNC = None


class CardRouteTests(unittest.TestCase):
    """Roz ka card (017): /api/card ka haal, locked card ki JPG, galat/na bani tarikh."""

    def test_card_routes(self):
        c = lab_server.app.test_client()
        v = c.get("/api/card").get_json()
        self.assertIn("play_date", v)
        self.assertIn("kyun", v)
        cp = os.path.join(lab_server.DATA_DIR, "cards.json")
        old = open(cp, encoding="utf-8").read() if os.path.exists(cp) else None
        try:
            cs = json.load(open(cp, encoding="utf-8")) if old else {"days": {}}
            cs["days"]["2026-11-28"] = {"solid": [58, 79, 85, 97], "spot": [10, 15, 24, 42, 51, 52, 59, 74]}
            with open(cp, "w", encoding="utf-8") as f:
                json.dump(cs, f)
            r = c.get("/api/card/2026-11-28.jpg")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.mimetype, "image/jpeg")
            self.assertTrue(r.data.startswith(b"\xff\xd8"))
            self.assertIn("attachment", c.get("/api/card/2026-11-28.jpg?download=1").headers.get("Content-Disposition", ""))
            self.assertEqual(c.get("/api/card/1999-01-01.jpg").status_code, 404)
            self.assertEqual(c.get("/api/card/kal.jpg").status_code, 400)
        finally:
            if old is None:
                os.remove(cp)
            else:
                with open(cp, "w", encoding="utf-8") as f:
                    f.write(old)
