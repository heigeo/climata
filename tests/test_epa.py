from .base import ClimataTestCase
from climata.epa import WqxDomainIO


class EpaTestCase(ClimataTestCase):
    module = "epa"

    def test_domain(self):
        data = WqxDomainIO(
            domain='Characteristic',
        )
        self.assertGreater(len(data), 0)
        item = data[0]
        self.assertHasFields(item, (
            "name", "picklist", "samplefractionrequired", "lastchangedate"
        ))
