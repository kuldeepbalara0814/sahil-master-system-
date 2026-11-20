import datetime as dt
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lab import data, monitor, paper, picks

D = dt.date


def rows3():
    return [(D(2026, 1, 1), [10, 11, 12, 13], ""), (D(2026, 1, 2), [20, 21, 22, 23], ""), (D(2026, 1, 3), [30, 31, 32, 33], "")]


class PaperTests(unittest.TestCase):
    def test_stake_rules(self):
        L = paper.new_ledger()
        for bad in (0, 3, 7, 12, 4.5, -5):
            with self.assertRaises(ValueError):
                paper.place(L, "manual", "2026-01-04", "FD", 5, bad)
        self.assertTrue(paper.place(L, "manual", "2026-01-04", "FD", 5, 5))
        self.assertFalse(paper.place(L, "manual", "2026-01-04", "FD", 5, 5))     # duplicate

    def test_settle_win_and_loss(self):
        L = paper.new_ledger()
        paper.place(L, "manual", "2026-01-03", "FD", 30, 5)    # jeet (FD=30)
        paper.place(L, "manual", "2026-01-03", "GB", 99, 10)   # haar
        paper.place(L, "manual", "2026-01-09", "FD", 1, 5)     # abhi result nahi
        self.assertEqual(paper.settle(L, rows3()), 2)
        s = paper.summary(L)
        self.assertEqual((s["bets"], s["wins"], s["pending"]), (2, 1, 1))
        self.assertEqual(s["net"], 5 * 94 - 10)       # 95 guna -> net 94 x stake

    def test_payout_drops_to_90_with_40_numbers(self):
        L = paper.new_ledger()
        for n in range(40):
            paper.place(L, "manual", "2026-01-03", "FD", n, 5)
        paper.place(L, "manual", "2026-01-03", "FD", 30, 5)            # 30 pehle se hai -> dobara nahi
        paper.settle(L, rows3())
        win = [b for b in L["bets"] if b["status"] == "win"][0]
        self.assertEqual(win["net"], 5 * 89)                           # 40 number -> 90 guna

    def test_auto_place_counts_and_play_date(self):
        rows = [r for r in data.load() if r[0] <= D(2026, 11, 19)]
        L = paper.new_ledger()
        added = paper.auto_place(L, rows, 5)
        self.assertEqual(added, 3 + 40 + 10)                           # single 3 + list10s 40 + list10 FD 10 (dobara 0)
        self.assertEqual({b["date"] for b in L["bets"]}, {"2026-11-20"})
        self.assertEqual(paper.auto_place(L, rows, 5), 0)              # dobara chalao to kuch nahi jodta

    def test_single_jodi_is_yesterdays_gb(self):
        rows = [r for r in data.load() if r[0] <= D(2026, 11, 19)]
        s = picks.single_jodi(rows)
        self.assertEqual(s["number"], rows[-1][1][1])
        self.assertEqual(s["games"], ["FD", "GL", "DS"])

    def test_list_size_and_tiers(self):
        rows = [r for r in data.load() if r[0] <= D(2026, 11, 19)]
        lst = picks.top_list(rows[-12:], [], 0, 10)
        self.assertEqual(len(lst), 10)
        self.assertEqual(len({n for n, _ in lst}), 10)
        last_same = rows[-1][1][0]
        self.assertNotIn(last_same, [n for n, _ in lst])               # kal ka same game ka number list me nahi

    def test_monitor_status(self):
        self.assertEqual(monitor.status(0.02, 100), "kam data")
        self.assertEqual(monitor.status(0.0135, 1000), "hara")
        self.assertEqual(monitor.status(0.0105, 1000), "peela")
        self.assertEqual(monitor.status(0.009, 1000), "laal")


if __name__ == "__main__":
    unittest.main()
