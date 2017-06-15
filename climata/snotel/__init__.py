from __future__ import print_function

from wq.io import BaseIO, TupleMapper, TimeSeriesMapper
from wq.io.parsers.base import BaseParser
from wq.io.exceptions import NoData
from wq.io.util import flattened

from suds.client import Client
from suds.sudsobject import asdict, Object as SudsObject
from climata.base import WebserviceLoader, FilterOpt, DateOpt
from climata.base import fill_date_range, as_list

url = 'https://wcc.sc.egov.usda.gov/awdbWebService/services?WSDL'
_server = None


def get_server():
    global _server
    if _server is None:
        _server = Client(url).service
    return _server


class SnotelIO(WebserviceLoader, BaseParser, TupleMapper, BaseIO):
    """
    Base class for accessing SNOTEL AWDB SOAP web services.
    """

    webservice_name = "awdbWebService"
    data_function = None

    # Override Default WebserviceLoader options
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
        fn = getattr(get_server(), self.data_function)
        self.data = fn(**params)
        if len(self.data) == 0:
            self.data = []
        else:
            self.data = as_list(self.data)
            if isinstance(self.data[0], SudsObject):
                parse = asdict
            else:
                parse = str
            self.data = [parse(row) for row in self.data]

    # Some records may have additional fields; loop through entire
    # array to ensure all field names are accounted for.  (Otherwise BaseIO
    # will guess field names using only the first record.)
    scan_fields = True

    def print_debug(self):
        print('%s.%s(%s)' % (
            self.webservice_name,
            self.data_function,
            ','.join(
                '%s=%s' % (key, val)
                for key, val in self.params.items()
            )
        ))


class StationIO(SnotelIO):
    """
    Retrieve metadata for all stations in a region.  Leverages both
    getStations() and getStationMetadata().
    """

    data_function = 'getStations'

    # Applicable WebserviceLoader default options
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
    """
    Wrapper for getStationMetadata() - used internally by StationIO.
    """

    data_function = 'getStationMetadata'

    station = FilterOpt(required=True, url_param='stationTriplet')


class StationElementIO(SnotelIO):
    """
    Wrapper for getStationElements(), incorporating element names from
    getElements()
    """

    data_function = 'getStationElements'

    # Applicable WebserviceLoader default options
    start_date = DateOpt(url_param='beginDate')
    end_date = DateOpt(url_param='endDate')
    station = FilterOpt(required=True, url_param='stationTriplet')

    def load(self):
        super(StationElementIO, self).load()
        names = ElementIO.get_names()
        for elem in self.data:
            elem['element_name'] = names[elem['elementCd']]


class StationDataIO(StationElementIO):
    """
    Base class for StationDailyDataIO and StationHourlyDataIO.  Retrieves all
    data for a station that matches the specified duration by calling the
    specified inner_io_class.
    """
    nested = True

    # Applicable WebserviceLoader default options
    start_date = DateOpt(url_param='beginDate', required=True)
    end_date = DateOpt(url_param='endDate', required=True)
    parameter = FilterOpt()

    inner_io_class = None
    duration = None

    @property
    def params(self):
        params = super(StationDataIO, self).params
        # Parameter filter (if any) is applied *after* the initial request
        params.pop('parameter', None)
        return params

    def load(self):
        super(StationDataIO, self).load()
        data = []
        for row in self.data:

            # Only include records matching the specified duration
            # and parameter
            if row['duration'] != self.duration:
                continue
            elem = self.getvalue('parameter')
            if elem and row['elementCd'] != elem:
                continue

            # getStationElements() sometimes returns parameters that don't
            # actually have data for the requested timeframe - silently catch
            # the exception and remove parameter from results.
            try:
                row['data'] = self.inner_io_class(
                    station=row['stationTriplet'],
                    parameter=row['elementCd'],
                    start_date=self.getvalue('start_date'),
                    end_date=self.getvalue('end_date'),
                    debug=self.debug,
                )
            except NoData:
                continue

            data.append(row)

        self.data = data


