from wq.io import CsvNetIO, CsvFileIO
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from datetime import date
from datetime import timedelta


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
    end_date = ''
    inner_call = False
    next_date = ''
    start_row = 3
    all_data = {}
    
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
            'end_date': self.end_date,
            # 'data_wish': 'View+CSV+Data',
        }

    def refresh(self):
        super(CDECWaterIO, self).refresh()
        if not self.inner_call:
            for d in self.data:
                dt = '%s%s' % (str(d['date']), str(d['time']))
                self.all_data[dt] = d['value']
            #print "All: %s" % sorted(self.all_data)
            print 'All Data Date: %s' % sorted(self.all_data)[-2][:8]
            self.next_date = datetime.strptime(sorted(self.all_data)[-2][:8], '%Y%m%d')
            print "Next DAte: %s" % self.next_date    
            while not self.check_dates():
                self.add_more()
        # Revert data to array.
        data_container = []
        #for key, value in self.all_data.items():
        #    dlist = [key[:8], key[-4:], value]
        #    data_container.add(dlist)
        #self.data = data_container

    def add_more(self):
        start_date = datetime.strftime(self.next_date, '%m/%d/%Y')
        new_io = CDECWaterIO(
                station_id=self.station_id,
                sensor_num=self.sensor_num,
                dur_code=self.dur_code,
                start_date=start_date,
                end_date = self.end_date,
                inner_call = True
            )
        for row in new_io.data:
            dt = '%s%s' % (str(row['date']), str(row['time']))
            self.all_data[dt] = row['value']
        print 'Sorted last after add: %s' % sorted(self.all_data)[-2][:8]
        print 'New IO Date: %s' % new_io.data[-1]['date']
        self.next_date = datetime.strptime(sorted(self.all_data)[-2][:8], '%Y%m%d')
        print 'Next Date: %s' % self.next_date
        #self.all_data += allvalues

    def check_dates(self):
        print self.data[-1]['date']
        if self.end_date == 'Now':
            this_end_date = date.today()
        else:
            this_end_date = datetime.strptime(self.end_date, '%m/%d/%Y')
        this_end_date = datetime.strptime(datetime.strftime(this_end_date, '%Y-%m-%d'), '%Y-%m-%d')
        diff = this_end_date - self.next_date
        if diff.days > 1:
            return False
        else:
            return True


class ParamIO(CsvFileIO):
    debug = True
    filename = 'parameters.csv'
    field_names = ['id', 'sensor', 'pe_code', 'description', 'units']


class SiteMetaIO(object):
    station_code = ''  # 3-letter station code
    soup = ''
    baseurl = 'http://cdec.water.ca.gov/cgi-progs/'

    def __init__(self, station_code):
        self.station_code = station_code
        r = requests.get(self.baseurl + 'staMeta?station_id=' + self.station_code)
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

    @property
    def valid_param_dates(self):
        print self.station_code
        r = requests.get('%squeryCSV?station_id=%s' % (self.baseurl, self.station_code))
        soup = BeautifulSoup(r.text)
        parameters_for_station = {}
        for row in soup.table.find_all('tr'):
            parameter = row.find_all('td')[0].text
            duration = str(row.find_all('td')[-2].text)[2:3]
            date_range = row.find_all('td')[-1].text
            if str(date_range)[0:6] == ' From ':
                date_range = str(date_range)[6:]
                if str(date_range)[-12:] == ' to present.':
                    date_range = str(date_range)[:-12]
                    start_date = datetime.strptime(date_range, '%m/%d/%Y %H:%M')
                    start_date = datetime.strftime(start_date, '%m/%d/%Y')
                    end_date = 'Now'
                else:
                    start_date = datetime.strptime(str(date_range)[:16], '%m/%d/%Y %H:%M')
                    start_date = datetime.strftime(start_date, '%m/%d/%Y')
                    end_date = datetime.strptime(str(date_range)[-17:-1], '%m/%d/%Y %H:%M')
                    end_date = datetime.strftime(end_date, '%m/%d/%Y')
            else:
                raise Exception('There was an error parsing the date: %s' % (soup))
            parameters_for_station["%s%s" % (parameter, duration)] = [parameter, duration, start_date, end_date]
        return parameters_for_station
