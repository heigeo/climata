from .base import ClimataTestCase
from climata.nws import EnsembleSiteIO, EnsembleForecastIO
from datetime import datetime, date
from wq.io.exceptions import NoData


class NwsTestCase(ClimataTestCase):
    module = "nws"

    def test_ensemble_forecast(self):
        data = EnsembleForecastIO(
            basin='klamath',
            start_date='2014-01-01',
        )
        self.assertGreater(len(data), 0)
        item = data[0]
        self.assertHasFields(item, ("site", "stationname", "data"))
        self.assertGreater(len(item.data), 0)

        row = item.data[0]
        self.assertHasFields(row, ("date", "year", "value"))
        self.assertIsInstance(row.date, date)
        self.assertIsInstance(row.year, int)
        self.assertIsInstance(row.value, float)

    def test_ensemble_sites(self):
        sites = EnsembleSiteIO()
        self.assertGreater(len(sites), 0)
        site = sites[sites.keys()[0]]
        self.assertHasFields(site, ("stationname", "latitude", "longitude"))
