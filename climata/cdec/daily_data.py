from __init__ import CDECWaterIO, CDECMetaIO
import os, sys
import requests
from bs4 import BeautifulSoup

dur_codes = ['M', 'H', 'D', 'E']
'''
station_codes = {
    'CLK':'Clear Lake', # No Real Time Single Station DAta
    'LRS':'Lost River', 
    'KLF': 'KLAMATH FALLS 2 SSW (KLAMATH R)', # 
    'KMN': 'KLAMATH NWR (KLAMATH R)',  # http://cdec.water.ca.gov/cgi-progs/queryF?s=KMN&d=28-Jan-2014+19:55&span=10000hours
    'KLI': 'KLAMATH R AT IRON GATE (KLAMATH R)',
    'KLO': 'KLAMATH R AT ORLEANS (KLAMATH R)',
    'KWP': 'KLAMATH R BL WEITCHPEC (KLAMATH R)',
    'KIW': 'KLAMATH R BLW IRON GATE (WATER QUALITY) (KLAMATH R)',
    'TUR': 'KLAMATH R NR KLAMATH (TURWAR CREEK) (KLAMATH R)',  # http://cdec.water.ca.gov/cgi-progs/queryF?s=TUR&d=28-Jan-2014+19:55&span=10000hours
    'KSW': 'KLAMATH R NR SEIAD VLY (WATER QUALITY) (KLAMATH R)',
    'KKY': 'KLAMATH R. NR KLAMATH-WATER QUALITY (KLAMATH R)',
    'OLS': 'KLAMATH RIVER AT ORLEANS (KLAMATH R)',  # http://cdec.water.ca.gov/cgi-progs/queryF?s=OLS&d=28-Jan-2014+19:55&span=10000hours
    'KIG': 'KLAMATH RIVER BELOW IRON GATE DAM (KLAMATH R)',
    'KNK': 'KLAMATH RIVER NEAR KLAMATH (KLAMATH R)',  # http://cdec.water.ca.gov/cgi-progs/queryF?s=KNK&d=28-Jan-2014+19:55&span=10000hours
    'KSV': 'KLAMATH RIVER NEAR SEIAD VALLEY (KLAMATH R)',  # http://cdec.water.ca.gov/cgi-progs/queryF?s=KSV&d=28-Jan-2014+19:55&span=10000hours
    'LKL': 'LOWER KLAMATH NWR (KLAMATH R)',  # http://cdec.water.ca.gov/cgi-progs/queryF?sLKL&d=28-Jan-2014+19:55&span=10000hours
    'KLM': 'UPPER KLAMATH (KLAMATH R)',
}   
codes_for_stations = {
    'CLK': ['7', '15'],
    'LRS': ['1', '6', '14'],
    'KLF': ['2'],
    'KMN': ['2', '4', '9', '10', '11', '12', '13', '14', '26', '77', '78'],
    'KLI': ['66', '67'],
    'KLO': ['65', '66', '72'],
    'KWP': ['25', '61', '62', '100'],
    'KIW': ['2', '4', '5', '25', '61', '62'],
    'TUR': ['1', '14', '16', '20', '41'],
    'KSW': ['4', '5', '25', '61', '62'],
    'KKY': ['25', '61', '62', '100'],
    'OLS': ['1', '2', '14', '16', '20', '41', '45', '169'],
    'KIG': ['1', '5', '14', '20', '62', '115', '146'],
    'KNK': ['1', '14', '20', '25', '41', '169'],
    'KSV': ['1', '14', '20', '169'],
    'LKL': ['2', '4', '9', '10', '11', '12', '13', '14', '26', '77', '78'],
    'KLM': ['15'],
}
'''
codes_for_stations = {}
for station in CDECMetaIO(filename='cdec_klamath_stations.csv'):
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
    
for code in codes_for_stations.values():
    print ','.join(code)
    
start_dates = {
    'M': '1950-01-01',
    'H': '2013-01-01',
    'D': '2000-01-01',
    'E': '2013-12-01',
}

for station, code_list in codes_for_stations.items():
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