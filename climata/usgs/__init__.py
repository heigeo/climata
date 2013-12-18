from wq.io import TimeSeriesMapper, XmlNetIO, CsvNetIO, JsonNetIO, CsvFileIO
from datetime import datetime, date, timedelta
from wq.io.parsers import readers
from collections import namedtuple, OrderedDict
import os

filename = os.path.join(os.path.dirname(__file__), 'parameter_cd_query.txt')

class USGSIO(CsvNetIO):
    """
    Base class for loading data from USGS web services This loads the summary data. 
    url: http://waterservices.usgs.gov/nwis/site/?format=rdb,1.0&huc=18010101&seriesCatalogOutput=true&outputDataTypeCd=all
    """
    basin = 18010101 #, 18010102, 18010103, etc.
    max_header_row=100
    delimiter = "\t"

    @property
    def url(self):
        return "http://waterservices.usgs.gov/nwis/site/?format=rdb,1.0&huc=%s&seriesCatalogOutput=true&outputDataTypeCd=all" % self.basin
  
  
    def list_to_csv(self):
        pass

class SiteDataIO(JsonNetIO):
    """
    Base class for loading data from the USGS web services. This loads the actual site data. 
    """
    site_name = 11532000
    max_header_row = 100
    @property
    def url(self):
        return "http://waterservices.usgs.gov/nwis/dv/?format=json&indent=on&sites=%s&startDT=1950-01-01&endDT=2013-12-17" % self.site_name
    
class ParamIO(CsvFileIO):
    """
    The USGS water data has a very large code mapping segment for the parm_cd field that needs to be put into readable text
    """
    delimiter = "\t"
    debug=True
    max_header_row=8
    filename = filename
    key_field = 'parm_cd'
    
    
    
    
    
    
    
    
    
    
    
    
    
    