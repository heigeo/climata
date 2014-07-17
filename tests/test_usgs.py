from .base import ClimataTestCase
from climata.usgs import SiteIO


class UsgsTestCase(ClimataTestCase):
    module = "usgs"

    def test_site(self):
        data = SiteIO(
            county='27053',
        )
        self.assertTrue(len(data) > 0)
        item = data[0]
        self.assertHasFields(item, ("station_nm", "dec_lat_va", "dec_long_va"))
