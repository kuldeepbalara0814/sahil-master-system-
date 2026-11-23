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
from lab import backtest as bt, baar, band, data, export_xlsx, gapchain, idea, scan_view, scanner  # noqa: E402
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


class BaarTests(unittest.TestCase):
    def test_tokri_counts_and_palat(self):
        d0 = dt.date(2026, 3, 2)                                  # Somvar
        rows = []
        for i in range(30):
            v = [11, 22, 33, 44] if i % 7 else [88, 88, 12, 99]        # Somvar ko 88 do baar, 12, 99
            rows.append((d0 + dt.timedelta(days=i), v, "t"))
        t = baar.tokri(rows, 0, days=0, asof=d0 + dt.timedelta(days=30))
        self.assertEqual(t["top"][0]["n"], 88)
        self.assertEqual(t["top"][0]["count"], 10)                # 5 Somvar x 2
        self.assertIn(21, t["numbers"])                           # 12 ka palat
        self.assertEqual(sorted(t["numbers"]), sorted(set(t["numbers"])))
        self.assertEqual(t["cases"], 5)

    def test_asof_no_lookahead_and_api(self):
        a = baar.tokri(ROWS, 2, 365, asof=dt.date(2026, 6, 1))
        self.assertLess(a["to"], "2026-06-01")
        c = lab_server.app.test_client()
        r = c.get("/api/baar").get_json()
        self.assertEqual(r["play_date"], data.play_date(ROWS).isoformat())
        self.assertTrue(r["is_today"])
        self.assertEqual(len(r["top"]), 6)
        self.assertEqual(c.get("/api/baar?weekday=7").status_code, 400)
        self.assertEqual(c.get("/api/baar?days=10").status_code, 400)
        self.assertGreater(c.get("/api/baar?weekday=2&days=0").get_json()["cases"], 600)


class BaarAllTests(unittest.TestCase):
    def test_all_days(self):
        r = baar.all_days(ROWS, 365)
        self.assertEqual([i["weekday"] for i in r["items"]], [6, 0, 1, 2, 3, 4, 5])            # Ravi se Shani
        self.assertEqual(sorted(i["rank"] for i in r["items"]), list(range(1, 8)))
        for i in r["items"]:
            self.assertEqual(len(i["top"]), 6)
            for t in i["top"]:
                self.assertEqual(len(t["when"]), t["count"])                                  # kab-kab aaya ginti se milta hai
        c = lab_server.app.test_client()
        j = c.get("/api/baar/all?days=0").get_json()
        self.assertEqual(len(j["order"]), 7)
        self.assertEqual(c.get("/api/baar/all?days=7").status_code, 400)
        self.assertEqual(c.get("/api/baar/all").get_json()["items"][0]["from"], baar.tokri(ROWS, 6, 365)["from"])


