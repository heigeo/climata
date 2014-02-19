from wq.io import BaseIO
from datetime import datetime, date, timedelta
from wq.io.parsers import readers
from collections import namedtuple, OrderedDict
from SOAPpy import SOAPProxy
import os
import time
import pickle

namespace = 'http://www.wcc.nrcs.usda.gov/ns/awdbWebService'
url = 'http://www.wcc.nrcs.usda.gov/awdbWebService/services?WSDL'
server = SOAPProxy(url, namespace)
today = datetime.now()


class SnotelIO(BaseIO):
    '''
     Works with the SOAP.py library to make a soap request.
     The data is stored in a cached file to speed loading, then
     it is loaded from the cache and returned.
    '''
    filename = None  # File name is the actual filename
    data_function = None
    cache = True
    debug = True

    def load(self):
        if self.cache:
            if self.checkfile():
                self.write_cache
            f = open(self.filename, 'r')
            self.data = pickle.load(f)
            f.close()
        else:
            self.data = self.data_function

    def write_cache(self):
        f = open(self.filename, 'w+')
        data = self.data_function
        pickle.dump(data, f)
        f.close()

    def checkfile(self):
        if os.path.isfile(self.filename):
            filedate = datetime.fromtimestamp(os.path.getmtime(self.filename))
            timediff = datetime.now() - filedate
            if timediff > timedelta(days=7):
                return True
            else:
                return False
        else:
            return True


class SnotelForecastIO(SnotelIO):
    stationTriplet = ''
    elementCd = ''
    forecastPeriod = ''
    cache = False

    @property
    def data_function(self):
        return server.getForecasts(
            stationTriplet=self.stationTriplet,
            elementCd=self.elementCd,
            forecastPeriod=self.forecastPeriod
        )


class SnotelForecastPubIO(SnotelIO):
    stationTriplet = ''
    elementCd = ''
    forecastPeriod = ''
    publicationDate = ''
    cache = False
    debug = True

    @property
    def data_function(self):
        return server.getForecast(
            stationTriplet=self.stationTriplet,
            elementCd=self.elementCd,
            forecastPeriod=self.forecastPeriod,
            publicationDate=self.publicationDate
        )


class SnotelSiteListIO(SnotelIO):
    hucs = None
    networkCds = None
    cache = True
    elements = ''

    @property
    def filename(self):
        return 'cache/site_list_%s.py' % self.hucs.replace(':', '-')

    @property
    def data_function(self):
        return server.getStations(
            hucs=self.hucs,
            networkCds=self.networkCds,
            logicalAnd='true',
            elementCds=self.elements,
            )


class SnotelStationMetaIO(SnotelIO):
    site = None
    cache = True

    @property
    def filename(self):
        return 'cache/station_meta_%s.py' % self.site.replace(':', '-')

    @property
    def data_function(self):
        return server.getStationMetadata(stationTriplet=self.site)


class SnotelStationElementsIO(SnotelIO):
    station = None
    cache = True

    @property
    def filename(self):
        return 'cache/station_elements_%s.py' % self.station.replace(':', '-')

    @property
    def data_function(self):
        return server.getStationElements(stationTriplet=str(self.station))


class SnotelElementsIO(SnotelIO):
    cache = False

    @property
    def data_function(self):
        return server.getElements()


class SnotelDailyDataIO(SnotelIO):
    station_triplets = None
    element_cd = None
    start_date = None

    @property
    def filename(self):
        return 'cache/daily_data_%s_%s.py' % (
            self.station_triplets.replace(':', '-'), self.element_cd)

    @property
    def data_function(self):
        return server.getData(
            stationTriplets=self.station_triplets,
            elementCd=self.element_cd,
            ordinal=1,
            duration='DAILY',
            getFlags='true',  # Needs to be true for the other to be false
            beginDate=self.start_date,
            endDate=str(datetime.date(datetime.now()).isoformat()),
            alwaysReturnDailyFeb29='false'
            )


class ForecastPeriodsIO(SnotelIO):
    cache = False
    debug = True

    @property
    def filename(self):
        return None

    @property
    def data_function(self):
        return server.getForecastPeriods()


class SnotelHourlyDataIO(SnotelIO):
    station_triplets = None
    element_cd = None
    start_date = None

    @property
    def filename(self):
        return 'cache/hourly_data_%s_%s.py' % (
            self.station_triplets.replace(':', '-'), self.element_cd)

    @property
    def data_function(self):
        return server.getHourlyData(
            stationTriplets=self.station_triplets,
            elementCd=self.element_cd,
            ordinal=1,
            beginDate=self.start_date,
            endDate=str(datetime.date(datetime.now()).isoformat()),
        )


class SnotelForecastData(SnotelIO):
    station_triplets = None
    element_cd = None
    forecast_period = None
    publication_date = None

    @property
    def filename(self):
        return 'forecast_data_%s_%s.py' % (
            self.station_triplets.replace(':', '-'), self.element_cd)

    @property
    def data_function(self):
        return server.getForecast(
            stationTriplets=self.station_triplets,
            elementCd=self.elementCd,
            forecastPeriod=self.forecast_period,
            publicationDate=self.publication_date,
        )
