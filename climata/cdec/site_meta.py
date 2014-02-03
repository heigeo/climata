from __init__ import CDECMetaIO, ParamIO
from wq.io.gis import ShapeIO, GisIO
from shapely.geometry import Point
from shapely.ops import cascaded_union
from bs4 import BeautifulSoup
import requests
import sys
import os
###########################
# Getting basins into an IO
###########################
basins = ShapeIO(filename='/var/www/klamath/db/loaddata/scripts/data/basins.shp')
klamath = cascaded_union([basin.geometry for basin in basins.values()])

###########################
# Filter all stations by coords
###########################
cdec_stations = {}
for station in CDECMetaIO():
        long = -float(station.long)
        lat = float(station.lat)
        loc = Point(long, lat)
        if klamath.contains(loc):
            cdec_stations[station.station_code] = station
            print loc

f = open('cdec_klamath_stations.csv', 'w+')
for station in cdec_stations.values():
    f.write(",".join(station))
    f.write('\n')
f.close()

##############################################################
# Gets valid parameters for each site and puts them in a dict
##############################################################
codes_for_stations = {}
all_station_codes = []
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
                if f not in parameters_for_station:
                    parameters_for_station.append(f)
                if f not in all_station_codes:
                    all_station_codes.append(f)
        else:
            skip_first = 1
    codes_for_stations[station.station_code] = parameters_for_station

######################################################
# Sorts all parameter codes into another dict
######################################################
sorted_station_codes = []
for code in all_station_codes:
    sorted_station_codes.append(int(code))
sorted_station_codes.sort()

####################################
# Adds parameters to the header row
####################################
headers_with_parameters = ['Station Code', 'Url', 'Description', 'No Of Records', 'Lat', 'Long']
for param in sorted_station_codes:
    if param not in headers_with_parameters:
        headers_with_parameters.append(param)

###################
# Get Parameter Definitions
###################
for n, l in enumerate(headers_with_parameters):
    for prm in ParamIO():
        if str(l) == str(prm.id):
            headers_with_parameters[n] = '"' + prm.description + '(' + prm.units + ')"'

#############################
# Get period of record info for each parameter using
# prm.description of the IO
# From http://cdec.water.ca.gov/cgi-progs.staMeta?station_id=XXX
# Use the BeautifulSoup library to get the data.
# The SENSOR DESCRIPTION (first column) is always Bold.
#############################


###########################################################
# Writes parameters to the file
# Then writes the sites with parameters for those that exist
############################################################
f = open('cdec_klamath_station_meta.csv', 'w+')
f.write(','.join(str(h) for h in headers_with_parameters))
f.write('\n')
for station in CDECMetaIO(filename='cdec_klamath_stations.csv'):
    station_string = ','.join(station)
    for val in sorted_station_codes:
        if str(val) in codes_for_stations[station.station_code]:
            station_string += ',X'
        else:
            station_string += ','
    f.write(station_string)
    f.write('\n')
f.close()