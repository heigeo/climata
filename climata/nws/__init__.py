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
    
    def parse(self):
        doc = ET.parse(self.file)
        root = doc.getroot()
        if self.root_tag is None:
            self.root_tag = root.tag
        if self.item_tag is None:
            self.item_tag = list(root)[1].tag # This is the data
        self.data = map(self.parse_item, root.findall(self.item_tag))
    
    def parse_item(self, element):
        item = {}
        for elem in element:
            layout_key = ''
            if elem.tag == 'time-layout':
                print elem[0].text
                start_dates = []
                end_dates = []
                for el in elem:
                    if el.tag == 'layout-key':
                        layout_key = el.text
                    elif el.tag == 'start-valid-time':
                        start_dates.append(el.text)
                    elif el.tag == 'end-valid-time':
                        end_dates.append(el.text)
                item[layout_key] = {'start_dates':[], 'end_dates':[], 'name': '', 'values':[]}
                item[layout_key]['start_dates'] = start_dates
                item[layout_key]['end_dates'] = end_dates
                
            if elem.tag == 'parameters':
                for el in elem: # This level is a climate-anomaly
                    for e in el: # This level is where the tag gets the time-layout           
                        layout_key = e.items()[2][1]
                        values_list = []
                        for val in e:
                            if val.tag == 'name':
                                item[layout_key]['name'] = val.text
                            else:
                                values_list.append(val.text)
                        item[layout_key]['values'] = values_list
        return item