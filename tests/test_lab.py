"""Lab (idea parser + backtest) aur Excel/Record ke test."""
import atexit
import io
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
atexit.register(shutil.rmtree, TMP, True)         # lab_server ek hi baar import hota hai, isliye dir saath me hi hatao

import numpy as np  # noqa: E402
from openpyxl import load_workbook  # noqa: E402

import lab_server  # noqa: E402
from lab import backtest as bt, data, export_xlsx, idea  # noqa: E402

H = {"X-Admin-Pin": "1234"}
ROWS = data.load(os.path.join(ROOT, "data", "results.csv"))


class ParserTests(unittest.TestCase):
    def sp(self, text):
        r = idea.parse(text)
        self.assertTrue(r["ok"], r)
        return r["spec"]

    def test_simple_rule(self):
        s = self.sp("kal GB me jo aaya wahi aaj FB me lagao")
        self.assertEqual((s["on"], s["sources"], s["ops"]), (["FD"], [{"game": "GB", "lag": 1}], ["same"]))

    def test_palat_multi_targets_and_day(self):
        s = self.sp("kal GB ka palat aaj GL aur DS me shukravar ko")
        self.assertEqual((s["on"], s["ops"], s["days"]), (["GL", "DS"], ["palat"], [4]))

    def test_fixed_dost_and_value(self):
        s = self.sp("jab GB me 30 aaye to agle din DS me 30 ke top 4 dost lagao")
        self.assertEqual((s["base"], s["fixed"], s["value"], s["ops"]), ("fixed", [30], 30, ["dost4"]))

    def test_hot_and_cold(self):
        h = self.sp("pichle 20 din me sabse zyada aaye wo 8 number GB me")
        self.assertEqual((h["mode"], h["window"], h["topk"]), ("hot", 20, 8))
        c = self.sp("jo number sabse der se nahi aaya wo 6 number FB me")
        self.assertEqual((c["mode"], c["topk"]), ("cold", 6))

    def test_impossible_and_unclear(self):
        r = idea.parse("aaj GL me jo aaye wo FB me lagao")           # GL baad me khulta hai
        self.assertFalse(r["ok"])
        self.assertFalse(idea.parse("mujhe kuch lagana hai")["ok"])
        self.assertFalse(idea.parse("")["ok"])

    def test_clean_rejects_bad_numbers(self):
        with self.assertRaises(ValueError):
            idea.clean({"mode": "rule", "on": ["FD"], "base": "fixed", "fixed": [100]})
        with self.assertRaises(ValueError):
            idea.clean({"mode": "rule", "on": []})


class BacktestTests(unittest.TestCase):
    SPECS = [
        {"mode": "rule", "on": ["FD", "DS"], "sources": [{"game": "GB", "lag": 1}], "ops": ["same", "palat"]},
        {"mode": "rule", "on": ["GL"], "sources": [{"game": "FD", "lag": 0}], "ops": ["family"]},
        {"mode": "rule", "on": ["FD"], "sources": [{"game": "GB", "lag": 1}], "ops": ["dost3"]},
        {"mode": "hot", "on": ["GB"], "window": 25, "topk": 10},
        {"mode": "cold", "on": ["FD"], "topk": 10},
    ]

    def test_no_lookahead(self):
        """Din i ki list sirf i tak ke data se bane: aage ka data kaat do to wahi list aani chahiye."""
        full = bt.History(ROWS)
        for spec in self.SPECS:
            spec = idea.clean(spec)
            for i in (400, 1500, 3000, 4800):
                for t in (bt.GAMES.index(g) for g in spec["on"]):
                    cut = bt.History(ROWS[:i + 1])
                    d1 = bt.DostWalk(full) if any(o.startswith("dost") for o in spec.get("ops", [])) else None
                    d2 = bt.DostWalk(cut) if d1 else None
                    a = bt.numbers_for(full, spec, i, t, d1)
                    b = bt.numbers_for(cut, spec, i, t, d2)
                    if d1:                                       # dost ka checkpoint alag: sirf 'pehle ka data' wali baat
                        continue
                    self.assertEqual(a, b, (spec, i, t))

    def test_run_shapes_and_money(self):
        r = bt.run(ROWS, idea.clean(self.SPECS[0]))
        s = r["summary"]
        self.assertGreater(s["bets"], 1000)
        self.assertAlmostEqual(s["hit_pct"], s["hits"] / s["numbers"])
        self.assertEqual(s["cost"], 5 * s["numbers"])
        # net = 5*95*hits(<40 number) - cost  (yahan sab bet <40 number ki hain)
        self.assertEqual(s["net"], 5 * 95 * s["hits"] - s["cost"])
        self.assertIn(r["verdict"]["color"], ("hara", "peela", "laal", "kam"))
        self.assertTrue(r["today"]["FD"]["numbers"])
        self.assertEqual(sum(y["bets"] for y in r["years"]), s["bets"])

    def test_random_is_not_great(self):
        """Mix kiya hua (shuffle) data par koi idea ka asar nahi hona chahiye: hit % random (1%) ke aas-paas."""
        rng = np.random.default_rng(7)
        R = np.array([r[1] for r in ROWS])
        for g in range(4):
            R[:, g] = rng.permutation(R[:, g])
        fake = [(r[0], [int(x) for x in R[i]], "") for i, r in enumerate(ROWS)]
        s = bt.run(fake, idea.clean(self.SPECS[0]))["summary"]
        self.assertLess(abs(s["hit_pct"] - 0.01), 0.002)

    def test_lag0_not_in_today(self):
        r = bt.run(ROWS, idea.clean(self.SPECS[1]))
        self.assertEqual(r["today"]["GL"]["numbers"], [])
        self.assertIn("result", r["today"]["GL"]["why"])


class ExportAndApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = lab_server.app.test_client()


    def test_xlsx_layout(self):
        blob = export_xlsx.build(ROWS, data.parse_date("2025-11-20"), data.parse_date("2026-02-28"))
        wb = load_workbook(io.BytesIO(blob))
        ws = wb["Record"]
        self.assertIn("YEAR 2025", ws["A1"].value)
        self.assertEqual([ws.cell(3, c).value for c in (2, 3, 4, 5)], ["FB", "GB", "GL", "DS"])
        by = {r[0]: r[1] for r in ROWS}
        d = data.parse_date("2025-12-05")
        self.assertEqual(ws.cell(8, 1).value, 5)                                         # date 5 ki row
        self.assertEqual([ws.cell(8, 2 + 4 + j).value for j in range(4)], by[d])         # Dec-25 ke 4 column
        self.assertEqual(ws.cell(8, 2).number_format, "00")
        t = wb["Sada Table"]
        self.assertEqual(t.max_row, len([r for r in ROWS if data.parse_date("2025-11-20") <= r[0] <= data.parse_date("2026-02-28")]) + 1)

    def test_record_api(self):
        r = self.c.get("/api/record?from=2026-10-01&to=2026-10-31").get_json()
        self.assertGreater(r["count"], 20)
        self.assertEqual(self.c.get("/api/record?from=junk").status_code, 400)
        self.assertEqual(self.c.get("/api/record?from=2026-05-01&to=2026-01-01").status_code, 400)
        x = self.c.get("/api/export/record.xlsx?from=2026-10-01&to=2026-10-31")
        self.assertEqual(x.status_code, 200)
        self.assertIn("xlsx", x.headers["Content-Disposition"])
        self.assertEqual(self.c.get("/api/export/record.xlsx?from=2031-01-01").status_code, 400)

    def test_lab_api_and_save(self):
        p = self.c.post("/api/lab/parse", json={"text": "kal GB ka palat aaj FB me"}).get_json()
        self.assertTrue(p["ok"])
        t = self.c.post("/api/lab/test", json={"spec": p["spec"]}).get_json()
        self.assertIn("verdict", t["result"])
        self.assertEqual(self.c.post("/api/lab/test", json={"spec": {"mode": "rule", "on": []}}).status_code, 400)
        self.assertEqual(self.c.post("/api/lab/save", json={"spec": p["spec"]}).status_code, 401)       # PIN chahiye
        s = self.c.post("/api/lab/save", json={"spec": p["spec"], "name": "mera idea"}, headers=H)
        self.assertEqual(s.status_code, 200)
        L = self.c.get("/api/lab/ideas").get_json()
        self.assertEqual(L[0]["name"], "mera idea")
        d = self.c.post("/api/lab/delete", json={"id": L[0]["id"]}, headers=H)
        self.assertEqual(d.get_json()["count"], 0)


if __name__ == "__main__":
    unittest.main()
