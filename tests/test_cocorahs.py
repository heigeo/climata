from .base import ClimataTestCase
from climata.cocorahs import CocorahsIO


class CocorahsTestCase(ClimataTestCase):
    module = "cocorahs"

    def test_cocorahs(self):
        data = CocorahsIO(
            state='MN',
            county='HN',
            start_date='2014-07-01',
            end_date='2014-07-01',
        )
        self.assertGreater(len(data), 0)
        item = data[0]
        fields = (
            "observationdate",
            "latitude",
            "longitude",
            "stationnumber",
            "totalprecipamt",
        )
        self.assertHasFields(item, fields)
