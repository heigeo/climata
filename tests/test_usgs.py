from .base import ClimataTestCase
from climata.usgs import SiteIO, DailyValueIO, InstantValueIO
from datetime import datetime, date


class UsgsTestCase(ClimataTestCase):
    module = "usgs"

    def test_site(self):
        data = SiteIO(
            county='27053',
        )
        self.assertGreater(len(data), 0)
        item = data[0]
        self.assertHasFields(item, ("station_nm", "dec_lat_va", "dec_long_va"))

    def test_daily_value(self):
        data = DailyValueIO(
            county='27053',
            start_date='2014-07-01',
            end_date='2014-07-01',
        )
        self.assertGreater(len(data), 0)
        item = data[0]
        self.assertHasFields(item, ("latitude", "longitude", "variable_code"))

        for item in data:
            if len(item.data) > 0:
                self.assertHasFields(item.data[0], ('date', 'value'))
                self.assertIsInstance(item.data[0].date, date)

    def test_instant_value(self):
        data = InstantValueIO(
            county='27053',
            start_date='2014-07-01',
            end_date='2014-07-01',
        )
        self.assertGreater(len(data), 0)
        item = data[0]
        self.assertHasFields(item, ("latitude", "longitude", "variable_code"))

        for item in data:
            if len(item.data) > 0:
                self.assertHasFields(item.data[0], ('date', 'value'))
                self.assertIsInstance(item.data[0].date, datetime)
