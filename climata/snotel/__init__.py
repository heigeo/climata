from wq.io import BaseIO
from datetime import datetime, date, timedelta
from wq.io.parsers import readers
from collections import namedtuple, OrderedDict
from SOAPpy import SOAPProxy
from SOAPpy.Types import simplify
from climata.base import WebserviceLoader, FilterOpt, DateOpt, ChoiceOpt
import os
import time
from datetime import datetime, timedelta

namespace = 'http://www.wcc.nrcs.usda.gov/ns/awdbWebService'
url = 'http://www.wcc.nrcs.usda.gov/awdbWebService/services?WSDL'
server = SOAPProxy(url, namespace)
today = datetime.now()

def fill_date_range(start_date, end_date):
    '''
    Function accepts start and end dates as strings and returns a list of dates (as strings)
    '''
    dateformat = '%Y-%m-%d %H:%M:%S'
    start_date = datetime.strptime(start_date, dateformat)
    end_date = datetime.strptime(end_date, dateformat)
    datelist = []
    while start_date <= end_date:
        datelist.append(datetime.strftime(start_date, dateformat))
        start_date = start_date + timedelta(days=1)
    return datelist

class SnotelIO(WebserviceLoader):
    '''
     Works with the SOAP.py library to make a soap request.
     The data is stored in a cached file to speed loading, then
     it is loaded from the cache and returned.
    '''
    # Overriding default parameters
    start_date = DateOpt(ignored=True)
    end_date = DateOpt(ignored=True)
    state = FilterOpt(ignored=True) # State is not used
    basin = FilterOpt(ignored=True, multi=True, url_param='hucs')
    county = FilterOpt(ignored=True) # never used
    
    # Adding additional parameters.
    station = FilterOpt(ignored=True, multi=True, url_param='stationTriplet')
    parameter = FilterOpt(multi=True, url_param='elementCd')
    forecastPeriod = FilterOpt(ignored=True, multi=True)
    networkCds = FilterOpt(ignored=True, multi=True, url_param='networkCds')
    
    data_function = None
    debug = True

    def load(self):
        params = self.params
        fn = getattr(server, self.data_function)
        self.snotelData = fn(**params)

    def parse(self):
        self.data = [simplify(self.snotelData)]

class SnotelSiteListIO(SnotelIO, BaseIO):
    data_function = 'getStations'
    elementCds = FilterOpt(required=False, url_param='elementCds')
    stationIds = FilterOpt(required=False, url_param='stationIds')
    county = FilterOpt(required=False, url_param='countyNames')
    minLatitude = FilterOpt(required=False, url_param='minLatitude')
    maxLatitude = FilterOpt(required=False, url_param='maxLatitude')
    minElevation = FilterOpt(required=False, url_param='minElevation')
    maxElevation = FilterOpt(required=False, url_param='maxElevation')
    ordinals = FilterOpt(required=False, url_param='ordinals')
    # heightDepths = FilterOpt(required=False, url_param='heightDepths')
    # This parameter is submitted as <heightDepths><value>value</value><unitCd>unit</unitCd></heightDepths>
    # Since it doesn't seem important and isn't well-documented, it is left out for now.
    
    default_params = {
        'logicalAnd': 'true',
    }


class SnotelStationMetaIO(SnotelIO, BaseIO):
    data_function = 'getStationMetadata'
    station = FilterOpt(multi=False, required=True, url_param='stationTriplet')
    parameter = FilterOpt(ignored=True)


class SnotelStationElementsIO(SnotelIO, BaseIO):
    data_function = 'getStationElements'
    station = FilterOpt(multi=False, url_param='stationTriplet')
    start_date = DateOpt(ignored=False, required=False, url_param='beginDate')
    end_date = DateOpt(ignored=False, required=False, url_param='endDate')
    parameter = FilterOpt(ignored=True)
    

class SnotelElementsIO(SnotelIO, BaseIO):
    data_function = 'getElements'
    parameter = FilterOpt(ignored=True)


class SnotelDailyDataIO(SnotelIO, BaseIO):
    data_function = 'getData'
    station = FilterOpt(required=True, multi=True, url_param='stationTriplets')
    parameter = FilterOpt(required=True, multi=True, url_param='elementCd')  # not sure if multi is possible
    start_date = DateOpt(required=True, url_param='beginDate')
    end_date = DateOpt(required=True, url_param='endDate')
    '''
        HeightDepth parameters apply as in SnotelSiteListIO, but don't seem to be necessary.
    '''
    
    default_params = {
        'ordinal': 1,
        'duration': 'DAILY',
        'getFlags': 'true',
        'alwaysReturnDailyFeb29': 'false',
    }
    def parse(self):
        self.snotelData = simplify(self.snotelData)
        self.data = zip(fill_date_range(self.snotelData['beginDate'], self.snotelData['endDate']), self.snotelData['values'], self.snotelData['flags'])


class SnotelHourlyDataIO(SnotelIO, BaseIO):
    data_function = 'getHourlyData'
    station = FilterOpt(required=True, url_param='stationTriplets', multi=True)
    parameter = FilterOpt(required=True, url_param='elementCd')
    start_date = DateOpt(required=True, url_param='beginDate')
    end_date = DateOpt(required=True, url_param='endDate')
    begin_hour = FilterOpt(required=False, url_param='beginHour')
    end_hour = FilterOpt(required=False, url_param='endHour')
    
    '''
        HeightDepth parameters apply as in SnotelSiteListIO, but don't seem to be necessary.
    '''
    
    default_params = {
        'ordinal': 1,
    }
    def parse(self):
        self.data = simplify(self.snotelData['values'])


class ForecastPeriodsIO(SnotelIO, BaseIO):
    data_function = 'getForecastPeriods'
    parameter = FilterOpt(ignored=True)


class SnotelForecastData(SnotelIO, BaseIO):
    data_function = 'getForecast'
    
    station = FilterOpt(required=True, url_param='stationTriplets', multi=True)
    parameter = FilterOpt(required=True, url_param='elementCd')
    forecast_period = FilterOpt(required=True, url_param='forecastPeriod')
    publication_date = DateOpt(required=True, url_param='publicationDate')


class SnotelForecastIO(SnotelIO, BaseIO):
    data_function = 'getForecasts'
    station = FilterOpt(required=True, multi=False, url_param='stationTriplet')
    parameter = FilterOpt(required=True, url_param='elementCd')
    forecastPeriod = FilterOpt(required=True, url_param='forecastPeriod')


class SnotelForecastPubIO(SnotelIO):
    data_function = 'getForecast'
    station = FilterOpt(required=True, multi=False, url_param='stationTriplet')
    parameter = FilterOpt(required=True, url_param='elementCd')
    forecastPeriod = FilterOpt(required=True, url_param='forecastPeriod')
    publication_date = DateOpt(required=True, url_param='publicationDate')
