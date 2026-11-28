"""Roz ka card (lab/card.py, patterns/017_roz_ka_card). Kagaz ka puzzle: sirf jaanch ki card sahi tarikh aur sahi niyam se bane."""
import copy
import datetime as dt
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from PIL import Image  # noqa: E402

from lab import card, data, update  # noqa: E402

D28 = "2026-11-28"


def _load(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as f:
        return json.load(f)


class CardRuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ps = _load("pockets.json")
        cls.rows = [r for r in data.load(os.path.join(ROOT, "data", "results.csv")) if r[0] <= dt.date(2026, 11, 27)]
        cls.rep = {"asof": "2026-11-27", "play_date": D28, "time": "2026-11-28T07:15:40+05:30", "errors": []}

    def test_28_nov_haath_wale_card_jaisa(self):
        """28 Nov ki lock tokri se wahi 12 jodi jo haath se bane card me: solid 58 79 85 97, spot baaki 8."""
        n = card.numbers(self.ps["days"][D28]["lists"])
        self.assertEqual(n["solid"], [58, 79, 85, 97])
        self.assertEqual(n["spot"], [10, 15, 24, 42, 51, 52, 59, 74])
        self.assertEqual(len(n["teeno"]), 12)

    def test_niyam_chhote_data_par(self):
        lists = {"top30": [1, 2, 3, 4, 5], "naksha": [1, 2], "naksha_sab": [3, 9], "dost": [1, 3, 4, 9], "baar": [3, 7]}
        self.assertEqual(card.numbers(lists), {"solid": [3], "spot": [1], "teeno": [1, 3]})
        self.assertEqual(card.numbers({}), {"solid": [], "spot": [], "teeno": []})

    def test_ready_sirf_ds_ke_baad_aur_taaza_scan_par(self):
        ok, key, _ = card.ready(self.rows, self.rep, self.ps, today=dt.date(2026, 11, 28))
        self.assertTrue(ok)
        self.assertEqual(key, D28)
        ok, _, why = card.ready(self.rows, self.rep, self.ps, today=dt.date(2026, 11, 29))     # 29 ki subah DS nahi aaya: kal ke data par nahi
        self.assertFalse(ok)
        self.assertIn("DS", why)
        stale = dict(self.rep, asof="2026-11-26", play_date="2026-11-27")
        self.assertFalse(card.ready(self.rows, stale, self.ps, today=dt.date(2026, 11, 28))[0])
        self.assertFalse(card.ready(self.rows, None, self.ps, today=dt.date(2026, 11, 28))[0])
        self.assertFalse(card.ready(self.rows, dict(self.rep, errors=[{"pattern": "x", "error": "y"}]), self.ps, today=dt.date(2026, 11, 28))[0])
        self.assertFalse(card.ready(self.rows, self.rep, {"days": {}}, today=dt.date(2026, 11, 28))[0])
        late = copy.deepcopy(self.ps)
        late["days"][D28]["late"] = True
        self.assertFalse(card.ready(self.rows, self.rep, late, today=dt.date(2026, 11, 28))[0])

    def test_mahine_ki_chhuti(self):
        """29 Nov ki line (DS 30 ki subah) ke baad agla din 1 Dec (30 chhuti): card 1 Dec ka, 30 ko bhi ban sakta hai."""
        rows = self.rows + [(dt.date(2026, 11, 28), [1, 2, 3, 4], "t"), (dt.date(2026, 11, 29), [5, 6, 7, 8], "t")]
        rep = {"asof": "2026-11-29", "play_date": "2026-12-01", "errors": []}
        ps = {"days": {"2026-12-01": copy.deepcopy(self.ps["days"][D28])}}
        self.assertEqual(card.ready(rows, rep, ps, today=dt.date(2026, 11, 30))[:2], (True, "2026-12-01"))

    def test_make_ek_baar_lock(self):
        cs = card.new_state()
        made, key, _ = card.make(cs, self.rows, self.rep, self.ps, today=dt.date(2026, 11, 28))
        self.assertTrue(made)
        self.assertEqual(cs["days"][key]["solid"], [58, 79, 85, 97])
        changed = copy.deepcopy(self.ps)
        changed["days"][D28]["lists"]["baar"] = []
        made2, _, why = card.make(cs, self.rows, self.rep, changed, today=dt.date(2026, 11, 28))
        self.assertFalse(made2)
        self.assertIn("lock", why)
        self.assertEqual(cs["days"][key]["solid"], [58, 79, 85, 97])
        self.assertFalse(card.make(card.new_state(), self.rows, self.rep, self.ps, today=dt.date(2026, 11, 29))[0])

    def test_render_jpg(self):
        im = Image.open(io.BytesIO(card.render(D28, [58, 79, 85, 97], [10, 15, 24, 42, 51, 52, 59, 74])))
        self.assertEqual((im.format, im.size), ("JPEG", (1080, 1350)))
        self.assertEqual(im.convert("RGB").getpixel((540, 260)), im.convert("RGB").getpixel((100, 260)))     # hara dabba
        big = Image.open(io.BytesIO(card.render(D28, list(range(9)), list(range(10, 23)))))
        self.assertGreater(big.size[1], 1350)
        self.assertEqual(Image.open(io.BytesIO(card.render(D28, [], []))).size[0], 1080)

    def test_view(self):
        cs = card.new_state()
        card.make(cs, self.rows, self.rep, self.ps, today=dt.date(2026, 11, 28))
        v = card.view(cs, self.rows, self.rep, self.ps, today=dt.date(2026, 11, 28))
        self.assertTrue(v["bana"])
        self.assertEqual(v["pichle"][0]["date"], D28)
        self.assertIn("paper test", v["dhyan"])


class UpdateHookTests(unittest.TestCase):
    def test_update_run_card_banata_hai(self):
        tmp = tempfile.mkdtemp()
        try:
            for f in os.listdir(os.path.join(ROOT, "data")):
                if f.endswith((".csv", ".json")) and f not in ("partial_results.json", "manual_results.json", "cards.json"):
                    shutil.copy(os.path.join(ROOT, "data", f), tmp)
            rows = data.load(os.path.join(tmp, "results.csv"))
            play = data.play_date(rows)
            r = update.run(fetch=False, today=play, data_dir=tmp, auto_bets=False)
            self.assertTrue(r["card"]["bana"], r["card"])
            with open(os.path.join(tmp, "cards.json"), encoding="utf-8") as f:
                cs = json.load(f)
            self.assertIn(play.isoformat(), cs["days"])
            self.assertTrue(os.path.exists(os.path.join(tmp, "cards", play.isoformat() + ".jpg")))
            r2 = update.run(fetch=False, today=play, data_dir=tmp, auto_bets=False)
            self.assertFalse(r2["card"]["bana"])                     # dobara nahi
            os.remove(os.path.join(tmp, "cards.json"))
            r3 = update.run(fetch=False, today=play + dt.timedelta(days=1), data_dir=tmp, auto_bets=False)
            self.assertFalse(r3["card"]["bana"])                     # agle din, naya DS nahi aaya: purane par nahi
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
