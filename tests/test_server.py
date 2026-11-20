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
        self.assertEqual(t["single"]["games"], ["FD", "GL", "DS"])
        self.assertEqual(len(t["list10_static"]["GB"]), 10)
        t2 = self.c.get("/api/today?known=12,47").get_json()
        self.assertIsNotNone(t2["list10"]["GL"])
        self.assertIsNone(t2["list10"]["DS"])
        self.assertEqual(self.c.get("/api/today?known=1,2,3,4").status_code, 400)

    def test_write_needs_pin_and_valid_stake(self):
        if os.path.exists(os.path.join(TMP, "paper_ledger.json")):
            os.remove(os.path.join(TMP, "paper_ledger.json"))          # test alag-alag rahe
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