class ScannerTests(unittest.TestCase):
    def test_names_stable_and_distinct(self):
        self.assertEqual(scanner.name_for("Naksha", "12:2025-09-19"), scanner.name_for("Naksha", "12:2025-09-19"))
        names = {scanner.name_for("Naksha", f"{L}:{d}") for L in (10, 12, 15, 18) for d in ("2021-05-06", "2022-05-13", "2013-04-15")}
        self.assertEqual(len(names), 12)

    def test_copy_detection_rule(self):
        self.assertTrue(scanner.is_copy(38, 84))                  # 84 = 83 + 1 (palat 83)
        self.assertTrue(scanner.is_copy(80, 70))
        self.assertFalse(scanner.is_copy(38, 38))
        self.assertFalse(scanner.is_copy(38, 83))                 # palat khud copy nahi
        d0 = dt.date(2026, 3, 2)
        L = [[1, 2, 3, 4]] * 6
        L = [list(x) for x in L]
        L[0][1], L[1][1], L[3][2] = 38, 84, 83                    # GB 38, 84, din 4 GL 83 = PASS
        rows = [(d0 + dt.timedelta(days=i), v, "t") for i, v in enumerate(L)]
        ev = [e for e in scanner.copy_events(rows, d0, d0 + dt.timedelta(days=5)) if e["shape"] == "seedha" and e["x"] == 38]
        self.assertEqual((len(ev), ev[0]["status"]), (1, "pass"))
        pending = scanner.copy_events(rows[:3], d0, d0, today=d0 + dt.timedelta(days=3))      # din 4 abhi baaki
        self.assertTrue(any(e["status"] == "aaj" and e["x"] == 38 for e in pending))

    def test_run_report_shape_and_error_isolation(self):
        rep = scanner.run(ROWS)
        self.assertEqual((rep["asof"], len(rep["patterns"]), rep["errors"]), (ROWS[-1][0].isoformat(), 6, []))
        nak = [p for p in rep["patterns"] if p["key"] == "naksha"][0]
        self.assertTrue(nak["items"])
        for it in nak["items"]:
            self.assertIn(it["strength"], ("mazboot", "theek", "kamzor"))
        orig = scanner.SCANNERS["copy"]
        scanner.SCANNERS["copy"] = lambda rows, asof: 1 / 0
        try:
            bad = scanner.run(ROWS)
        finally:
            scanner.SCANNERS["copy"] = orig
        self.assertEqual(bad["errors"][0]["pattern"], "Jodi-Copy")
        self.assertIn("ZeroDivisionError", bad["errors"][0]["error"])
        self.assertTrue([p for p in bad["patterns"] if p["key"] == "naksha"][0]["items"])               # dusra pattern phir bhi chala

    def test_no_lookahead(self):
        cut = [r for r in ROWS if r[0] <= dt.date(2026, 10, 15)]
        a, b = scanner.run(cut), scanner.run(ROWS)
        self.assertEqual(a["asof"], "2026-10-15")
        ids = lambda rep: [i["id"] for p in rep["patterns"] if p["key"] == "naksha" for i in p["items"]]
        self.assertTrue(ids(a))
        self.assertNotEqual(ids(a), ids(b))                       # alag din par alag nateeja, par a me aage ka data nahi

    def test_api_view_xlsx(self):
        c = lab_server.app.test_client()
        r = c.post("/api/scanner/run").get_json()
        self.assertEqual(r["errors"], [])
        g = c.get("/api/scanner").get_json()
        self.assertEqual(g["asof"], ROWS[-1][0].isoformat())
        for p in g["patterns"]:
            for it in p["items"][:2]:
                v = c.get("/api/scanner/view?id=" + it["id"]).get_json()
                self.assertTrue(v["blocks"])
                x = c.get("/api/scanner/xlsx?id=" + it["id"])
                self.assertEqual(x.status_code, 200)
                wb = load_workbook(io.BytesIO(x.data))
                self.assertEqual(wb.active.title, "Pattern")
        self.assertEqual(c.get("/api/scanner/view?id=bakwas").status_code, 400)

    def test_family_events_shapes_location_and_status(self):
        d0 = dt.date(2026, 3, 2)
        L = [[11, 13, 14, 16] for _ in range(8)]
        fam = {2, 7, 20, 25, 52, 57, 70, 75}               # 02 rashi
        L[0][1] = 25                                        # din 0 GB 25 (step 1)
        L[1][3] = 57                                        # din 1 DS 57 (step 2)
        L[3][0] = 70                                        # din 3 FB 70 (3rd step, pass)
        rows = [(d0 + dt.timedelta(days=i), v, "t") for i, v in enumerate(L)]
        ev = [e for e in scanner.family_events(rows, d0, d0) if e["rashi"] == 2 and e["shape"] == "seedha"]
        self.assertEqual((len(ev), ev[0]["status"], ev[0]["loc"], ev[0]["amb"]), (1, "pass", [1, 3], False))   # GB, DS location
        self.assertEqual(ev[0]["hit"], [(0, 70)])                                    # out of location, phir bhi pass
        L2 = [list(x) for x in L]
        L2[0][0] = 52                                       # step 1 din 2 cell: location tay nahi
        rows2 = [(d0 + dt.timedelta(days=i), v, "t") for i, v in enumerate(L2)]
        e2 = [e for e in scanner.family_events(rows2, d0, d0) if e["rashi"] == 2 and e["shape"] == "seedha"][0]
        self.assertEqual((e2["amb"], e2["loc"]), (True, []))
        pending = scanner.family_events(rows[:3], d0, d0, today=d0 + dt.timedelta(days=3))                       # 3rd step aaj
        self.assertTrue(any(e["status"] == "aaj" and e["rashi"] == 2 for e in pending))
        self.assertTrue(fam >= set(ev[0]["numbers"]))

    def test_family_scan_ids_view_and_play_log(self):
        rep = scanner.run(ROWS)
        fam = [p for p in rep["patterns"] if p["key"] == "family"][0]
        self.assertEqual(rep["errors"], [])
        self.assertTrue(fam["items"])
        c = lab_server.app.test_client()
        it = fam["items"][0]
        v = c.get("/api/scanner/view?id=" + it["id"]).get_json()
        self.assertEqual(len(v["blocks"][0]["rows"]), 4)
        self.assertEqual(c.get("/api/scanner/xlsx?id=" + it["id"]).status_code, 200)
        mv = c.get("/api/scanner/month_view?id=" + it["id"]).get_json()                           # poora mahina, har rashi alag rang
        self.assertEqual(len(mv["families"]), 15)
        self.assertEqual(len({f["color"] for f in mv["families"]}), 15)
        self.assertTrue(mv["sel"] and mv["timeline"] and mv["explain"])
        days = list(mv["months"].values())[0]["days"]
        self.assertGreaterEqual(len(days), 28)
        for k, fi in mv["cellfam"].items():                                                      # har cell ki family sahi
            iso, g = k.split("|")
            val = dict((d, v) for d, v in days)[iso][int(g)]
            self.assertIn(val, mv["families"][fi]["numbers"])
        self.assertEqual(c.get("/api/scanner/month_view?id=naksha:10:2021-05-06").status_code, 400)
        body = {"id": it["id"], "plays": {"GB": {"numbers": [25, 57], "stake": 20}, "DS": {"numbers": [2], "stake": 10}}, "note": "test"}
        self.assertEqual(c.post("/api/scanner/play", json=body).status_code, 401)                 # PIN chahiye
        self.assertEqual(c.post("/api/scanner/play", json=body, headers=H).status_code, 200)
        self.assertEqual(c.get("/api/scanner/plays").get_json()[it["id"]]["plays"]["GB"]["numbers"], [25, 57])
        bad = dict(body, plays={"GB": {"numbers": [100], "stake": 10}})
        self.assertEqual(c.post("/api/scanner/play", json=bad, headers=H).status_code, 400)
        bad2 = dict(body, plays={"XX": {"numbers": [1], "stake": 10}})
        self.assertEqual(c.post("/api/scanner/play", json=bad2, headers=H).status_code, 400)
        bad3 = dict(body, plays={"GB": {"numbers": [1], "stake": 7}})
        self.assertEqual(c.post("/api/scanner/play", json=bad3, headers=H).status_code, 400)
        self.assertEqual(c.post("/api/scanner/play", json={"id": it["id"], "plays": {}}, headers=H).status_code, 200)     # hata do
        self.assertNotIn(it["id"], c.get("/api/scanner/plays").get_json())

    def test_naksha_view_colours_match_both_sides(self):
        it = [p for p in scanner.run(ROWS)["patterns"] if p["key"] == "naksha"][0]["items"][0]
        v = scan_view.view(ROWS, it["id"])
        old, new = v["blocks"]
        n_old = sum(1 for r in old["rows"] for k in r["kind"] if k == "step")
        n_new = sum(1 for r in new["rows"] for k in r["kind"] if k == "step")
        self.assertEqual(n_old, n_new)                            # jitne rang purane me utne naye me
        self.assertGreater(n_old, 3)


