#!/usr/bin/env python
from __init__ import *
from datetime import datetime
import sys

def load_station_meta(**kwargs):
    sites = site_list(hucs='180102')
    station_meta_dict = {}
    site_keys = set([])
    station_element_values = {}
    station_element_keys = set([])
    for site in sites:
        meta = station_meta(site=site)
        station_meta_dict[site] = meta
        elements = station_elements(station=site)
        station_element_values[site] = elements
        
    for elements in station_element_values.values():
        for element in elements:
            try:
                station_element_keys.add('%s - %s' % (element.elementCd, element.duration))
            except:
                pass # station_element_keys.add('%s - %s' % (elements.elementCd, elements.duration))
        '''
         The station_meta_dict can be accessed as follows:
         station_meta_dict['stationTriplet'].property
        '''
    
    for keys in station_meta_dict.items():
        for key in keys[1]._keys():
            if key not in site_keys:
                site_keys.add(key)
    sys.stdout.write(','.join(sorted(site_keys)))
    sys.stdout.write(',')
    sys.stdout.write(','.join(sorted(station_element_keys)))
    sys.stdout.write('\n')
    for station in station_meta_dict.values():
        for key in sorted(site_keys):
            if key in station._keys():
                sys.stdout.write('"' + station[key] + '",')
            else:
                sys.stdout.write(",")
        # Station Measurement Data
        for elkey in sorted(station_element_keys):
            found = False
            for elstation in station_element_values[station.stationTriplet]:
                try:
                    if elkey == '%s - %s' % (elstation.elementCd, elstation.duration):
                        found = True
                        beginDate = datetime.strftime(datetime.strptime(elstation.beginDate, '%Y-%m-%d %H:%M:%S'), "%Y/%m/%d")
                        endDate = datetime.strftime(datetime.strptime(elstation.endDate, '%Y-%m-%d %H:%M:%S'), "%Y/%m/%d")
                        if endDate == '2100/01/01':
                            endDate = 'Present'
                        sys.stdout.write(beginDate + '-' + endDate + ',')
                except:
                    pass
            if not found:
                sys.stdout.write(',')
        sys.stdout.write('\n')
    '''
     This was a good idea for using in site headers
        names = []
        latitudes = []
        longitudes = []
        counties = []
        elevations = []
        hucs = []
        huds = []
        triplets = []
            # THEN LOOP THEN:
            names.append(station.name)
            latitudes.append(station.latitude)
            longitudes.append(station.longitude)
            counties.append(station.countyName)
            elevations.append(station.elevation)
            hucs.append(station.huc)
            huds.append(station.hud)
            triplets.append(station.stationTriplet)
            
        sys.stdout.write(','.join(names))
        sys.stdout.write('\n')
        sys.stdout.write(','.join(triplets))
        sys.stdout.write('\n')
        sys.stdout.write(','.join(hucs))
        sys.stdout.write('\n')
        sys.stdout.write(','.join(huds))
        sys.stdout.write('\n')
        sys.stdout.write(','.join(elevations))
        sys.stdout.write('\n')
        sys.stdout.write(','.join(latitudes))
        sys.stdout.write('\n')
        sys.stdout.write(','.join(longitudes))
        sys.stdout.write('\n')
    '''
    
if __name__ == "__main__":
    load_station_meta(*sys.argv[1:])