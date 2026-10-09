import unittest

from flighttracker.db import DB
from flighttracker.tracker import check_watch


class Seq:
    def __init__(self, prices):
        self.prices = iter(prices)

    def get_cheapest(self, watch):
        return next(self.prices)


class TrackerTest(unittest.TestCase):
    def setUp(self):
        self.db = DB(":memory:")
        self.db.add_watch("ORD", "LHR", "2027-01-10")
        self.watch = self.db.watches()[0]
        self.alerts = []

    def run_prices(self, prices, **kw):
        prov = Seq(prices)
        return [check_watch(self.db, prov, self.watch, [lambda t, m: self.alerts.append(t)], **kw)[1]
                for _ in prices]

    def test_alerts_only_on_new_low_after_warmup(self):
        flags = self.run_prices([500, 450, 480, 470, 400, 410, 400, 399])
        # 450 is a new low but within warm-up (<3 prior checks); 400 and 399 alert; 400 tie does not
        self.assertEqual(flags, [False, False, False, False, True, False, False, True])
        self.assertEqual(len(self.alerts), 2)

    def test_no_offers(self):
        self.assertEqual(check_watch(self.db, Seq([None]), self.watch, [])[0], None)

    def test_duplicate_watch_ignored(self):
        self.assertIsNone(self.db.add_watch("ord", "lhr", "2027-01-10"))


if __name__ == "__main__":
    unittest.main()