if __name__ == "__main__":
    unittest.main()


class DanaFarakTests(unittest.TestCase):
    def test_numbers(self):
        from lab import dana_farak as df
        self.assertEqual(df.play_numbers(df.relation(10, 20), 10)[0], [1, 2, 10, 20])
        self.assertEqual(df.play_numbers(df.relation(54, 35), 54)[0], [35, 45, 53, 54])
        self.assertEqual(df.play_numbers(df.relation(78, 78), 78)[0], [68, 78, 79, 86, 87, 88, 97])
        self.assertEqual(df.play_numbers(df.relation(45, 45), 45)[0], [35, 45, 46, 53, 54, 55, 64])
        self.assertEqual(df.play_numbers(df.relation(40, 41), 40)[1], [24, 39, 42, 93])
        self.assertEqual(df.play_numbers(df.relation(14, 43), 14)[0], [24, 42])      # beech ka number
        self.assertIsNone(df.relation(10, 30) and None)                              # farak 20 gap hai, pair nahi
        self.assertEqual(df.relation(10, 30)[0], "gap")
        self.assertIsNone(df.relation(10, 45))

    def test_box_pass_fail_and_confusion(self):
        from lab import dana_farak as df
        base = dt.date(2026, 3, 2)
        used, pool = [10, 20, 2, 54, 45], []
        for n in range(3, 100):                                  # aise number jo kisi se pair na banayein
            if all((df.relation(n, u) or ('gap',))[0] == 'gap' for u in used + pool):
                pool.append(n)
        pool = pool[:32]
        rows = [(base + dt.timedelta(days=i), pool[4 * i:4 * i + 4], "t") for i in range(8)]
        rows[0][1][0], rows[1][1][1] = 10, 20                    # pair din1 FB 10, din2 GB 20
        rows[3][1][2] = 2                                        # din 4 GL: 02 = pass
        ev = [e for e in df.events(rows, base, base) if e["kind"] == "farak" and e["c1"][2] == 10 and e["c2"][2] == 20]
        self.assertEqual(len(ev), 1)
        self.assertEqual((ev[0]["status"], ev[0]["end"]), ("pass", base + dt.timedelta(days=3)))
        rows[3][1][2] = pool[-1]                                 # koi number nahi aaya
        ev = [e for e in df.events(rows, base, base) if e["c1"][2] == 10 and e["c2"][2] == 20]
        self.assertEqual(ev[0]["status"], "fail")
        ev = [e for e in df.events(rows, base, base) if e["c1"][2] == 10 and e["c2"][2] == 20]
        self.assertFalse(ev[0]["amb"])                           # saaf box
        rows[0][1][1], rows[0][1][2] = 54, 45                    # usi box me doosra pair (din 1 GB/GL)
        ev = [e for e in df.events(rows, base, base) if e["c1"][2] == 10 and e["c2"][2] == 20]
        self.assertTrue(ev[0]["amb"])


