from wq.io import CsvNetIO, TimeSeriesMapper
from datetime import datetime, date, timedelta
from collections import OrderedDict


class HydrometIO(TimeSeriesMapper, CsvNetIO):
    """
    Base class for retrieving Hydromet data from USBR.
    Use DailyDataIO or InstantDataIO instead, depending on your needs.
    """

    # USBR region: pn or gp
    region = 'pn'

    # Four-letter Hydromet station code
    station = None

    # Hydromet parameter codes
    parameters = []

    # Date Range
    startdate = date.today() - timedelta(days=30)
    enddate = date.today()

    website = 'www.usbr.gov'
    script = None

    # TimeSeriesMapper configuration
    date_formats = ['%m/%d/%Y %H:%M', '%m/%d/%Y']

    def clean_field_name(self, field):
        field = super(HydrometIO, self).clean_field_name(field)
        return field.replace(self.station.lower(), "")

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
        if not self.station:
            raise NotImplementedError("Station must be defined!")
        if not self.parameters:
            raise NotImplementedError("Parameters must be defined!")

        start = self.startdate
        end = self.enddate
        pcodes = [
            "%s %s" % (self.station, param)
            for param in self.parameters
        ]
        # Note: ordering of URL parameters is important
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

    data = DailyDataIO(station='ACAO', parameters=['GD','QD'])
    for row in data:
        print row.date, row.gd, row.qd
    """

    script = "webarccsv.pl"
    key_fields = ['date']


class InstantDataIO(HydrometIO):
    """
    Retrieves instant (e.g. 15-min) values for USBR Hydromet/Agrimet sites.

    Usage:

    data = InstantDataIO(station='ACAO', parameters=['GH','Q'])
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

    @property
    def params(self):
        if not self.station:
            raise NotImplementedError("Station must be defined!")
        return OrderedDict([
            ('cbtt', self.station),
            ('interval', 'instant'),
            ('format', 2),
            ('back', 360)
        ])
