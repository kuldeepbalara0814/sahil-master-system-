import datetime as dt
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lab import data, fetcher

D = dt.date
FX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def fake_fetch(y, m):
    p = os.path.join(FX, f"chart_{y}-{m:02d}.html")
    if not os.path.exists(p):
        raise fetcher.FetchError("fixture nahi")
    return open(p, encoding="utf-8").read()


class FetcherTests(unittest.TestCase):
    def test_parse_and_ds_shift(self):
        site = fetcher.parse_month(fake_fetch(2026, 11), 2026, 11)
        self.assertEqual(site[D(2026, 11, 1)]["ds"], None)            # 1 tarikh ko DS XX
        self.assertEqual(site[D(2026, 11, 20)]["ds"], 47)             # 20 ko khula DS (19 ki line ka)
        lines = {d: v for d, v, _ in fetcher.build_lines(site)}
        self.assertEqual(lines[D(2026, 11, 19)], [12, 47, 85, 47])    # DS = site ki agli tarikh ka
        self.assertEqual(lines[D(2026, 11, 1)], [77, 63, 82, 64])
        self.assertNotIn(D(2026, 11, 20), lines)                      # aaj ki line abhi poori nahi

    def test_reproduces_stored_data_exactly(self):
        """Purani line se aage ki lines site se banao -> wahi jo file me hain (parser + niyam ki jaanch)."""
        rows = [r for r in data.load() if r[0] <= D(2026, 10, 15)]
        stored = {d: v for d, v, _ in data.load() if D(2026, 10, 15) < d <= D(2026, 11, 19)}   # fixture sirf 19 Nov tak
        new, info = fetcher.new_lines(rows, today=D(2026, 11, 21), fetch=fake_fetch, pause=0)
        self.assertEqual(info["errors"], [])
        got = {d: v for d, v, _ in new}
        self.assertEqual(got, stored)                                 # Oct 16 se Nov 19 tak sab barabar
        merged, added, skipped, conflicts = data.merge_new(rows, new)
        self.assertEqual((len(skipped), len(conflicts)), (0, 0))
        self.assertEqual(data.validate(merged), [])

    def test_missing_month_is_reported_not_crashing(self):
        rows = [r for r in data.load() if r[0] <= D(2026, 10, 15)]
        new, info = fetcher.new_lines(rows, today=D(2026, 12, 3), fetch=fake_fetch, pause=0)   # Dec fixture nahi
        self.assertEqual(len(info["errors"]), 1)
        self.assertGreater(len(new), 0)

    def test_bad_page_raises(self):
        with self.assertRaises(fetcher.FetchError):
            fetcher.parse_month("<html>blocked</html>", 2026, 11)


if __name__ == "__main__":
    unittest.main()


class UpdateTests(unittest.TestCase):
    def test_full_update_in_temp_dir(self):
        import json
        import shutil
        import tempfile
        from lab import update
        tmp = tempfile.mkdtemp()
        try:
            rows = [r for r in data.load() if r[0] <= D(2026, 10, 15)]
            data.save(rows, os.path.join(tmp, "results.csv"))
            r1 = update.run(today=D(2026, 11, 21), data_dir=tmp, fetch_fn=fake_fetch, pause=0, stake=5)
            self.assertEqual(r1["last_date"], "2026-11-19")
            self.assertEqual(r1["problems"], [])
            self.assertEqual(len(r1["added"]), len([r for r in data.load() if D(2026, 10, 15) < r[0] <= D(2026, 11, 19)]))
            self.assertEqual(r1["new_bets"], 3 + 40 + 10)
            r2 = update.run(today=D(2026, 11, 21), data_dir=tmp, fetch_fn=fake_fetch, pause=0, stake=5)   # dobara chalao
            self.assertEqual(r2["added"], [])                       # kuch duplicate nahi
            self.assertEqual(r2["new_bets"], 0)
            self.assertEqual(r2["days"], r1["days"])
            for f in ("results.csv", "paper_ledger.json", "friends_snapshot.json", "drift_log.json", "monitor.json", "fetch_log.json"):
                self.assertTrue(os.path.exists(os.path.join(tmp, f)), f)
            self.assertEqual(json.load(open(os.path.join(tmp, "monitor.json")))["asof"], "2026-11-19")
        finally:
            shutil.rmtree(tmp)
