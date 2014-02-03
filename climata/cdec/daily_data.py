from __init__ import CDECWaterIO, CDECMetaIO
import os, sys
import requests
from bs4 import BeautifulSoup

dur_codes = ['M', 'H', 'D', 'E']
codes_for_stations = {}
for station in CDECMetaIO(filename='cdec_klamath_stations.csv'):
    codes_for_stations[station.station_code] = SiteMetaIO(station.station_code).valid_param_dates
    '''
    # This is the actual list of stations put out by the meta_io
    r = requests.get('http://cdec.water.ca.gov/cgi-progs/queryCSV?station_id=%s' % station.station_code)
    soup = BeautifulSoup(r.text)
    fonts = soup.find_all('font')
    parameters_for_station = []
    skip_first = 0
    for font in fonts:
        if skip_first != 0:
            for f in font.contents:
                parameters_for_station.append(f)
        else:
            skip_first = 1
    codes_for_stations[station.station_code] = parameters_for_station
    '''    
for code, parameters in codes_for_stations.values():
    print ','.join(code)
    
start_dates = {
    'M': '1950-01-01',
    'H': '2013-01-01',
    'D': '2000-01-01',
    'E': '2013-12-01',
}

for station in codes_for_stations.values:
    for sensor in code_list:
        for dur in dur_codes:
            station_data = CDECWaterIO(
                station_id=station,
                sensor_num=sensor,
                dur_code=dur,
                start_date=start_dates[dur]
            )
            filename = 'output/%s/%s_%s.csv' % (dur, station, sensor)
            f = open(filename, 'w+')
            sys.stdout.write('output/%s/%s_%s.csv' % (dur, station, sensor) + '\n')
            f.write(','.join(station_data.field_names))
            sys.stdout.write(','.join(station_data.field_names) + '\n')
            f.write('\n')
            try:
                for data in station_data:
                    try:
                        sys.stdout.write(str(data.date) + ',' + str(data.time) + ',' + str(data.value) + '\n')  
                        f.write(str(data.date) + ',' + str(data.time) + ',' + str(data.value))
                    except:
                        continue
                    f.write('\n')
            except:
                continue
            f.close()

'''
for root, dirs, filenames in os.walk('/var/www/klamath/db/loaddata/climata/climata/cdec/output/'):
    for f in filenames:
        if os.path.getsize(f) == 900:
            os.remove(f)
        elif os.path.getsize(f) == 43:
            os.remove(f)
'''