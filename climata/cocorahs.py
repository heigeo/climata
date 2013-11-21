from wq.io import TimeSeriesMapper, XmlNetIO
from datetime import datetime, date, timedelta


class CocorahsIO(TimeSeriesMapper, XmlNetIO):
    """
    Retrieves CoCoRaHS observations from data.cocorahs.org

    Usage:

    data = CocorahsIO(state='MN', county='HN')
    for row in data:
        print row.stationname, row.observationdate.date(), row.totalprecipamt
    """

    state = None
    county = None
    startdate = date.today() - timedelta(days=30)
    enddate = date.today()
    datetype = "reportdate"
    type = "Daily"

    url = "http://data.cocorahs.org/cocorahs/export/exportreports.aspx"
    params = {
        'dtf': "1",
        'Format': "XML",
        'TimesInGMT': "False",
        'responsefields': "all"
    }
    root_tag = 'Cocorahs'

    date_formats = [
        '%Y-%m-%d %I:%M %p',
        '%Y-%m-%d',
        '%I:%M %p',
        '%m/%d/%Y %I:%M %p'
    ]

    key_fields = [
        "stationnumber",
        "stationname",
        "latitude",
        "longitude",
        "datetimestamp",
        "observationdate",
        "observationtime",
        "entrydatetime",
    ]

    @property
    def item_tag(self):
        if self.type == "Daily":
            return 'DailyPrecipReports/DailyPrecipReport'
        elif self.type == "MultiDay":
            return 'MultiDayPrecipReports/MultiDayPrecipReport'
        raise Exception("%s is not a valid report type!" % self.type)

    def load(self):
        fmt = '%m/%d/%Y'
        self.params['ReportType'] = self.type
        self.params['State'] = self.state
        if self.county is not None:
            self.params['County'] = self.county

        self.params['ReportDateType'] = self.datetype
        if self.datetype == "reportdate":
            self.params['StartDate'] = self.startdate.strftime(fmt)
            self.params['EndDate'] = self.enddate.strftime(fmt)
        elif self.datetype == "timestamp":
            self.params['Date'] = self.startdate.strftime(fmt + " %I:%M %p")

        super(CocorahsIO, self).load()

    def map_value(self, field, value):
        value = super(CocorahsIO, self).map_value(field, value)
        if isinstance(value, datetime) and value.year == 1:
            return None
        return value
