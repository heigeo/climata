from wq.io import CsvNetIO, TimeSeriesMapper
from datetime import datetime, date, timedelta
from collections import OrderedDict


class HydrometIO(TimeSeriesMapper, CsvNetIO):
    """
    Retrieves Hydromet data from USBR

    Usage:

    data = HydrometIO(station='ACAO', parameters=['GD','QD'])
    for row in data:
        print row.date, row.gd, row.qd
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
    script = 'webarccsv.pl'

    # TimeSeriesMapper configuration
    date_formats = ['%m/%d/%Y %H:%M', '%m/%d/%Y']
    key_fields = ['datetime', 'date']

    def clean_field_name(self, field):
        field = super(HydrometIO, self).clean_field_name(field)
        return field.replace(self.station.lower(), "")

    # NetLoader configuration
    @property
    def url(self):
        return "http://%s/%s-bin/%s" % (
            self.website, self.region, self.script
        )

    @property
    def params(self):
        if not self.station:
            raise NotImplementedError("Station must be defined!")
        if not self.parameters:
            raise NotImplementedError("Parameters must be defined!")

        # Unfortunately, webarccsv.pl expects a very specific order of
        # parameters in the query string. Thus, instead of returning a dict()
        # here we need to construct the query string manually.
        params = '&'.join([
            "format=2",
            "year={start.year}",
            "month={start.month}",
            "day={start.day}",
            "year={end.year}",
            "month={end.month}",
            "day={end.day}",
            "station={station}"
        ]).format(
            start=self.startdate,
            end=self.enddate,
            station=self.station.upper()
        )
        for param in self.parameters:
            params += '&pcode=' + param.upper()
        return params

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


# PN also has an agrimet.pl that can return the last 8 days of data for a
# station (no params need to be specified)
class AgrimetIO(HydrometIO):
    script = "agrimet.pl"

    @property
    def params(self):
        if not self.station:
            raise NotImplementedError("Station must be defined!")
        return OrderedDict([
            ('cbtt', self.station),
            ('interval', 'instant'),
            ('format', 2),
            ('back', 192)
        ])
