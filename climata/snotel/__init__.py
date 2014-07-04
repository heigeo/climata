from wq.io import BaseIO, TupleMapper, TimeSeriesMapper
from wq.io.parsers.base import BaseParser
from wq.io.exceptions import NoData
from wq.io.util import flattened

from SOAPpy import SOAPProxy, simplify
from climata.base import WebserviceLoader, FilterOpt, DateOpt, ChoiceOpt
from climata.base import fill_date_range, as_list

namespace = 'http://www.wcc.nrcs.usda.gov/ns/awdbWebService'
url = 'http://www.wcc.nrcs.usda.gov/awdbWebService/services?WSDL'
server = SOAPProxy(url, namespace)


class SnotelIO(WebserviceLoader, BaseParser, TupleMapper, BaseIO):
    '''
     Works with the SOAP.py library to make a soap request.
    '''

    webservice_name = "awdbWebService"
    data_function = None

    # Default WebserviceLoader parameters
    start_date = DateOpt(ignored=True)
    end_date = DateOpt(ignored=True)
    state = FilterOpt(ignored=True)
    basin = FilterOpt(ignored=True)
    county = FilterOpt(ignored=True)
    station = FilterOpt(ignored=True)
    parameter = FilterOpt(ignored=True)

    def load(self):
        if self.debug:
            self.print_debug()
        params = self.params
        fn = getattr(server, self.data_function)
        self.data = simplify(fn(**params))
        if self.data == {}:
            self.data = []
        else:
            self.data = as_list(self.data)

    def parse(self):
        # Some records may have additional fields; loop through entire
        # array to ensure all fields are accounted for.

        field_names = set()
        for row in self.data:
            field_names.update(row.keys())
        self.field_names = field_names

    def print_debug(self):
        print '%s.%s(%s)' % (
            self.webservice_name,
            self.data_function,
            ','.join(
                '%s=%s' % (key, val)
                for key, val in self.params.items()
            )
        )

class StationIO(SnotelIO):
    data_function = 'getStations'

    state = FilterOpt(url_param='stateCds', multi=True)
    county = FilterOpt(url_param='countyNames', multi=True)
    basin = FilterOpt(url_param='hucs', multi=True)
    parameter = FilterOpt(url_param='elementCds', multi=True)

    # Additional options
    min_latitude = FilterOpt(url_param='minLatitude')
    max_latitude = FilterOpt(url_param='maxLatitude')
    min_elevation = FilterOpt(url_param='minElevation')
    max_elevation = FilterOpt(url_param='maxElevation')
    ordinals = FilterOpt(url_param='ordinals')

    # This is not the same as station (stationTriplet)
    station_ids = FilterOpt(url_param='stationIds', multi=True)

    # heightDepths = FilterOpt(url_param='heightDepths')
    # This parameter is submitted as
    # <heightDepths><value>value</value><unitCd>unit</unitCd></heightDepths>
    # Left out since it doesn't seem important and isn't well-documented

    default_params = {
        'logicalAnd': 'true',
    }

    def load(self):
        super(StationIO, self).load()
        self.data = [
            StationMetaIO(station=station, debug=self.debug).data[0]
            for station in self.data
        ]


class StationMetaIO(SnotelIO):
    data_function = 'getStationMetadata'

    station = FilterOpt(required=True, url_param='stationTriplet')


class StationElementIO(SnotelIO):
    data_function = 'getStationElements'

    start_date = DateOpt(url_param='beginDate')
    end_date = DateOpt(url_param='endDate')
    station = FilterOpt(required=True, url_param='stationTriplet')

    def load(self):
        super(StationElementIO, self).load()
        names = {e.elementcd: e.name for e in elements}
        for elem in self.data:
            elem['element_name'] = names[elem['elementCd']]


