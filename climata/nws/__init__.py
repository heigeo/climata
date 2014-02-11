from wq.io import BaseIO, XmlNetIO, CsvNetIO
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
        self.data = self.parse_item(list(root)[1])
        #self.data = map(self.parse_item, root.findall(self.item_tag))
    
    def parse_item(self, element):
        item = []
        for elem in element:
            layout_key = ''
            if elem.tag == 'time-layout':
                start_dates = []
                end_dates = []
                for el in elem:
                    if el.tag == 'layout-key':
                        layout_key = el.text
                    elif el.tag == 'start-valid-time':
                        start_dates.append(el.text)
                    elif el.tag == 'end-valid-time':
                        end_dates.append(el.text)
                item.append({'key':layout_key, 'start_dates':start_dates, 'end_dates':end_dates, 'name': '', 'values':[]})
            if elem.tag == 'parameters':
                for el in elem: # This level is a climate-anomaly
                    for e in el: # This level is where the tag gets the time-layout           
                        layout_key = e.items()[2][1]
                        values_list = []
                        for val in e:
                            if val.tag == 'name':
                                for it in item:
                                    if it['key'] == layout_key:
                                        it['name'] = val.text
                            else:
                                values_list.append(val.text)
                        for it in item:
                            if it['key'] == layout_key:
                                it['values'] = values_list
        item_to_return = []
        for a, b in enumerate(item):
            item_to_return.append({'key': b['key'], 'name': b['name'], 'values': []})
            values_as_timeseries = []
            for j, k in enumerate(b['end_dates']):
                ts = {
                    'end_date': b['end_dates'][j], 
                    'start_date': b['start_dates'][j],
                    'value': b['values'][j],
                    }
                values_as_timeseries.append(ts)
            item_to_return[a]['values']=values_as_timeseries
        return item_to_return


class NWSForecastIO(XmlNetIO):
    ###########################################
    # valid is the time of the forecast in UTC
    # primary is the stage in ft 
    # secondary is the flow in kcfs
    # pedts is ???
    # It appears to return 3 days forecast in the future
    # 
    ###########################################
    gage = ''

    @property
    def url(self):
        return 'http://water.weather.gov/ahps2/hydrograph_to_xml.php' % self.params

    @property
    def params(self):
        return {
            'gage':self.gage,
            'output':'xml',
        }

    def parse(self):
        doc = ET.parse(self.file)
        root = doc.getroot()
        if self.root_tag is None:
            self.root_tag = root.tag
        if self.item_tag is None:
            for l in list(root):
                if l.tag == 'forecast':
                    self.item_tag = l
                    print self.item_tag
        self.data = self.parse_item(self.item_tag)

    def parse_item(self, element):
        items = []
        for el in element:
            item = {
                el[0].tag : el[0].text,
                el[1].tag : el[1].text,
                el[2].tag : el[2].text,
                el[3].tag : el[3].text,
            }
            items.append(item)
        return items


class CNRFForecastIO(CsvNetIO):
    ###################################################
    # This gets the table in tab-separated HTML format
    # Hopefully we can get a better way to access the
    # forecast data.
    ###################################################
    location = 'KLAO3'
    accumtype = 'mean'
    interval = 'day'
    disttype = 'empirical'
    S_month = '02'
    S_day = '10'
    S_year = '2014'
    E_month = '05'
    E_day= '10'
    E_year= '2014'
    plottype = 'traces'
    tabletype = 'forecastinfo'
    outtype = 'Generate+a+Table'
    
    @property
    def url(self):
        return 'http://www.cnrfc.noaa.gov/send_espTrace.cgi' % self.params

    @property
    def params(self):
        return {
            'location':self.location,
            'accumtype':self.accumtype,
            'interval':self.interval,
            'disttype':self.disttype,
            'S_month':self.S_month,
            'S_day':self.S_day,
            'S_year':self.S_year,
            'E_month':self.E_month,
            'E_day':self.E_day,
            'E_year':self.E_year,
            'plottype':self.plottype,
            'tabletype':self.tabletype,
            'outtype':self.outtype,
        }
