from wq.io import TimeSeriesMapper, XmlParser, BaseIO
from datetime import datetime
from climata.base import WebserviceLoader, FilterOpt, DateOpt, ChoiceOpt


class CocorahsIO(WebserviceLoader, XmlParser, TimeSeriesMapper, BaseIO):
    """
    Retrieves CoCoRaHS observations from data.cocorahs.org

    Usage:

    data = CocorahsIO(state='MN', county='HN')
    for row in data:
        print row.stationname, row.observationdate.date(), row.totalprecipamt
    """

    # Customize date parameters
    start_date = DateOpt(
        required=True,
        date_only=False,
        url_param="StartDate",
    )
    end_date = DateOpt(
        date_only=False,
        url_param="EndDate",
    )

    # These region filters are supported
    state = FilterOpt(required=True)
    county = FilterOpt()

    # Other filters are ignored
    basin = FilterOpt(ignored=True)
    station = FilterOpt(ignored=True)
    parameter = FilterOpt(ignored=True)

    # CoCoRaHS-specific options
    datetype = ChoiceOpt(
        url_param="ReportDateType",
        default="reportdate",
        choices=["reportdate", "timestamp"],
    )
    reporttype = ChoiceOpt(
        url_param="ReportType",
        default="Daily",
        choices=["Daily", "MultiDay"],
    )

    # Configuration for wq.io base classes
    url = "http://data.cocorahs.org/cocorahs/export/exportreports.aspx"

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

    # These params apply to every request
    default_params = {
        'dtf': "1",
        'Format': "XML",
        'TimesInGMT': "False",
        'responsefields': "all"
    }

    @property
    def item_tag(self):
        if self.getvalue('reporttype') == "Daily":
            return 'DailyPrecipReports/DailyPrecipReport'
        else:
            # i.e. self.getvalue('reporttype') == "MultiDay"
            return 'MultiDayPrecipReports/MultiDayPrecipReport'

    def serialize_params(self, params, complex):
        params = super(CocorahsIO, self).serialize_params(params, complex)
        fmt = '%m/%d/%Y'

        # Different date parameters and formats depending on use case
        if 'EndDate' in params:
            # Date range (usually used with datetype=reportdate)
            params['StartDate'] = self.getvalue('start_date').strftime(fmt)
            params['EndDate'] = self.getvalue('end_date').strftime(fmt)
        else:
            # Only start date (usually used with datetype=timestamp)
            params['Date'] = self.getvalue(
                'start_date'
            ).strftime(fmt + " %I:%M %p")
            del params['StartDate']
        return params

    def map_value(self, field, value):
        value = super(CocorahsIO, self).map_value(field, value)
        # CoCoRaHS empty dates are represented as 1/1/0001
        if isinstance(value, datetime) and value.year == 1:
            return None
        return value
