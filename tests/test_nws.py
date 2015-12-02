from .base import ClimataTestCase
from climata.nws import EnsembleSiteIO, EnsembleForecastIO, HydroForecastIO
from datetime import datetime, date


class NwsTestCase(ClimataTestCase):
    module = "nws"

    def test_hydro_forecast(self):
        data = HydroForecastIO(station="WMSO3")
        self.assertGreater(len(data), 0)
        item = data[0]
        self.assertHasFields(item, ("date", "stage", "flow"))

        self.assertIsInstance(item.date, datetime)
        self.assertGreater(item.stage, 0)
        self.assertGreater(item.flow, 0)

    def test_ensemble_forecast(self):
        data = EnsembleForecastIO(
            basin='klamath',
            start_date='2014-01-01',
        )
        self.assertGreater(len(data), 0)
        item = data[0]
        self.assertHasFields(item, ("site", "parameter", "data"))
        self.assertGreater(len(item.data), 0)

        row = item.data[0]
        self.assertHasFields(row, ("date", "year", "value"))
        self.assertIsInstance(row.date, date)
        self.assertIsInstance(row.year, int)
        self.assertIsInstance(row.value, float)

    def test_ensemble_single(self):
        data = EnsembleForecastIO(
            basin='klamath',
            start_date='2014-01-01',
            station="KLAO3"
        )
        self.assertEqual(len(data), 1)
        item = data[0]
        self.assertEqual(item.site, "KLAO3")
        self.assertGreater(len(item.data), 0)

        row = item.data[0]
        self.assertHasFields(row, ("date", "year", "value"))
        self.assertIsInstance(row.date, date)
        self.assertIsInstance(row.year, int)
        self.assertIsInstance(row.value, float)

    def test_ensemble_date(self):
        data = EnsembleForecastIO(
            basin='klamath',
            start_date='2014-01-01',
            end_date='2014-02-14',
            station="KLAO3"
        )
        self.assertEqual(len(data), 1)
        item = data[0]
        self.assertEqual(item.site, "KLAO3")
        self.assertGreater(len(item.data), 0)
        for row in item.data:
            self.assertLess(row.date.date(), date(2014, 2, 15))

    def test_ensemble_sites(self):
        sites = EnsembleSiteIO()
        self.assertGreater(len(sites), 0)
        site = sites[list(sites.keys())[0]]
        self.assertHasFields(site, ("stationname", "latitude", "longitude"))
