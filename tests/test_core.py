import datetime as dt
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lab import data, friends

D = dt.date


class DataTests(unittest.TestCase):
    def test_real_file_is_clean(self):
        rows = data.load()
        self.assertEqual(data.validate(rows), [])
        self.assertGreaterEqual(len(rows), 4905)

    def test_merge_never_duplicates_or_overwrites(self):
        rows = [(D(2026, 1, 1), [1, 2, 3, 4], "s"), (D(2026, 1, 2), [5, 6, 7, 8], "s")]
        new = [(D(2026, 1, 2), [5, 6, 7, 8], "site"),       # same -> skip
               (D(2026, 1, 2), [9, 9, 9, 9], "site"),       # conflict
               (D(2026, 1, 3), [5, 6, 7, 8], "site"),       # pichle din ki copy -> skip
               (D(2026, 1, 4), [10, 11, 12, 13], "site"),   # nayi
               (D(2026, 1, 31), [1, 1, 1, 1], "site")]      # mahine ka aakhri din
        merged, added, skipped, conflicts = data.merge_new(rows, new)
        self.assertEqual(added, [D(2026, 1, 4)])
        self.assertEqual(len(merged), 3)
        self.assertEqual(len(conflicts), 1)
        self.assertEqual({r[1] for r in skipped}, {"pichle din ki copy", "mahine ka aakhri din (chhuti)"})
        self.assertEqual(dict((d, v) for d, v, _ in merged)[D(2026, 1, 2)], [5, 6, 7, 8])   # purani line nahi badli

    def test_play_date_skips_holiday(self):
        self.assertEqual(data.play_date([(D(2026, 10, 29), [1, 1, 1, 1], "")]), D(2026, 10, 30))
        self.assertEqual(data.play_date([(D(2026, 10, 30), [1, 1, 1, 1], "")]), D(2026, 11, 1))   # 31 chhuti


class FriendTests(unittest.TestCase):
    def test_known_friend_of_30_matches_excel(self):
        rows = [r for r in data.load() if r[0] <= D(2026, 11, 19)]
        f = friends.Friends(rows).table(30)
        top = f["friends"]["poora"][0]
        self.assertEqual((top["n"], top["together"]), (72, 33))           # Excel me bhi 72, 33 baar
        self.assertEqual([x["tier"] for x in f["friends"]["poora"]], ["green"] * 3 + ["yellow"] * 3 + ["orange"] * 4)

    def test_periods_and_changes(self):
        rows = data.load()
        fr = friends.Friends(rows)
        per = fr.per
        self.assertIsNone(per["poora"])
        last = rows[-1][0]
        self.assertEqual(per["month"], D(last.year, last.month, 1))
        t = fr.table(10)
        for name in ("last3m", "month"):
            for x in t["friends"][name]:
                self.assertIn(x["change"], ("naya", "upar", "neeche", "wahi"))

    def test_drift_detects_top_change(self):
        prev = {"top": {"10": {"poora": [93], "last3m": [93], "month": [93]}}}
        new = {"top": {"10": {"poora": [93], "last3m": [94], "month": [93]}}}
        self.assertEqual(friends.drift(prev, new), [dict(number=10, period="last3m", old=93, new=94)])


if __name__ == "__main__":
    unittest.main()
