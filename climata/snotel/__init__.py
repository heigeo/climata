from wq.io import TimeSeriesMapper, CsvNetIO, JsonNetIO
from datetime import datetime, date, timedelta
from wq.io.parsers import readers
from collections import namedtuple, OrderedDict
from SOAPpy import SOAPProxy
import os, time, pickle


namespace = 'http://www.wcc.nrcs.usda.gov/ns/awdbWebService'
url = 'http://www.wcc.nrcs.usda.gov/awdbWebService/services?WSDL'
server = SOAPProxy(url, namespace)
today = datetime.now()


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

def site_list(hucs = None, networkCds=None):
    '''
     This function returns a list of sites in triplet format
     Triplets have this format: [station id]:[state code]:[network code]
     http://www.wcc.nrcs.usda.gov/web_service/AWDB_Web_Service_Reference.htm
     Network Codes:
     BOR Any Bureau of Reclamation reservoir stations plus other non-BOR reservoir stations
     CLMIND Used to store climate indices (such as Southern Oscillation Index or Trans-Nino Index)
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
        sites = server.getStations(hucs=str(hucs), networkCds=networkCds, logicalAnd='true')
        pickle.dump(sites, f)
        f.close()
    
    if checkfile(filestring):
        write_contents_to_file()
    f = open(filestring, 'r')
    return pickle.load(f)

def station_meta(site=None):
    '''
     Gets the beginDate, endDate, fipsCountryCd (US), countyName, fipsStateNumber,
     elevation, huc (eg. 180102040103), hud (eg. 18020001), latitude, longitude, name,
     shefId (eg. CRWC1), stationDataTimeZone (eg. -8.0), stationTriplet
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

def station_elements(station = None):
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


def element_list(element = None):  # Not needed
    '''
     This returns a list of elements, which are measurement codes
     the elementCd needed for queries is accessed at elements[i].elementCd
     where i is the index. elements[i].name is a description of the measurement
     and elements[i].storedUnitCd is the unit of measurement
    '''
    elements = server.getElements()
    return elements

def get_daily_data(stationTriplets = None, elementCd = None):
    '''
     This gets the daily data for any site or list of sites
     for only one element code. Although it is possible that other measurements
     can be read from by the ordinal, '1' is the most common according to the
     documentation. 
    '''
    today = datetime.strftime(datetime.now(), 'YYYY-MM-dd')
    data = server.getData(
        stationTriplets=stationTriplets,
        elementCd=elementCd,
        ordinal=1,
        duration='DAILY',
        getFlags='false',
        beginDate='2000-01-01',
        endDate=str(datetime.date(datetime.now()).isoformat())
        )

class SnotelIO(CsvNetIO):
    """
      Files are located on this base directory:
      http://www.wcc.nrcs.usda.gov/ftpref/data/snow/snotel/cards/
      Then %state_name/% for oregon or california
      The file names are %id%_all.txt. Each file seems to have a different
      first column. %ST%SITENAME-date where %ST% is the 2-character
      state name. The other columns are:
      pill  prec    tmax    tmin    tavg    prcp
      
      Klamath Watershed:
      43.284, -121.566
      42.810, -120.874
      41.918, -120.627
      41.507, -121.132
      41.491, -122.006
      40.207, -122.994
      41.565, -124.066
      41.983, -123.500
      42.252, -122.418
      42.786, -122.159
      
      CA:
      SNTL 	2000 	CA 	CROWDER FLAT (977) 		1999-October 	2100-January 	41.89 	-120.75 	5170 	Modoc 	Mosquito Creek-Willow Creek (180102040103)  20H02S
      OR:
      SNTL 	2007 	OR 	SWAN LAKE MTN (1077) 		2006-October 	2100-January 	42.41 	-121.68 	6830 	Klamath 	Grizzly Butte (180102040802)    21G16S
      SNTL 	2006 	OR 	SUN PASS (1078) 		2006-June 	2100-January 	42.79 	-121.98 	5400 	Klamath 	Egan Spring-Williamson River (180102010602) 21G17S
      SNTL 	1980 	OR 	CHEMULT ALTERNATE (395) 		1980-June 	2100-January 	43.23 	-121.81 	4850 	Klamath 	Deer Creek (180102010201)   21F22S
      SNTL 	1980 	OR 	COLD SPRINGS CAMP (406) 		1980-June 	2100-January 	42.53 	-122.18 	5940 	Klamath 	Upper Fourmile Creek (180102030202) 22G24S
      SNTL 	1980 	OR 	HYATT PRAIRIE (259) 		1980-June 	1990-October 	42.18 	-122.47 	4900 	Jackson 	Keene Creek (180102060405)  
      SNTL 	1980 	OR 	QUARTZ MOUNTAIN (706) 		1980-June 	2100-January 	42.32 	-120.83 	5720 	Lake 	Middle South Fork Sprague River (180102020404)  20G06S
      SNTL 	1980 	OR 	SEVENMILE MARSH (745) 		1980-June 	2100-January 	42.70 	-122.14 	5700 	Klamath 	Sevenmile Creek (180102030104)  22G33S
      SNTL 	1980 	OR 	STRAWBERRY (794) 		1980-June 	2100-January 	42.13 	-120.84 	5770 	Lake 	Barnes Valley Creek (180102040501)  20G09S
      SNTL 	1979 	OR 	BILLIE CREEK DIVIDE (344) 		1978-October 	2100-January 	42.41 	-122.27 	5280 	Klamath 	Seldom Creek (180102030201) 22G13S
      SNTL 	1979 	OR 	SUMMER RIM (800) 		1978-October 	2100-January 	42.70 	-120.80 	7080 	Lake 	Headwaters Sycan River (180102020103)   20G02S
      SNTL 	1979 	OR 	TAYLOR BUTTE (810) 		1978-October 	2100-January 	42.69 	-121.43 	5030 	Klamath 	Chester Spring-Sycan River (180102020606)   21G03S
      
    """
    delimiter = "\t"
    site_code = '20H02S'
    state = 'california'
    debug = True
     
    @property
    def filename(self):
        return "%s_all.txt" % self.site_code.lower() # 20h02s for Crowder Flat
   
    
    @property
    def url(self):
        return "http://www.wcc.nrcs.usda.gov/ftpref/data/snow/snotel/cards/%s/%s" % (self.state, self.filename)