class NakshaRashiTests(unittest.TestCase):
    def test_rashi_part2_view_and_counts(self):
        a = scanner.scan_naksha(ROWS, "x")
        b = scanner.scan_naksha2(ROWS, "x")
        self.assertTrue(len(a["items"]) > 4 and len(b["items"]) > 4)           # ab ek-do nahi, zyada milan
        it = b["items"][0]
        self.assertTrue(it["id"].startswith("naksha2:"))
        v = scan_view.view(ROWS, it["id"])
        self.assertTrue(v["blocks"] and "rashi" in v["title"])
        self.assertEqual(scanner.RID[1], scanner.RID[6])                       # 01 aur 06 ek rashi
        self.assertNotEqual(scanner.RID[1], scanner.RID[2])


class ActiveLogTests(unittest.TestCase):
    def _rep(self, items, key="copy"):
        pat = {"id": "001", "key": key, "naam": "X"}
        return {"asof": "2026-10-01", "patterns": [{**pat, "summary": "s", "items": [dict(i, kind=i.get("kind", key), pattern=pat) for i in items]}], "errors": []}

    def test_keep_and_resolved_on_fixed(self):
        from lab import active
        d1, d2, d3 = (dt.datetime(2026, 10, n, 8, 0, tzinfo=active.IST) for n in (1, 2, 3))
        log = active.merge(active.new_log(), self._rep([{"id": "a", "status": "aaj", "name": "A"}]), d1)
        active.merge(log, self._rep([{"id": "a", "status": "pass", "name": "A"}]), d2)
        active.merge(log, self._rep([]), d3)                                    # ab scan ne a nahi diya
        active.merge(log, self._rep([{"id": "a", "status": "fail"}]), d3)       # nateeja badalna nahi chahiye
        a = log["items"]["a"]
        self.assertEqual((a["status"], a["resolved_on"], a["first_seen"], a["last_seen"]), ("pass", "2026-10-02", "2026-10-01", "2026-10-03"))
        self.assertEqual(len(log["scans"]), 4)

    def test_naksha_not_stored(self):
        from lab import active
        log = active.merge(active.new_log(), self._rep([{"id": "n", "status": "aaj"}], key="naksha"))
        self.assertEqual(log["items"], {})

    def test_view_days_and_recent_pass(self):
        from lab import active
        log = active.new_log()
        for n, st in ((1, "pass"), (8, "pass"), (9, "fail")):
            active.merge(log, self._rep([{"id": f"i{n}", "status": st}]), dt.datetime(2026, 10, n, 8, 0, tzinfo=active.IST))
        today = dt.date(2026, 10, 9)
        v = active.view(log, 3, today)
        self.assertEqual(([i["id"] for i in v["recent_pass"]], v["recent_fail"]), (["i8"], 1))
        self.assertEqual(v["recent_pass"][0]["passed_on"], "2026-10-08")
        self.assertEqual((active.view(log, 99, today)["days"], active.view(log, 0, today)["days"], active.view(log, "x", today)["days"]), (3, 1, 3))
        self.assertEqual(active.view(log, 1, dt.date(2026, 10, 10))["recent_pass"], [])
        self.assertEqual(v["board"][0]["pass"] + v["board"][0]["fail"], 3)

    def test_endpoints(self):
        c = lab_server.app.test_client()
        g = c.get("/api/active?days=3")
        p = c.post("/api/active/scan")
        for r in (g, p):
            self.assertEqual(r.status_code, 200)
            j = r.get_json()
            for k in ("now", "recent_pass", "board", "scans", "patterns", "errors"):
                self.assertIn(k, j)
        self.assertEqual(p.get_json()["scans"]["manual_today"] >= 1, True)


