from wq.io import BaseIO, TupleMapper, TimeSeriesMapper
from wq.io.exceptions import NoData
from wq.io.parsers import readers
from datetime import datetime, date, timedelta
from collections import namedtuple, OrderedDict
from SOAPpy import SOAPProxy
from SOAPpy.Types import simplify
from climata.base import WebserviceLoader, FilterOpt, DateOpt, ChoiceOpt
from climata.base import fill_date_range
import os
import time

namespace = 'http://www.wcc.nrcs.usda.gov/ns/awdbWebService'
url = 'http://www.wcc.nrcs.usda.gov/awdbWebService/services?WSDL'
server = SOAPProxy(url, namespace)
today = datetime.now()


class SnotelIO(WebserviceLoader):
    '''
     Works with the SOAP.py library to make a soap request.
     The data is stored in a cached file to speed loading, then
     it is loaded from the cache and returned.
    '''
    # Overriding default parameters
    start_date = DateOpt(ignored=True)
    end_date = DateOpt(ignored=True)
    state = FilterOpt(ignored=True)  # State is not used
    basin = FilterOpt(ignored=True, url_param='hucs')
    county = FilterOpt(ignored=True)  # never used

    # Adding additional parameters.
    station = FilterOpt(ignored=True, url_param='stationTriplet')
    parameter = FilterOpt(url_param='elementCd')

    data_function = None
    debug = True

    def load(self):
        params = self.params
        fn = getattr(server, self.data_function)
        self.snotel_data = fn(**params)
        #raise Exception(self.snotel_data)

    def parse(self):
        self.data = simplify(self.snotel_data)
        if not isinstance(self.snotel_data, list):
            self.data = [simplify(self.snotel_data)]


class SnotelSiteIO(SnotelIO, TupleMapper, BaseIO):
    data_function = 'getStations'
    parameter = FilterOpt(required=False, url_param='elementCds')
    basin = FilterOpt(required=False, url_param='hucs')
    county = FilterOpt(required=False, url_param='countyNames')
    station_ids = FilterOpt(required=False, url_param='stationIds')
    min_latitude = FilterOpt(required=False, url_param='minLatitude')
    max_latitude = FilterOpt(required=False, url_param='maxLatitude')
    min_elevation = FilterOpt(required=False, url_param='minElevation')
    max_elevation = FilterOpt(required=False, url_param='maxElevation')
    ordinals = FilterOpt(required=False, url_param='ordinals')
    # heightDepths = FilterOpt(required=False, url_param='heightDepths')
    # This parameter is submitted as
    # <heightDepths><value>value</value><unitCd>unit</unitCd></heightDepths>
    # Left out since it doesn't seem important and isn't well-documented

    default_params = {
        'logicalAnd': 'true',
    }

    def load(self):
        super(SnotelSiteIO, self).load()
        station_meta = []
        for row in self.snotel_data:
            fn2 = getattr(server, 'getStationMetadata')
            tdict = simplify(fn2(stationTriplet=row))
            station_meta.append(tdict)
        self.data = station_meta
        field_names = set()
        for row in self.data:
            field_names.update(row.keys())
        self.field_names = field_names

    def parse(self):
        pass


class SnotelStationMetaIO(SnotelIO, TupleMapper, BaseIO):
    data_function = 'getStationMetadata'
    station = FilterOpt(required=True, url_param='stationTriplet')
    parameter = FilterOpt(ignored=True)


class SnotelStationElementsIO(SnotelIO, TupleMapper, BaseIO):
    data_function = 'getStationElements'
    station = FilterOpt(required=True, url_param='stationTriplet')
    start_date = DateOpt(required=True, url_param='beginDate')
    end_date = DateOpt(required=True, url_param='endDate')
    parameter = FilterOpt(ignored=True)


