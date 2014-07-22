from .base import ClimataTestCase
from climata.hydromet import DailyDataIO, InstantDataIO, AgrimetRecentIO
from datetime import datetime, date
from wq.io.exceptions import NoData


class HydrometTestCase(ClimataTestCase):
    module = "hydromet"

    def test_daily_data(self):
        data = DailyDataIO(
            station='HPD',
            parameter='AF',
            start_date='2014-07-01',
            end_date='2014-07-01',
        )
        self.assertEqual(len(data), 1)
        item = data[0]
        self.assertHasFields(item, ("date", "af"))
        self.assertIsInstance(item.date, date)
        self.assertIsInstance(item.af, float)
        self.assertGreater(item.af, 0)

    def test_instant_data(self):
        data = InstantDataIO(
            station='HPD',
            parameter='AF',
            start_date='2014-07-01',
            end_date='2014-07-01',
        )
        self.assertEqual(len(data), 24 * 4)
        item = data[0]
        self.assertHasFields(item, ("datetime", "af"))
        self.assertIsInstance(item.datetime, datetime)
        self.assertIsInstance(item.af, float)
        self.assertGreater(item.af, 0)

    def test_no_data(self):
        data = AgrimetRecentIO(
            station='HPD',
        )
        self.assertEqual(len(data), 0)

        with self.assertRaises(NoData):
            AgrimetRecentIO(
                station='INVALID_ID',
            )

    def test_agrimet_recent_data(self):
        data = AgrimetRecentIO(
            station='KFLO',
        )
        self.assertGreater(len(data), 0)
        item = data[0]
        self.assertHasFields(item, ('datetime', 'ob', 'wd'))
        self.assertIsInstance(item.datetime, datetime)
        self.assertIsInstance(item.ob, float)