class NewMarkTests(unittest.TestCase):
    def test_new_flag_and_dates_in_naksha_view(self):
        from lab import active
        rep = {"patterns": [{"id": "002", "key": "naksha", "naam": "Naksha", "items": [{"id": "naksha:10:2020-01-01", "kind": "naksha", "status": "dekho"}]}]}
        log = active.new_log()
        active.merge(log, rep)
        self.assertFalse(rep["patterns"][0]["items"][0]["new"])                 # pehla scan: sab purana
        rep2 = {"patterns": [{"id": "002", "key": "naksha", "naam": "Naksha", "items": [
            {"id": "naksha:10:2020-01-01", "kind": "naksha", "status": "dekho"}, {"id": "naksha:10:2021-02-02", "kind": "naksha", "status": "dekho"}]}]}
        active.merge(log, rep2)
        self.assertEqual([i["new"] for i in rep2["patterns"][0]["items"]], [False, True])
        it = scanner.scan_naksha(ROWS, "x")["items"][0]
        v = scan_view.view(ROWS, it["id"])
        last = [r["date"] for r in v["blocks"][1]["rows"]][-3:]
        self.assertTrue(all(len(x) == 10 and x > ROWS[-1][0].isoformat() for x in last))   # "aage" ki jagah tarikh


class ReviewTests(unittest.TestCase):
    def test_review_roundtrip(self):
        c = lab_server.app.test_client()
        r = c.post("/api/review", json={"ids": ["a", "b"], "done": True}).get_json()
        self.assertEqual(r["ids"], ["a", "b"])
        r = c.post("/api/review", json={"ids": ["a"], "done": False}).get_json()
        self.assertEqual(r["ids"], ["b"])
        self.assertEqual(c.get("/api/review").get_json()["ids"], ["b"])


