from wq.io import BaseIO, XmlNetIO
from datetime import datetime, date, timedelta
from wq.io.parsers import readers
from SOAPpy import SOAPProxy
# The following imports are probably not necessary once the IO is working properly
from xml.etree import ElementTree as ET
import requests

# This service can be accessed via SOAP or through REST. I chose the Rest/XML implementation
# to work with wq.io more seamlessly

class NWSIO(XmlNetIO):
    lat = ''
    lon = ''
    product = 'time-series'
    begin = '' # Leave blank to get all data
    end = '' # leave blank to get all data
    unit = 'e' # for english measurements
    baseurl = 'http://graphical.weather.gov/xml/sample_products/browser_interface/ndfdXMLclient.php'
    # http://graphical.weather.gov/xml/docs/elementInputNames.php
    parameters = {
    'Probability of 8- To 14-Day Total Precipitation Above Median': 'prcpabv14d',
    'Probability of 8- To 14-Day Total Precipitation Below Median': 'prcpblw14d',
    'Probability of One-Month Total Precipitation Above Median': 'prcpabv30d',
    'Probability of One-Month Total Precipitation Below Median': 'prcpblw30d',
    'Probability of Three-Month Total Precipitation Above Median': 'prcpabv90d',
    'Probability of Three-Month Total Precipitation Below Median': 'prcpblw90d',
    }
    debug=True
    param_list = ['prcpabv14d', 'prcpblw14d', 'prcpabv30d', 'prcpblw30d', 'prcpabv90d', 'prcpblw90d']
    
    @property
    def params(self):
        dic = {
            'lat':self.lat,
            'lon':self.lon,
            'product':self.product,
            'begin':self.begin,
            'end':self.end,
            'Unit':self.unit, 
        }
        for p in self.param_list:
            dic[p] = p
        return dic
    
    @property
    def url(self):
        return self.baseurl % self.params


# This IO makes a mess out of the headers, since the structure is weird.
# Sample URL:
# http://graphical.weather.gov/xml/sample_products/browser_interface/ndfdXMLclient.php?product=time-series&prcpblw90d=prcpblw90d&end=&prcpblw14d=prcpblw14d&prcpblw30d=prcpblw30d&lon=-120.872&begin=&prcpabv90d=prcpabv90d&prcpabv14d=prcpabv14d&lat=37.937&prcpabv30d=prcpabv30d&Unit=e
r = requests.get('http://graphical.weather.gov/xml/sample_products/browser_interface/ndfdXMLclient.php?product=time-series&prcpblw90d=prcpblw90d&end=&prcpblw14d=prcpblw14d&prcpblw30d=prcpblw30d&lon=-120.872&begin=&prcpabv90d=prcpabv90d&prcpabv14d=prcpabv14d&lat=37.937&prcpabv30d=prcpabv30d&Unit=e')
tree = ET.fromstring(r.text)
for element in tree[1]:
    for el in element:
        print el.text
    print element.text

tree[1][2][0].text