class SnotelStationDataMetaIO(SnotelStationElementsIO):
    date_formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d']
    nested = True

    def load(self):
        super(SnotelStationDataMetaIO, self).load()
        station_meta = []
        for row in self.snotel_data:
            try:
                if row.duration == "DAILY":
                    sd = datetime.strftime(self.getvalue('start_date'), '%Y-%m-%d')
                    ed = datetime.strftime(self.getvalue('end_date'), '%Y-%m-%d')
                    daily = SnotelDailyDataIO(
                        station=row.stationTriplet,
                        parameter=row.elementCd,
                        start_date=sd,
                        end_date=ed,
                    )
                    tdict = simplify(row)
                    tdict['data'] = daily.data
                    station_meta.append(tdict)
            except:
                pass
        self.data = station_meta

    def parse(self):
        pass


class SnotelStationListElementsLookupIO(SnotelSiteIO):
    start_date = DateOpt(required=True)
    end_date = DateOpt(required=True)

    def load(self):
        params = self.params
        if params.has_key('start_date'):
            params.pop('start_date')
        if params.has_key('end_date'):
            params.pop('end_date')
        fn = getattr(server, 'getStations')
        self.snotel_data = fn(**params)
        sd = datetime.strftime(self.getvalue('start_date'), '%Y-%m-%d')
        ed = datetime.strftime(self.getvalue('end_date'), '%Y-%m-%d')
        parent_dict = []
        for row in self.snotel_data:
            elems = SnotelStationDataMetaIO(station=row, start_date=sd, end_date=ed)
            if elems.data != []:
                for item in elems.data:
                    parent_dict.append(item)
        self.data = parent_dict

class SnotelElementsIO(SnotelIO, TupleMapper, BaseIO):
    data_function = 'getElements'
    parameter = FilterOpt(ignored=True)


class SnotelDailyDataIO(SnotelIO, TupleMapper, BaseIO):
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
        self.snotel_data = simplify(self.snotel_data)
        try:
            bd = self.snotel_data['beginDate']
            ed = self.snotel_data['endDate']
            df = '%Y-%m-%d %H:%M:%S'
            zipped = fill_date_range(bd, ed, date_format=df)
            vals = self.snotel_data['values']
            flags = self.snotel_data['flags']
            self.unnamed_tuple = zip(zipped, vals, flags)
            self.data = [{
                'date': date,
                'value': val,
                'flag': flag
            } for date, val, flag in self.unnamed_tuple]
        except:
            raise NoData


class SnotelHourlyDataIO(SnotelIO, TimeSeriesMapper, BaseIO):
    data_function = 'getHourlyData'
    date_formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M'
    ]
    station = FilterOpt(required=True, url_param='stationTriplets')
    parameter = FilterOpt(required=True, url_param='elementCd')
    start_date = DateOpt(required=True, url_param='beginDate')
    end_date = DateOpt(required=True, url_param='endDate')
    begin_hour = FilterOpt(required=False, url_param='beginHour')
    end_hour = FilterOpt(required=False, url_param='endHour')
    '''
    HeightDepth parameters don't seem to be necessary.
    '''

    default_params = {
        'ordinal': 1,
    }

    def parse(self):
        self.data = simplify(self.snotel_data['values'])


class ForecastPeriodsIO(SnotelIO, TupleMapper, BaseIO):
    data_function = 'getForecastPeriods'
    parameter = FilterOpt(ignored=True)


class SnotelForecastData(SnotelIO, TupleMapper, BaseIO):
    data_function = 'getForecast'
    station = FilterOpt(required=True, url_param='stationTriplets')
    parameter = FilterOpt(required=True, url_param='elementCd')
    forecast_period = FilterOpt(required=True, url_param='forecastPeriod')
    publication_date = DateOpt(required=True, url_param='publicationDate')


class SnotelForecastIO(SnotelIO, TupleMapper, BaseIO):
    data_function = 'getForecasts'
    station = FilterOpt(required=True, url_param='stationTriplet')
    parameter = FilterOpt(required=True, url_param='elementCd')
    forecastPeriod = FilterOpt(required=True, url_param='forecastPeriod')
