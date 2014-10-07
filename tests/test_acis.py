from .base import ClimataTestCase
from climata.acis import StationMetaIO, StationDataIO


class AcisTestCase(ClimataTestCase):
    module = "acis"

    def test_station_meta(self):
        data = StationMetaIO(
            county='27053',
        )
        self.assertGreater(len(data), 0)
        item = data[0]
        self.assertHasFields(item, ("latitude", "longitude", "sids"))

    def test_station_data(self):
        data = StationDataIO(
            county='27053',
            start_date='2014-07-01',
            end_date='2014-07-01',
            parameter='pcpn',
        )

        self.assertGreater(len(data), 0)
        item = data[0]
        self.assertHasFields(item, ("latitude", "longitude", "data"))

        row = item.data[0]
        self.assertHasFields(row, ("date", "pcpn"))
