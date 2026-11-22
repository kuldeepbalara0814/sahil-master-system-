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
from lab import backtest as bt, band, data, export_xlsx, gapchain, idea  # noqa: E402
import datetime as dt  # noqa: E402

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


class GapFilterTests(unittest.TestCase):
    """Gap filter: number+palat, koi bhi game, ek jaisa gap, 3rd step aane wala / pass / nahi aaya."""

    @staticmethod
    def rows(*lines):
        d0 = dt.date(2026, 3, 2)
        return [(d0 + dt.timedelta(days=i), list(v), "t") for i, v in enumerate(lines)]

    def test_two_steps_then_due_then_pass(self):
        L = [[1, 2, 3, 4]] * 20
        L = [list(x) for x in L]
        L[0] = [15, 70, 71, 72]                  # din 0: 15 (FB)
        L[4] = [60, 51, 61, 62]                  # din 4: 51 = 15 ka palat (GB), gap 4
        rows = self.rows(*L[:8])                 # din 7 tak ka data
        r = gapchain.find(rows, gaps=[4], days=15)
        ch = [c for c in r["chains"] if c["cls"] == [15, 51]]
        self.assertEqual(len(ch), 1)
        self.assertEqual((ch[0]["status"], ch[0]["len"], ch[0]["due"]), ("aane", 2, "2026-03-10"))
        L[8] = [15, 0, 0, 0]
        rows = self.rows(*L[:9])                 # din 8: 3rd step aa gaya
        c = [c for c in gapchain.find(rows, gaps=[4], days=15)["chains"] if c["cls"] == [15, 51]][0]
        self.assertEqual((c["status"], c["len"], c["due"]), ("pass", 3, None))
        rows = self.rows(*(L[:8] + [[9, 9, 9, 9], [9, 9, 9, 9]]))        # din 8 par nahi aaya
        c = [c for c in gapchain.find(rows, gaps=[4], days=15)["chains"] if c["cls"] == [15, 51]][0]
        self.assertEqual(c["status"], "miss")

    def test_real_example_15_chain(self):
        """20 Nov: 12 Nov 15(GL) -> 16 Nov 51(GL) -> 20 Nov 15(GB), gap 4: pass; 18 Nov tak 'aane wala' (due 20)."""
        r = gapchain.find(ROWS, gaps=[4], days=15, end=dt.date(2026, 11, 20))
        self.assertTrue(any(c["cls"] == [15, 51] and c["status"] == "pass" for c in r["chains"]))
        r = gapchain.find(ROWS, gaps=[4], days=15, end=dt.date(2026, 11, 18))
        c = [c for c in r["chains"] if c["cls"] == [15, 51]][0]
        self.assertEqual((c["status"], c["due"]), ("aane", "2026-11-20"))

    def test_no_lookahead_and_colors(self):
        full = gapchain.find(ROWS, days=30, end=dt.date(2026, 11, 10))
        cut = gapchain.find([r for r in ROWS if r[0] <= dt.date(2026, 11, 10)], days=30)
        self.assertEqual(full["chains"], cut["chains"])
        r = gapchain.find(ROWS, days=15)
        for c in r["chains"]:                                                     # rang gap ke hisaab se
            self.assertEqual(c["color"], gapchain.GAP_COLORS[c["gap"]])
        self.assertGreater(len({c["color"] for c in r["chains"]}), 1)

    def test_api_and_excel(self):
        c = lab_server.app.test_client()
        g = c.get("/api/gaps?gaps=3,4,5,6,7&days=15").get_json()
        self.assertTrue(g["chains"] and g["marks"])
        self.assertEqual(c.get("/api/gaps?gaps=&days=15").status_code, 400)
        x = c.get("/api/export/record.xlsx?from=2026-09-01&to=2026-11-20&gaps=3,4,5,6,7&days=15")
        self.assertEqual(x.status_code, 200)
        wb = load_workbook(io.BytesIO(x.data))
        self.assertIn("Gap Filter", wb.sheetnames)
        ws = wb["Record"]
        filled = [cell for row in ws.iter_rows() for cell in row if cell.fill.fgColor.rgb in ("00FF9800", "FFFF9800", "00E040FB", "FFE040FB")]
        self.assertTrue(filled)
        self.assertTrue(any(isinstance(cell.value, str) and cell.value.endswith("?") for row in ws.iter_rows() for cell in row))