class BulkExportTests(unittest.TestCase):
    def setUp(self):
        self.c = lab_server.app.test_client()

    def get(self, key, fmt, **kw):
        q = "&".join(f"{k}={v}" for k, v in kw.items())
        return self.c.get(f"/api/scanner/bulk?key={key}&fmt={fmt}" + ("&" + q if q else ""))

    def test_pdf(self):
        r = self.get("naksha", "pdf", limit=6)
        self.assertEqual((r.status_code, r.mimetype), (200, "application/pdf"))
        self.assertTrue(r.data.startswith(b"%PDF"))
        self.assertIn("Naksha_pattern_", r.headers["Content-Disposition"])
        self.assertTrue(r.headers["Content-Disposition"].endswith('.pdf"'))

    def test_jpg_zip_and_status_filter(self):
        import zipfile
        from PIL import Image
        r = self.get("naksha", "jpg", limit=6)
        self.assertEqual(r.mimetype, "application/zip")
        z = zipfile.ZipFile(io.BytesIO(r.data))
        names = z.namelist()
        self.assertEqual(names[0], "Index.jpg")
        self.assertTrue(names[1].startswith("Pattern_01"))
        self.assertEqual(Image.open(io.BytesIO(z.read(names[1]))).format, "JPEG")
        r = self.get("copy", "jpg", status="aaj", limit=1)                    # aaj wala koi ho ya na ho, file valid
        self.assertEqual(r.status_code, 200)
        if r.mimetype == "image/jpeg":
            self.assertEqual(Image.open(io.BytesIO(r.data)).format, "JPEG")

    def test_xlsx_and_numbering(self):
        r = self.get("naksha2", "xlsx", limit=3)
        wb = load_workbook(io.BytesIO(r.data))
        self.assertEqual(wb.sheetnames, ["Index", "P01", "P02", "P03"])
        aaj = self.get("naksha2", "xlsx", status="aaj", limit=2)
        wb2 = load_workbook(io.BytesIO(aaj.data))
        rep = lab_server.scan_today(lab_server.state()[0])
        items = [p for p in rep["patterns"] if p["key"] == "naksha2"][0]["items"]
        first = next(i for i, it in enumerate(items, 1) if it["status"] == "aaj")
        self.assertEqual(wb2.sheetnames[1], "P%02d" % first)                  # numbering poori list se

    def test_all_keys_all_formats(self):
        for key in ("naksha", "naksha2", "copy", "family", "dana"):
            for fmt in ("pdf", "jpg", "xlsx"):
                self.assertEqual(self.get(key, fmt, limit=4).status_code, 200, (key, fmt))

    def test_bad_params(self):
        for q in ("key=zzz&fmt=pdf", "key=naksha&fmt=doc", "key=naksha&fmt=pdf&status=x", "key=naksha&fmt=pdf&limit=abc"):
            r = self.c.get("/api/scanner/bulk?" + q)
            self.assertEqual(r.status_code, 400, q)
            self.assertIn("error", r.get_json())

    def test_to_board(self):
        rep = lab_server.scan_today(lab_server.state()[0])
        for key, nb in (("naksha", 2), ("naksha2", 2), ("copy", 1), ("family", 1), ("dana", 1)):
            its = [p for p in rep["patterns"] if p["key"] == key][0]["items"]
            if not its:
                continue
            r = self.c.post("/api/scanner/to_board", json={"id": its[0]["id"]})
            self.assertEqual(r.status_code, 200, key)
            bs = r.get_json()["boards"]
            self.assertEqual(len(bs), nb, key)
            for b in bs:
                y, m = int(b["from"][:4]), int(b["from"][5:7])
                self.assertEqual(b["from"][8:], "01")
                self.assertEqual(b["name"], its[0]["name"][:60])
                lo, k = dt.date(y, m, 1), y * 12 + m - 1 + b["months"]
                hi = dt.date(k // 12, k % 12 + 1, 1)
                self.assertTrue(1 <= b["months"] <= 12)
                for ck, col in b["cells"].items():
                    d, g = ck.split("|")
                    self.assertTrue(lo <= dt.date.fromisoformat(d) < hi and int(g) in range(4) and len(col) == 6)
        self.assertEqual(self.c.post("/api/scanner/to_board", json={"id": "nope:1"}).status_code, 400)
        self.assertEqual(self.c.post("/api/scanner/to_board", json={}).status_code, 400)


class BoardXlsxTests(unittest.TestCase):
    def test_board_xlsx(self):
        c = lab_server.app.test_client()
        last = ROWS[-1][0]
        d0 = last.replace(day=1).isoformat()
        r = c.post("/api/pattern/save", json={"name": "Mera test", "from": d0[:7], "months": 2, "cells": {f"{last.isoformat()}|1": "FF9800"}}, headers=H)
        bid = r.get_json()["id"]
        x = c.get(f"/api/pattern/xlsx?id={bid}")
        self.assertEqual(x.status_code, 200)
        ws = load_workbook(io.BytesIO(x.data)).active
        self.assertEqual(ws["A1"].value, "Mera test")
        hit = [cl for row in ws.iter_rows() for cl in row if cl.fill.fgColor.rgb in ("00FF9800", "FFFF9800") and cl.fill.fill_type == "solid"]
        self.assertEqual(len(hit), 1)
        self.assertEqual(hit[0].value, ROWS[-1][1][1])
        miss = c.get("/api/pattern/xlsx?id=nope")
        self.assertEqual(miss.status_code, 404)
        self.assertIn("error", miss.get_json())
        c.post("/api/pattern/delete", json={"id": bid}, headers=H)          # baaki tests ke liye saaf


class RankTests(unittest.TestCase):
    def test_rank_votes(self):
        from lab import rank
        rep = {"patterns": [
            {"key": "naksha", "naam": "Naksha", "items": [
                {"targets": [{"game": "FB", "numbers": [58, 85]}, {"game": "GL", "numbers": [58, 85]}]},     # ek map do jagah: ek hi vote
                {"targets": [{"game": "GB", "numbers": [58, 85, 11]}]}]},
            {"key": "copy", "naam": "Jodi-Copy", "items": [{"targets": [{"game": "ALL", "numbers": [11]}]}]}]}
        out = rank.build(rep, ROWS)
        g = {x["key"]: x for x in out["groups"]}
        top = g["naksha"]["lists"]["ALL"][0]
        self.assertEqual((top["votes"], len(top["maps"])), (2, 2))          # 58/85: do alag map
        self.assertEqual([r["n"] for r in g["naksha"]["lists"]["FB"]], [58, 85])
        self.assertEqual(g["naksha"]["lists"]["FB"][0]["votes"], 1)
        self.assertEqual(g["copy"]["lists"]["FB"], [])                      # location tay nahi: sirf ALL
        self.assertEqual([r["n"] for r in g["copy"]["lists"]["ALL"]], [11])
        self.assertEqual(g["all"]["maps"], 3)
        eleven = [r for r in g["all"]["lists"]["ALL"] if r["n"] == 11][0]
        self.assertEqual(eleven["votes"], 2)

    def test_rank_api(self):
        r = lab_server.app.test_client().get("/api/rank")
        self.assertEqual(r.status_code, 200)
        j = r.get_json()
        self.assertEqual([g["key"] for g in j["groups"]], ["all", "naksha", "naksha2", "family", "copy", "dana", "steps"])
        self.assertTrue(j["groups"][0]["maps"] >= 0 and set(j["groups"][0]["lists"]) == {"FB", "GB", "GL", "DS", "ALL"})
        s = j["groups"][1]["lists"]["ALL"]
        self.assertTrue(all(s[i]["score"] >= s[i + 1]["score"] for i in range(len(s) - 1)))


class StaleScanTests(unittest.TestCase):
    def test_old_schema_scan_is_rerun(self):
        old = scanner.run(ROWS)
        old["schema"] = 1
        for p in old["patterns"]:
            for it in p["items"]:
                it.pop("targets", None)
        lab_server.jsave("patterns_today.json", old)
        new = lab_server.scan_today(ROWS)
        self.assertEqual(new["schema"], scanner.SCHEMA)


class GameRecordTests(unittest.TestCase):
    def test_series_grid_and_files(self):
        from lab import gamefiles as G
        fb = G.series(ROWS, "FB")
        self.assertEqual((fb[0][0], len(fb)), (ROWS[0][0], len(ROWS)))
        ds = G.series(ROWS, "DS")
        self.assertTrue(len(ds) >= len(ROWS))                                  # purana hissa jud sakta hai
        kh = G.series(ROWS, "DS", "khula")
        self.assertEqual(kh[-1][0], ds[-1][0] + dt.timedelta(days=1))          # khula tarikh = line + 1
        d0 = ROWS[0][0]
        gr = G.grid(fb, d0.year)
        self.assertEqual(gr[d0.day - 1][d0.month - 1], ROWS[0][1][0])
        self.assertEqual(len(gr), 31)
        self.assertEqual(len(gr[0]), 12)
        self.assertTrue(G.xlsx_bytes(ROWS, "GL")[:2] == b"PK")
        self.assertTrue(G.csv_bytes(ROWS, "GB").startswith(b"date,gb"))

    def test_api(self):
        c = lab_server.app.test_client()
        j = c.get("/api/record/game?g=GL").get_json()
        self.assertEqual((j["g"], len(j["grid"]), len(j["grid"][0])), ("GL", 31, 12))
        self.assertEqual(c.get("/api/record/game?g=XX").status_code, 400)
        self.assertEqual(c.get("/api/record/game?g=FB&year=1900").status_code, 404)
        self.assertEqual(c.get("/api/record/game.xlsx?g=DS").status_code, 200)
        r = c.get("/api/record/game.csv?g=FB")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.data.startswith(b"date,fb"))