class StationDataIO(StationElementIO):
    nested = True

    start_date = DateOpt(url_param='beginDate', required=True)
    end_date = DateOpt(url_param='endDate', required=True)
    parameter = FilterOpt()

    inner_io_class = None
    duration = None

    @property
    def params(self):
        params = super(StationDataIO, self).params
        params.pop('parameter', None)
        return params

    def load(self):
        super(StationDataIO, self).load()
        data = []
        for row in self.data:
            if row['duration'] != self.duration:
                continue
            elem = self.getvalue('parameter')
            if elem and row['elementCd'] != elem:
                continue

            try:
                row['data'] = self.inner_io_class(
                    station=row['stationTriplet'],
                    parameter=row['elementCd'],
                    start_date=self.getvalue('start_date'),
                    end_date=self.getvalue('end_date'),
                    debug=self.debug,
                )
            except NoData:
                row['data'] = []
            data.append(row)
        self.data = data


class RegionDailyDataIO(StationIO):
    nested = True

    start_date = DateOpt(required=True)
    end_date = DateOpt(required=True)
    parameter = FilterOpt(url_param='elementCds')

    @property
    def params(self):
        params = super(RegionDailyDataIO, self).params
        del params['start_date']
        del params['end_date']
        return params

    def load(self):
        super(RegionDailyDataIO, self).load()
        for station in self.data:
            station['data'] = flattened(
                StationDailyDataIO,
                station=station['stationTriplet'],
                start_date=self.getvalue('start_date'),
                end_date=self.getvalue('end_date'),
                parameter=self.getvalue('parameter'),
                debug=self.debug,
            )


class ElementIO(SnotelIO):
    data_function = 'getElements'

elements = ElementIO()


class DailyDataIO(SnotelIO):
    data_function = 'getData'

    station = FilterOpt(required=True, url_param='stationTriplets')
    parameter = FilterOpt(required=True, url_param='elementCd')
    start_date = DateOpt(required=True, url_param='beginDate')
    end_date = DateOpt(required=True, url_param='endDate')
    '''
    HeightDepth parameters don't seem to be necessary.
    '''

    default_params = {
        'ordinal': 1,
        'duration': 'DAILY',
        'getFlags': 'true',
        'alwaysReturnDailyFeb29': 'false',
    }

    def parse(self):
        data = self.data[0]
        if not data or 'values' not in data:
            raise NoData
        bd = data['beginDate']
        ed = data['endDate']
        dates = fill_date_range(bd, ed, date_format='%Y-%m-%d %H:%M:%S')
        vals = as_list(data['values'])
        flags = as_list(data['flags'])

        self.data = [{
            'date': date,
            'value': val,
            'flag': flag
        } for date, val, flag in zip(dates, vals, flags)]


class StationDailyDataIO(StationDataIO):
    inner_io_class = DailyDataIO
    duration = "DAILY"


class HourlyDataIO(TimeSeriesMapper, SnotelIO):
    data_function = 'getHourlyData'

    date_formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M'
    ]
    station = FilterOpt(required=True, url_param='stationTriplets')
    parameter = FilterOpt(required=True, url_param='elementCd')
    start_date = DateOpt(required=True, url_param='beginDate')
    end_date = DateOpt(required=True, url_param='endDate')
    begin_hour = FilterOpt(url_param='beginHour')
    end_hour = FilterOpt(url_param='endHour')
    '''
    HeightDepth parameters don't seem to be necessary.
    '''

    default_params = {
        'ordinal': 1,
    }

    def load(self):
        super(HourlyDataIO, self).load()
        if self.data and 'values' in self.data[0]:
            self.data = as_list(self.data[0]['values'])
        else:
            raise NoData


class ForecastPeriodIO(SnotelIO):
    data_function = 'getForecastPeriods'


class ForecastDataIO(SnotelIO):
    data_function = 'getForecast'

    station = FilterOpt(required=True, url_param='stationTriplets')
    parameter = FilterOpt(required=True, url_param='elementCd')

    forecast_period = FilterOpt(required=True, url_param='forecastPeriod')
    publication_date = DateOpt(required=True, url_param='publicationDate')


class ForecastIO(SnotelIO):
    data_function = 'getForecasts'

    station = FilterOpt(required=True, url_param='stationTriplet')
    parameter = FilterOpt(required=True, url_param='elementCd')

    forecastPeriod = FilterOpt(required=True, url_param='forecastPeriod')