class BandTests(unittest.TestCase):
    def test_rashi_families_match_user(self):
        fam = {k: sorted(v) for k, v in band.RASHIS.items()}
        self.assertEqual(len(fam), 15)
        self.assertEqual(sorted(len(v) for v in fam.values()), [4] * 5 + [8] * 10)
        self.assertEqual(fam[band.key(1)], [1, 6, 10, 15, 51, 56, 60, 65])
        self.assertEqual(fam[band.key(2)], [2, 7, 20, 25, 52, 57, 70, 75])
        self.assertEqual(fam[band.key(3)], [3, 8, 30, 35, 53, 58, 80, 85])
        self.assertEqual(fam[band.key(11)], [11, 16, 61, 66])
        self.assertEqual(fam[band.key(33)], [33, 38, 83, 88])
        self.assertEqual(sorted(n for v in fam.values() for n in v), list(range(100)))

    def test_status_and_api(self):
        r = band.status(ROWS, 7)
        self.assertTrue(all(x["band"] >= 7 for x in r["rashis"] + r["numbers"]))
        last = ROWS[-1]
        for n in last[1]:                                    # aakhri line ke number 0 din band
            self.assertEqual([x["band"] for x in band.status(ROWS, 0)["numbers"] if x["n"] == n][0], 0)
        c = lab_server.app.test_client()
        j = c.get("/api/band?min=15").get_json()
        self.assertIn("history", j)
        self.assertEqual(c.get("/api/band?min=x").status_code, 400)


class PatternWindowTests(unittest.TestCase):
    def test_sheet_boards(self):
        c = lab_server.app.test_client()
        r = c.get("/api/pattern/sheet?from=2026-09&months=3&gaps=3,4,5,6,7&days=15").get_json()
        self.assertEqual(r["days"][0][0], "2026-09-01")
        self.assertEqual(len(r["days"]), 30 + 31 + 30)                       # Sep + Oct + Nov, har calendar din
        self.assertEqual([x for x in r["days"] if x[0] == "2026-11-30"][0][1], None)       # aakhri din / aage ka din khaali
        self.assertTrue(r["marks"] and r["gap"]["legend"]["3"] == gapchain.GAP_COLORS[3])
        auto = c.get("/api/pattern/sheet?months=2").get_json()               # pichle 2 mahine
        self.assertEqual(auto["from"][5:], "10")
        self.assertEqual(c.get("/api/pattern/sheet?from=x").status_code, 400)
        cells = {"2026-11-12|2": "FF9800", "2026-11-16|2": "E040FB"}
        self.assertEqual(c.post("/api/pattern/save", json={"cells": cells}).status_code, 401)         # PIN chahiye
        s = c.post("/api/pattern/save", json={"name": "t1", "from": "2026-09", "months": 3, "cells": cells}, headers=H)
        self.assertEqual(s.status_code, 200)
        bid = s.get_json()["id"]
        self.assertEqual(c.post("/api/pattern/save", json={"cells": {"bad": "FF9800"}}, headers=H).status_code, 400)
        self.assertEqual(c.post("/api/pattern/save", json={"cells": {"2026-11-12|9": "FF9800"}}, headers=H).status_code, 400)
        s2 = c.post("/api/pattern/save", json={"id": bid, "name": "t1b", "from": "2026-09", "months": 3, "cells": {"2026-11-12|2": "FF9800"}}, headers=H)
        L = c.get("/api/pattern/boards").get_json()
        self.assertEqual((len(L), L[0]["name"], len(L[0]["cells"])), (1, "t1b", 1))          # update hua, naya nahi bana
        self.assertEqual(c.post("/api/pattern/delete", json={"id": bid}, headers=H).get_json()["count"], 0)


class AutoFetchTests(unittest.TestCase):
    IST = dt.timezone(dt.timedelta(hours=5, minutes=30))

    def test_expected_last(self):
        f = lambda *a: lab_server.expected_last(dt.datetime(*a, tzinfo=self.IST))
        self.assertEqual(f(2026, 11, 22, 11, 0), dt.date(2026, 11, 21))          # subah 5:45 ke baad kal ki line
        self.assertEqual(f(2026, 11, 22, 4, 0), dt.date(2026, 11, 20))           # DS abhi khula nahi
        self.assertEqual(f(2026, 12, 1, 9, 0), dt.date(2026, 11, 29))            # 30 Nov chhuti: 29 ki line

    def test_no_auto_fetch_without_token(self):
        self.assertFalse(lab_server.maybe_auto_fetch(ROWS))


if __name__ == "__main__":
    unittest.main()
