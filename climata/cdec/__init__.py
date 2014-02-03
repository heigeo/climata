from wq.io import CsvNetIO, CsvFileIO
from bs4 import BeautifulSoup
import requests


class CDECMetaIO(CsvFileIO):
    debug = True
    quotechar = "'"
    filename = 'cdec_stations.csv'
    field_names = [
        'station_code',
        'url',
        'description',
        'no_of_records',
        'lat',
        'long'
        ]
    ########################################################
    # url = 'http://cdec.water.ca.gov/misc/all_stations.csv'
    # If CDEC can fix their document, we can use the netio
    ########################################################


class CDECWaterIO(CsvNetIO):
    station_id = ''
    sensor_num = ''
    dur_code = ''
    debug = True
    field_names = ['date', 'time', 'value']
    start_date = ''

    @property
    def url(self):
        return 'http://cdec.water.ca.gov/cgi-progs/queryCSV' % self.params

    @property
    def params(self):
        return {
            'station_id': self.station_id,
            'sensor_num': self.sensor_num,
            'dur_code': self.dur_code,
            'start_date': self.start_date,
            'end_date': 'Now',
            # 'data_wish': 'View+CSV+Data',
        }


class ParamIO(CsvFileIO):
    debug = True
    filename = 'parameters.csv'
    field_names = ['id', 'sensor', 'pe_code', 'description', 'units']


class SiteMetaIO(object):
    station_code = ''  # 3-letter station code
    soup = ''
    baseurl = 'http://cdec.water.ca.gov/cgi-progs/staMeta?station_id='

    def __init__(self, station_code):
        r = requests.get(self.baseurl + station_code)
        self.soup = BeautifulSoup(r.text)

    @property
    def parameters(self):
        sensors = {}
        table_one = str(self.soup.find_all('table')[1].find_all('th')[0].text)
        if table_one == 'Sensor Description':
            rows = self.soup.find_all('table')[1].find_all('tr')
        else:
            rows = self.soup.find_all('table')[2].find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            sensors[str(cells[0].text)] = str(cells[4].text)
        return sensors

    @property
    def elevation(self):
        return self.soup.table.find_all('td')[3]
