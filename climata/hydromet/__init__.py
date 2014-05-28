from wq.io import CsvParser, TimeSeriesMapper, BaseIO
from datetime import datetime, date, timedelta
from collections import OrderedDict
from climata.base import WebserviceLoader, FilterOpt


class HydrometIO(WebserviceLoader, CsvParser, TimeSeriesMapper, BaseIO):
    """
    Base class for retrieving Hydromet data from USBR.
    Use DailyDataIO or InstantDataIO instead, depending on your needs.
    """

    # URL components (see url() below)
    region = 'pn'  # USBR region: pn or gp
    website = 'www.usbr.gov'
    script = None

    # TimeSeriesMapper configuration
    date_formats = ['%m/%d/%Y %H:%M', '%m/%d/%Y']

    # None of the default region filters will work
    state = FilterOpt(ignored=True)
    county = FilterOpt(ignored=True)
    basin = FilterOpt(ignored=True)

    # Instead, specify a four-letter Hydromet station code (one per request)
    station = FilterOpt(required=True)

    # Hydromet parameter codes are also required (multiple allowed)
    parameter = FilterOpt(required=True, multi=True)

    def clean_field_name(self, field):
        field = super(HydrometIO, self).clean_field_name(field)
        return field.replace(self.station.value.lower(), "")

    # NetLoader configuration
    @property
    def url(self):
        if self.script is None:
            raise NotImplementedError("Script must be defined!")
        return "http://%s/%s-bin/%s" % (
            self.website, self.region, self.script
        )

    @property
    def params(self):
        start = self.start_date.value
        end = self.end_date.value
        params, params_is_complex = self.getlist('parameter')
        pcodes = [
            "%s %s" % (self.station.value, param)
            for param in params
        ]

        # Note: The USBR Perl scripts are pretty quirky: a specific ordering of
        # URL parameters is important for proper function.
        return OrderedDict([
            ('parameter', ",".join(pcodes)),
            ('syer', start.year),
            ('smnth', start.month),
            ('sdy', start.day),
            ('eyer', end.year),
            ('emnth', end.month),
            ('edy', end.day),
            ('format', 2),
        ])

    # Help CsvParser find data
    def reader_class(self):
        cls = super(HydrometIO, self).reader_class()

        class Reader(cls):
            def choose_header(self, rows):
                for i, row in enumerate(rows):
                    if len(row) > 0 and row[0] == "BEGIN DATA":
                        return i + 1, rows[i + 1]
                return 0, ['header_not_found']
        return Reader

    # Cancel BaseIO iteration when END DATA is seen
    # FIXME: what about len()?
    def usable_item(self, item):
        item = super(HydrometIO, self).usable_item(item)
        if item[0] == "END DATA":
            return None
        return item


class DailyDataIO(HydrometIO):
    """
    Retrieves daily values for USBR Hydromet/Agrimet sites.

    Usage:

    data = DailyDataIO(station='ACAO', parameter=['GD','QD'])
    for row in data:
        print row.date, row.gd, row.qd
    """

    script = "webarccsv.pl"
    key_fields = ['date']


class InstantDataIO(HydrometIO):
    """
    Retrieves instant (e.g. 15-min) values for USBR Hydromet/Agrimet sites.

    Usage:

    data = InstantDataIO(station='ACAO', parameter=['GH','Q'])
    for row in data:
        print row.datetime, row.gh, row.q
    """

    script = "webdaycsv.pl"
    key_fields = ['datetime']


# PN also has an agrimet.pl that can return all data from the last 2 weeks of
# data for a station (no params need to be specified)
class AgrimetRecentIO(InstantDataIO):
    """
    Load recent Agrimet data (all available parameters)

    Usage:

    data = AgrimetRecentIO(station='ABEI')
    for row in data:
        print row.datetime, row.ob, row.wd
    """
    script = "agrimet.pl"

    start_date = FilterOpt(ignored=True)
    end_date = FilterOpt(ignored=True)
    parameter = FilterOpt(ignored=True)

    @property
    def params(self):
        return OrderedDict([
            ('cbtt', self.station.value),
            ('interval', 'instant'),
            ('format', 2),
            ('back', 360)
        ])
