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
    debug=True

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
    cache=False
    debug=True
    
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
        return '/var/www/klamath/db/loaddata/climata/climata/snotel/cache/forecast_data_%s_%s.py' % (
            self.station_triplets.replace(':', '-'), self.element_cd)

    @property
    def data_function(self):
        return server.getForecast(
            stationTriplets=self.station_triplets,
            elementCd=self.elementCd,
            forecastPeriod=self.forecast_period,
            publicationDate=self.publication_date,
        )

def checkfile(filename=None):
    '''
     Returns True if the file is expired or does not exist
     and False if the file should be loaded.
    '''
    if os.path.isfile(filename):
        filedate = datetime.fromtimestamp(os.path.getmtime(filename))
        timediff = today - filedate
        if timediff > timedelta(days=7):
            return True
        else:
            return False
    else:
        return True


def site_list(hucs=None, networkCds=None):
    '''
     This function returns a list of sites in triplet format
     Triplets have this format: [station id]:[state code]:[network code]
     http://www.wcc.nrcs.usda.gov/web_service/AWDB_Web_Service_Reference.htm
     Network Codes:
     BOR Any Bureau of Reclamation reservoir stations plus
                    other non-BOR reservoir stations
     CLMIND Used to store climate indices (such as Southern Oscillation Index
                    or Trans-Nino Index)
     COOP National Weather Service COOP stations
     MPRC Manual precipitation sites
     MSNT Manual SNOTEL non-telemetered, non-real time sites
     SNOW NRCS Snow Course Sites
     SNTL NWCC SNOTEL and SCAN stations
     USGS Any USGS station, but also other non-USGS streamflow stations
    '''
    filestring = 'cache/site_list_%s.py' % hucs.replace(':', '-')

    def write_contents_to_file():
        f = open(filestring, 'w+')
        sites = server.getStations(
            hucs=str(hucs),
            networkCds=networkCds,
            logicalAnd='true')
        pickle.dump(sites, f)
        f.close()

    if checkfile(filestring):
        write_contents_to_file()
    f = open(filestring, 'r')
    return pickle.load(f)


def station_meta(site=None):
    '''
     Gets the beginDate, endDate, fipsCountryCd (US), countyName,
     fipsStateNumber, elevation, huc (eg. 180102040103), hud (eg. 18020001),
     latitude, longitude, name, shefId (eg. CRWC1),
     stationDataTimeZone (eg. -8.0), stationTriplet
    '''
    filestring = 'cache/station_meta_%s.py' % site.replace(':', '-')

    def write_contents_to_file():
        f = open(filestring, 'w+')
        station = server.getStationMetadata(stationTriplet=site)
        pickle.dump(station, f)
        f.close()
    if checkfile(filestring):
        write_contents_to_file()
    f = open(filestring)
    return pickle.load(f)


def station_elements(station=None):
    '''
     This returns a list of element codes measured at a given station
     Also has the beginDate and endDate and the storedUnitCode for the
     thing being measured.
    '''
    filestring = 'cache/station_elements_%s.py' % station.replace(':', '-')

    def write_contents_to_file():
        f = open(filestring, 'w+')
        elements = server.getStationElements(stationTriplet=str(station))
        pickle.dump(elements, f)
        f.close()
    if checkfile(filestring):
        write_contents_to_file()
    f = open(filestring)
    return pickle.load(f)


def element_list(element=None):  # Not needed
    '''
     This returns a list of elements, which are measurement codes
     the elementCd needed for queries is accessed at elements[i].elementCd
     where i is the index. elements[i].name is a description of the measurement
     and elements[i].storedUnitCd is the unit of measurement
    '''
    elements = server.getElements()
    return elements


def get_daily_data(stationTriplets=None, elementCd=None, startDate=None):
    '''
     This gets the daily data for any site or list of sites
     for only one element code. Although it is possible that other measurements
     can be read from by the ordinal, '1' is the most common according to the
     documentation.
    '''
    filestring = '''cache/daily_data_%s_%s.py
                        ''' % (stationTriplets.replace(':', '-'), elementCd)

    def write_contents_to_file(**kwargs):
        today = datetime.strftime(datetime.now(), 'YYYY-MM-dd')
        f = open(filestring, 'w+')
        data = server.getData(
            stationTriplets=stationTriplets,
            elementCd=elementCd,
            ordinal=1,
            duration='DAILY',
            getFlags='true',  # Needs to be true for the other to be false
            beginDate=startDate,
            endDate=str(datetime.date(datetime.now()).isoformat()),
            alwaysReturnDailyFeb29='false'
            )
        pickle.dump(data, f)
        f.close()

    if checkfile(filestring):
        write_contents_to_file()
    f = open(filestring, 'r')
    return pickle.load(f)


def get_hourly_data(stationTriplets=None, elementCd=None, startDate=None):
    '''
     Nearly identical to daily data. Gets hourly values instead
    '''
    filestring = '''cache/hourly_data_%s_%s.py
                    ''' % (stationTriplets.replace(':', '-'), elementCd)

    def write_contents_to_file():
        today = datetime.strftime(datetime.now(), 'YYYY-MM-dd')
        f = open(filestring, 'w+')
        data = server.getHourlyData(
            stationTriplets=stationTriplets,
            elementCd=elementCd,
            ordinal=1,
            beginDate=startDate,
            endDate=str(datetime.date(datetime.now()).isoformat()),
        )
        pickle.dump(data, f)
        f.close()

    if checkfile(filestring):
        write_contents_to_file()
    f = open(filestring, 'r')
    return pickle.load(f)
