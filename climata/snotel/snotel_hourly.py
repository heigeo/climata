#!/usr/bin/env python
from __init__ import *
import sys
from datetime import datetime

def load_hourly_data(**kwargs):
    sites = site_list(hucs='180102')
    site_element_list = {}
    all_elements_in_range = set([])
    for site in sites:
        slist = set([])
        for li in station_elements(site):
            try:
                if li.duration == 'DAILY':
                    slist.add(li.elementCd)
                    all_elements_in_range.add(li.elementCd)
            except:
                pass
        site_element_list[site] = slist
    
    for element in all_elements_in_range:
        element_sites = set([])
        for key, value in site_element_list.items():
            if element in value:
                element_sites.add(key)
    
    for site, elements in site_element_list.items():
        for element in elements:
            # sitelist.add(get_daily_for_site_and_element(site, element))
            f = open('csv/hourly_values_%s_%s.csv' % (site.replace(':', '-'), element), 'w+')
            f.write("site: %s, flag, element: %s" %(site, element))
            f.write('\n')
            f.write('date, flag, value')
            f.write('\n')
            data = get_hourly_data(site, element, '2005-01-01')
            try:
                for value in data.values:
                    f.write(','.join(value))
                    f.write('\n')
                f.close()
            except:
                pass

if __name__ == '__main__':
    load_hourly_data(*sys.argv[1:])