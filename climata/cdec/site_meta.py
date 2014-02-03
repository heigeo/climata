from __init__ import CDECMetaIO, ParamIO, SiteMetaIO
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
bsns = ShapeIO(filename='/var/www/klamath/db/loaddata/scripts/data/basins.shp')
klamath = cascaded_union([basin.geometry for basin in bsns.values()])

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
all_station_parameters = set()
parameters_for_stations = {}
for station in CDECMetaIO(filename="cdec_klamath_stations.csv"):
    site = SiteMetaIO(station.station_code)
    site_params = {}
    for parameter, date_range in site.parameters.items():
        all_station_parameters.add(parameter)
        site_params[parameter] = date_range
    parameters_for_stations[station.station_code] = site_params

headers_with_parameters = [
    'Station Code',
    'Url',
    'Description',
    'No Of Records',
    'Lat',
    'Long'
    ]

###########################################################
# Writes parameters to the file
# Then writes the sites with parameters for those that exist
############################################################
f = open('cdec_klamath_station_meta.csv', 'w+')
f.write('"' + '","'.join(str(h) for h in headers_with_parameters) + '"')
f.write(',')
f.write('"' + '","'.join(str(h) for h in all_station_parameters) + '"')
f.write('\n')
for station in CDECMetaIO(filename='cdec_klamath_stations.csv'):
    tpr = ','.join(station)
    for parameter in all_station_parameters:
        tpr += ',"'
        if parameter in parameters_for_stations[station.station_code]:
            tpr += parameters_for_stations[station.station_code][parameter]
        tpr += '"'
    f.write(station_string)
    f.write('\n')
f.close()