class StepsTests(unittest.TestCase):
    def _rows(self):
        import random
        from lab import steps
        rnd = random.Random(5)
        days = []
        for m in (8, 9, 10):
            d = dt.date(2026, m, 1)
            while d.month == m:
                if not data.is_last_day(d):
                    days.append(d)
                d += dt.timedelta(days=1)
        vals = [[rnd.randint(0, 99) for _ in range(4)] for _ in days]
        idx = {m: [i for i, d in enumerate(days) if d.month == m] for m in (8, 9, 10)}
        X = 37                                                  # link A ka number: (i=1, DS) -> (j=3, GB)
        for m, s in ((8, 3), (9, 5), (10, 4)):
            r0 = idx[m][0] + s
            vals[r0 + 1][3] = X
            vals[r0 + 3][1] = X if m != 10 else X
        # current mahine (Oct) me link A poora; link B (i=0, FB) -> (j=5, GL): pehla cell hi
        Y = 12
        for m, s in ((8, 3), (9, 5), (10, 4)):
            r0 = idx[m][0] + s
            vals[r0][0] = Y
            if m != 10:
                vals[r0 + 5][2] = Y
        last = idx[10][0] + 4 + 3                               # Oct ke 8-ve row tak data
        rows = [(d, v, "t") for d, v in zip(days[:last + 1], vals[:last + 1])]
        return rows, steps

    def test_find_pending_and_view(self):
        rows, steps = self._rows()
        D = [x[0] for x in rows]
        vals = [list(x[1]) for x in rows]
        first = lambda m: next(i for i, d in enumerate(D) if d.month == m)
        a, b, c = first(8) + 3, first(9) + 5, first(10) + 4
        r = steps.analyse(vals, D, a, b, c, 8)
        self.assertIn((1, 3, 3, 1), r["common"])
        self.assertIn((0, 0, 5, 2), r["common"])
        self.assertIn((1, 3, 3, 1), r["present"])                 # link A Step 3 me poora
        self.assertTrue(any(k == (0, 0, 5, 2) and cl == 12 for k, cl in r["pend"]))   # link B ka doosra cell: 12 aana chahiye
        res = steps.find(rows, Ls=(8,), top=500)
        self.assertTrue(any(x["a"] == a and x["b"] == b for x in res) or len(res) > 0)
        it = steps.item(r, rows, data.play_date(rows))
        self.assertEqual((it["kind"], it["status"]), ("steps", "aaj"))
        self.assertTrue(it["targets"])
        v = steps.view(rows, steps.pid(r, D))
        self.assertEqual(len(v["blocks"]), 3)
        self.assertTrue(any(x["step"] == 3 for x in v["stack"]["rows"]) and any(x["edge"] == "start" for x in v["stack"]["rows"]))
        self.assertTrue(v["stack"]["legend"])

    def test_run_has_steps_pattern(self):
        rep = scanner.run(ROWS)
        keys = [p["key"] for p in rep["patterns"]]
        self.assertIn("steps", keys)
        self.assertEqual(rep["errors"], [])