class ElementIO(SnotelIO):
    """
    List of all SNOTEL element names, codes and units.
    """
    data_function = 'getElements'

    @classmethod
    def get_elements(cls):
        """
        Store singleton instance on IO to speed up retrieval after first call.
        """
        if not hasattr(cls, '_cache'):
            cls._cache = cls()
        return cls._cache

    @classmethod
    def get_names(cls):
        return {
            e.elementcd: e.name
            for e in cls.get_elements()
        }


class DailyDataIO(SnotelIO):
    """
    Wrapper for getData(), used internally by StationDailyDataIO
    """
    data_function = 'getData'

    # Applicable WebserviceLoader default options
    station = FilterOpt(required=True, url_param='stationTriplets')
    parameter = FilterOpt(required=True, url_param='elementCd')
    start_date = DateOpt(required=True, url_param='beginDate')
    end_date = DateOpt(required=True, url_param='endDate')

    # HeightDepth parameters don't seem to be necessary.

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
    """
    Requests all daily data for the specified station, optionally filtered by
    parameter.  The outer IO is the list of available parameters/elements, with
    each item in the list containing a nested IO with the actual data.

    Usage:

    params = StationDailyDataIO(
        station='302:OR:SNTL',
        start_date='2014-07-01',
        end_date='2014-07-31'
    )
    for param in params:
        print param.element_name
        for row in param.data:
            print "   ", row.date, row.value, param.storedunitcd

    """
    inner_io_class = DailyDataIO
    duration = "DAILY"


class RegionDailyDataIO(StationIO):
    """
    All-in-one IO for loading site metadata and daily data for a region (i.e. a
    state, county, or basin).  Internally calls:
      - getStations()
      - getStationMetadata()
      - getStationElements()
      - getData()

    The outer IO is a list of sites in the region - derived from StationIO, but
    with an extra "data" property on each station pointing to an inner time
    series IO for each site.  The inner IO is based on StationDailyDataIO but
    flattened to avoid multiple levels of nesting.  parameter is optional but
    recommended (otherwise all available data for all sites will be returned).

    Usage:

    sites = RegionDailyDataIO(
        basin='17060105',
        start_date='2014-07-01',
        end_date='2014-07-31',
        parameter='TAVG',
    )
    for site in sites:
        print site.name
        for row in site.data:
            print "   ", row.date, row.value, row.storedunitcd

    """

    nested = True

    # Applicable WebserviceLoader default options
    start_date = DateOpt(required=True)
    end_date = DateOpt(required=True)
    parameter = FilterOpt(url_param='elementCds')

    @property
    def params(self):
        params = super(RegionDailyDataIO, self).params
        # Start and end date are actually only used by inner io.
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


class HourlyDataIO(TimeSeriesMapper, SnotelIO):
    """
    Wrapper for getHourlyData(), used internally by StationHourlyDataIO
    """
    data_function = 'getHourlyData'

    # TimeSeriesMapper configuration
    date_formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M'
    ]

    # Applicable WebserviceLoader default options
    station = FilterOpt(required=True, url_param='stationTriplets')
    parameter = FilterOpt(required=True, url_param='elementCd')
    start_date = DateOpt(required=True, url_param='beginDate')
    end_date = DateOpt(required=True, url_param='endDate')

    # Additional options
    begin_hour = FilterOpt(url_param='beginHour')
    end_hour = FilterOpt(url_param='endHour')

    # HeightDepth parameters don't seem to be necessary.

    default_params = {
        'ordinal': 1,
    }

    def load(self):
        super(HourlyDataIO, self).load()
        if self.data and 'values' in self.data[0]:
            self.data = [
                asdict(row)
                for row in as_list(self.data[0]['values'])
            ]
        else:
            raise NoData


class StationHourlyDataIO(StationDataIO):
    """
    Requests all hourly data for the specified station, optionally filtered by
    parameter.  The outer IO is the list of available parameters/elements, with
    each item in the list containing a nested IO with the actual data.

    Usage:

    params = StationHourlyDataIO(
        station='302:OR:SNTL',
        start_date='2014-07-01',
        end_date='2014-07-02',
    )
    for param in params:
        print param.element_name
        for row in param.data:
            print "   ", row.datetime, row.value, param.storedunitcd

    """
    inner_io_class = HourlyDataIO
    duration = "HOURLY"


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

    forecast_period = FilterOpt(required=True, url_param='forecastPeriod')
