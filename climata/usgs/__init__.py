from wq.io import TimeSeriesMapper, XmlNetIO, CsvNetIO, JsonNetIO, CsvFileIO
from datetime import datetime, date, timedelta
from wq.io.parsers import readers
from collections import namedtuple, OrderedDict
import os

filename = os.path.join(os.path.dirname(__file__), 'parameter_cd_query.txt')


class USGSIO(CsvNetIO):
    """
      Base class for loading data from USGS web services: summary.
      url: http://waterservices.usgs.gov/nwis/site/?format=rdb,
        1.0&huc=18010101&seriesCatalogOutput=true&outputDataTypeCd=all
    """
    basin = None  # 18010201  # ,18010202, 18010203, etc.
    max_header_row = 100
    delimiter = "\t"
    parameterCd = ''

    @property
    def params(self):
        return {
            'format': 'rdb,1.0',
            'huc': self.basin,
            #'seriesCatalogOutput': 'true',
            'outputDataTypeCd': 'iv,dv,gw,id,aw',
            'parameterCd': self.parameterCd,
            'siteStatus': 'active',
            }

    @property
    def url(self):
        return "http://waterservices.usgs.gov/nwis/site/" % self.params

    def list_to_csv(self):
        pass


class SiteDataIO(JsonNetIO):
    """
    Base class for loading data from the USGS web services: actual site data.

    Here's how the data is layed out:
    [{index}]       # The index is for each site
        [1]         # 0 = sourceInfo; 1 = Values; 2 = Variables; 3 = Name
            [0]     # This should probably be left as '0' as it's a spacer
                ['value'] # This is to get the values list for each site
                    [{index}] # Loop through this level for each site to get
                              # to get the values
    """
    basin = None
    debug = True
    namespace = "value.timeSeries"
    start_date = None  # '1950-01-01'
    end_date = datetime.strftime(datetime.today(), '%Y-%m-%d')
    siteType = None  # 'LK,ST,ST-CA,ST-DCH,ST-TS,SP,
    # GW,GW-CR,GW-EX,GW-HZ,GW-IW,GW-MW,GW-TH'
    parameterCd = None  # '00055,00056,00058,00059,00060,00061,
    # 00062,00064,00065,00072,72015,72016,72019,72020'

    @property
    def params(self):
        return {
            'format': 'json',
            'indent': 'on',
            'huc': self.basin,
            'startDT': self.start_date,
            'endDt': self.end_date,
            #'siteType': self.siteType,  # Not necessary with parameter codes.
            'parameterCd': self.parameterCd,  # measurements in ft and ft3/s
        }

    @property
    def url(self):
        return "http://waterservices.usgs.gov/nwis/dv/"


class SitesForHucIO(SiteDataIO):
    '''
    This is just designed to obtain all valid sites for a given huc id.
    '''
    basin = None  # 18010202
    debug = False
    startDT = None  # '2013-09-01'
    endDT = None  # '2013-12-30'
    parameterCd = None  # '00055,00056,00058,00059,00060,00061,
    # 00062,00064,00065,00072,72015,72016,72019,72020'

    @property
    def url(self):
        return "http://waterservices.usgs.gov/nwis/iv/"

    @property
    def params(self):
        return {
            'format': 'json,1.1',
            'huc': self.basin,
            'startDT': self.startDT,
            'endDT': self.endDT,
            'parameterCd': self.parameterCd,
        }


class InstantValuesIO(SiteDataIO):
    '''
    This class examines the instantaneous values for USGS data.
    '''
    debug = False
    start_date = ''
    sites = ''
    end_date = ''

    @property
    def url(self):
        return "http://waterservices.usgs.gov/nwis/iv/"

    @property
    def params(self):
        return {
            'format': 'json,1.1',
            'sites': self.sites,
            'startDT': self.start_date,
            'endDT': self.end_date,
            # 'parameterCd':'00055,00056,00058,00059,00060,00061,
            # 00062,00064,00065,00072,72015,72016,72019,72020',
            # 'siteType':'LK,ST,ST-CA,ST-DCH,ST-TS,SP,
            # GW,GW-CR,GW-EX,GW-HZ,GW-IW,GW-MW,GW-TH',
        }


class ParamIO(CsvFileIO):
    """
    The USGS water data has a very large code mapping segment for the parm_cd
    field that needs to be put into readable text
    """
    delimiter = "\t"
    debug = True
    max_header_row = 8
    filename = filename
    key_field = 'parm_cd'
