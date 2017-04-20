from wq.io import BaseIO, TimeSeriesMapper, XmlParser
from climata.base import ZipWebserviceLoader, FilterOpt, DateOpt, ChoiceOpt
from .constants import DOMAINS


class WqxDomainIO(ZipWebserviceLoader, XmlParser, TimeSeriesMapper, BaseIO):
    """
    Load WQX / STORET domain values from EPA web services.

    Usage:

        chars = WqxDomainIO(domain='Characteristic')
        for char in chars:
            print char.picklist, char.name
    """

    # Override Default WebserviceLoader options
    start_date = DateOpt(ignored=True)
    end_date = DateOpt(ignored=True)
    state = FilterOpt(ignored=True)
    basin = FilterOpt(ignored=True)
    county = FilterOpt(ignored=True)
    station = FilterOpt(ignored=True)
    parameter = FilterOpt(ignored=True)

    # Custom Loader options
    domain = ChoiceOpt(choices=DOMAINS, required=True)
    base_url = 'http://cdx.epa.gov/wqx/download/DomainValues/'

    @property
    def url(self):
        domain = self.getvalue('domain')
        if domain == 'CharacteristicWithPickList':
            domain = 'ResultMeasureValuePickList'
        return self.base_url + domain + '.zip'

    @property
    def params(self):
        return {}

    # Custom Parser options
    ns = '{http://www.exchangenetwork.net/schema/wqx/2}'
    root_tag = ns + 'WQXElement'
    item_tag = ns + 'WQXElementRow'

    def parse_item(self, el):
        return {
            e.attrib['colname']: e.attrib['value']
            for e in el.findall(self.ns + 'WQXElementRowColumn')
        }

    # Custom Mapper options
    date_formats = ['iso8601']
    map_floats = False
    scan_fields = True
