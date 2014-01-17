#!/usr/bin/env python
from __init__ import *
import sys
from datetime import datetime


def load_daily_data(**kwargs):
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
        stels = station_elements(site)
        for element in elements:
            stDate = get_start_date(stels, element)
            # sitelist.add(get_daily_for_site_and_element(site, element))
            f = open('csv/daily_values_%s_%s.csv' % (site, element), 'w+')
            f.write("site: %s, element: %s" %(site, element))
            f.write('\n')
            f.write('date,value')
            f.write('\n')
            data = get_daily_data(site, element, stDate)
            try:
                startDate = datetime.strptime(data.beginDate, '%Y-%m-%d %H:%M:%S')
                endDate = data.endDate
                dateCounter = 0
                for value in data.values:
                    f.write('%s,' % (startDate + timedelta(days=dateCounter)))
                    dateCounter = dateCounter + 1
                    if value is None:
                        f.write('0')
                    else:
                        f.write(value)
                    f.write('\n')
                f.close()
            except:
                pass

def get_start_date(stels, element):
    for el in stels:
        if el.elementCd == element:
            return datetime.strftime(datetime.strptime(el.beginDate, '%Y-%m-%d %H:%M:%S'), "%Y-%m-%d")

if __name__ == '__main__':
    load_daily_data(*sys.argv[1:])