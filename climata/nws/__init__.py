from wq.io import BaseIO, CsvNetIO, TupleMapper, TimeSeriesMapper
from wq.io.parsers.base import BaseParser
from datetime import datetime, date, timedelta
from wq.io.parsers import readers
from SOAPpy import SOAPProxy
from climata.base import WebserviceLoader, FilterOpt, DateOpt, ChoiceOpt
from xml.etree import ElementTree as ET
from dateutil import parser

# This service can be accessed via SOAP
# or through REST. I chose the Rest/XML implementation
# to work with wq.io more seamlessly

parameters = {
    'Prob. of 8-14-Day Total Precipitation Above Median': 'prcpabv14d',
    'Prob. of 8-14-Day Total Precipitation Below Median': 'prcpblw14d',
    'Prob. of 1-Month Total Precipitation Above Median': 'prcpabv30d',
    'Prob. of 1-Month Total Precipitation Below Median': 'prcpblw30d',
    'Prob. of 3-Month Total Precipitation Above Median': 'prcpabv90d',
    'Prob. of 3-Month Total Precipitation Below Median': 'prcpblw90d',
}


class NWSIO(WebserviceLoader, BaseParser, BaseIO):
    #######################################################
    ## This doesn't work as a timeseries, because        ##
    ## a) The returned values vary by parameter, and     ##
    ## b) The values come with a start and end date each ##
    #######################################################
    start_date = DateOpt(ignored=True)  # begin='' Leave blank to get all data
    end_date = DateOpt(ignored=True)  # end = ''  # leave blank to get all data
    state = FilterOpt(ignored=True)
    lat = FilterOpt()  # lat = ''
    lon = FilterOpt()  # lon = ''
    baseurl = 'http://graphical.weather.gov/xml/sample_products/'
    baseurl = baseurl + 'browser_interface/ndfdXMLclient.php'
    # http://graphical.weather.gov/xml/docs/elementInputNames.php
    root_tag = None
    item_tag = None
    default_params = {
        'product': 'time-series',
        'unit': 'e',
        'prcpabv14d': 'prcpabv14d',
        'prcpblw14d': 'prcpblw14d',
        'prcpabv30d': 'prcpabv30d',
        'prcpblw30d': 'prcpblw30d',
        'prcpabv90d': 'prcpabv90d',
        'prcpblw90d': 'prcpblw90d',
    }
    debug = True

    @property
    def url(self):
        return self.baseurl  # % self.params

    def parse(self):
        doc = ET.parse(self.file)
        root = doc.getroot()
        if self.root_tag is None:
            self.root_tag = root.tag
        if self.item_tag is None:
            self.item_tag = list(root)[1].tag  # This is the data
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
                item.append({
                    'key': layout_key,
                    'start_dates': start_dates,
                    'end_dates': end_dates,
                    'name': '',
                    'values': []
                    })
            if elem.tag == 'parameters':
                for el in elem:  # This level is a climate-anomaly
                    for e in el:  # Where the tag gets the time-layout
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
            item_to_return.append({
                'key': b['key'],
                'name': b['name'],
                'values': []
                })
            values_as_timeseries = []
            for j, k in enumerate(b['end_dates']):
                ts = {
                    'end_date': b['end_dates'][j],
                    'start_date': b['start_dates'][j],
                    'value': b['values'][j],
                    }
                values_as_timeseries.append(ts)
            item_to_return[a]['values'] = values_as_timeseries
        return item_to_return


class NWSForecastIO(WebserviceLoader, BaseIO, TimeSeriesMapper):
    ###########################################
    # valid is the time of the forecast in UTC
    # primary is the stage in ft
    # secondary is the flow in kcfs
    # pedts is ???
    # It appears to return 3 days forecast in the future
    ###########################################
    start_date = DateOpt(ignored=True)
    end_date = DateOpt(ignored=True)
    state = FilterOpt(ignored=True)
    county = FilterOpt(ignored=True)
    station = FilterOpt(url_param='gage')
    parameter = FilterOpt(ignored=True)
    basin = FilterOpt(ignored=True)
    root_tag = None
    item_tag = None
    default_parameters = {
        'output': 'xml',
    }
    date_formats = [
        '%Y-%m-%dT%H:%M:%S-%z'
    ]
    url = 'http://water.weather.gov/ahps2/hydrograph_to_xml.php'

    def parse(self):
        doc = ET.parse(self.file)
        root = doc.getroot()
        if self.root_tag is None:
            self.root_tag = root.tag
        if self.item_tag is None:
            for l in list(root):
                if l.tag == 'forecast':
                    self.item_tag = l
        self.data = self.parse_item(self.item_tag)

    def parse_item(self, element):
        items = []
        for el in element:
            item = {
                'date': parser.parse(el.find('valid').text),
                el.find('primary').attrib['name']: el.find('primary').text,
                el.find('secondary').attrib['name']: el.find('secondary').text,
            }
            items.append(item)
        return items
