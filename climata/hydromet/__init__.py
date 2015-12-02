from wq.io import CsvParser, TimeSeriesMapper, TupleMapper, BaseIO
from collections import OrderedDict
from climata.base import WebserviceLoader, FilterOpt
from wq.io.exceptions import NoData
from requests.compat import urlencode


class HydrometLoader(WebserviceLoader):
    """
    Shared options for Hydromet IO classes.
    """

    # start_date and end_date are the same as WebserviceLoader defaults

    # None of the default region filters will work
    state = FilterOpt(ignored=True)
    county = FilterOpt(ignored=True)
    basin = FilterOpt(ignored=True)

    # Instead, specify a four-letter Hydromet station code (one per request)
    station = FilterOpt(required=True)

    # Hydromet parameter codes are also required (multiple allowed)
    parameter = FilterOpt(required=True, multi=True)


class HydrometIO(HydrometLoader, CsvParser, TimeSeriesMapper, BaseIO):
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

    def clean_field_name(self, field):
        return field.replace(self.getvalue('station').upper(), "").strip()

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
        start = self.getvalue('start_date')
        end = self.getvalue('end_date')
        params, params_is_complex = self.getlist('parameter')
        pcodes = [
            "%s %s" % (self.getvalue('station'), param)
            for param in params
        ]

        # Note: The USBR Perl scripts are pretty quirky: a specific ordering of
        # URL parameters is important for proper function.
        return urlencode(OrderedDict([
            ('parameter', ",".join(pcodes)),
            ('syer', start.year),
            ('smnth', start.month),
            ('sdy', start.day),
            ('eyer', end.year),
            ('emnth', end.month),
            ('edy', end.day),
            ('format', 2),
        ]))

    # Help CsvParser find data starting with BEGIN DATA
    def reader_class(self):
        cls = super(HydrometIO, self).reader_class()

        class Reader(cls):
            def choose_header(self, rows):
                for i, row in enumerate(rows):
                    if len(row) > 0 and row[0] == "BEGIN DATA":
                        return i + 1, rows[i + 1]
                raise NoData
        return Reader

    # Remove END DATA and trailing HTML from output
    def parse(self):
        super(HydrometIO, self).parse()
        if not self.data:
            return
        end_i = None
        for i in range(len(self.data)):
            row = self.data[-i - 1]
            if "END DATA" in row.values():
                end_i = i
        if end_i is None:
            return
        self.data = self.data[:-end_i - 1]


class DailyDataIO(HydrometIO):
    """
    Retrieves daily values for a single USBR Hydromet/Agrimet site.

    Usage:

    data = DailyDataIO(station='ACAO', parameter=['GD','QD'])
    for row in data:
        print row.date, row.gd, row.qd
    """

    script = "webarccsv.pl"
    key_fields = ['date']


class MultiStationDailyIO(HydrometLoader, TupleMapper, BaseIO):
    """
    Retrieves daily values for one or more USBR Hydromet/Agrimet sites.
    (Internally calls DailyDataIO for each site.)

    Usage:

    data = MultiStationDailyIO(station=['ACAO'], parameter=['GD','QD'])
    for s in data:
        print s.station
        for row in s.data:
            print row.date, row.gd, row.qd
    """

    nested = True

    station = FilterOpt(required=True, multi=True)

    # Customize load function with nested IOs
    def load(self):
        self.data = [{
            'station': station,
            'data': DailyDataIO(
                station=station,
                parameter=self.getvalue('parameter'),
                start_date=self.getvalue('start_date'),
                end_date=self.getvalue('end_date'),
                debug=self.debug,
            )
        } for station in self.getvalue('station')]

    def parse(self):
        pass


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
        return urlencode(OrderedDict([
            ('cbtt', self.getvalue('station')),
            ('interval', 'instant'),
            ('format', 2),
            ('back', 360)
        ]))
