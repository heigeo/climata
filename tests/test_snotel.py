from .base import ClimataTestCase
from climata.snotel import (
    StationIO, StationDailyDataIO, RegionDailyDataIO, ElementIO
)


class SnotelTestCase(ClimataTestCase):
    def test_station(self):
        data = StationIO(
            basin='18010201',
        )
        self.assertGreater(len(data), 0)
        item = data[0]
        self.assertHasFields(
            item, ("name", "stationtriplet", "latitude", "longitude")
        )

    def test_station_daily_data(self):
        data = StationDailyDataIO(
            station='395:OR:SNTL',
            start_date='2014-07-01',
            end_date='2014-07-01',
        )
        item = data[0]
        self.assertHasFields(
            item, (
                "stationtriplet", "elementcd", "element_name", "storedunitcd"
            )
        )
        self.assertHasFields(
            item.data[0], ("value", "flag", "date")
        )

    def test_region_daily_data(self):
        data = RegionDailyDataIO(
            basin='18010201',
            start_date='2014-07-01',
            end_date='2014-07-01',
        )
        for site in data:
            self.assertHasFields(
                site, ("name", "stationtriplet", "latitude", "longitude")
            )
            if len(site.data) > 0:
                self.assertHasFields(
                    site.data[0], ("elementcd", "value", "flag", "date")
                )

    def test_element(self):
        data = ElementIO()
        item = data[0]
        self.assertHasFields(item, ("elementcd", "name", "storedunitcd"))
