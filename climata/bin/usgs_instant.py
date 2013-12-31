import sys
import csv
import os
import datetime
from climata.usgs.constants import *  # data_type_cd, summary_header_fields
from climata.usgs import *
from dateutil.parser import *

today = datetime.strftime(datetime.today(), '%Y-%m-%d')


def data_to_csv(headers, dates, current_filename, instant=False):
    f = open(current_filename+'.csv', 'w')
    # Prints off headers
    def write_header(variable):
        f.write('"",')
        for row in headers:
            f.write('"' + str(headers[row][variable]) + '",')
        f.write("\n")    
    
    write_header('siteName')
    write_header('siteCode')
    write_header('siteType')
    write_header('latitude')
    write_header('longitude')
    if(instant):
        write_header('site')
        write_header('param')
    write_header('unit')
    
    # Prints out rows. 
    
    for date in sorted(dates):
        f.write('"' + date + '",')
        for row in headers:
            try: 
                f.write('"' + dates[date][row] + '",')
            except:
                f.write('"",')
        f.write("\n")
    f.close()
    

def load_instant_data(basin, start_date='2013-09-01', end_date=today, parameterCd=None):
    def instant_values(site_id):
        sites = InstantValuesIO(
            sites=site_id,
            debug=False,
        )
        dates = {}
        headers = {}
        
        for site in sites:
            code = site.sourceinfo['siteProperty'][0]['value']
            unit = site.variable['unit']['unitAbbreviation']
            site_code = site.sourceinfo['siteCode'][0]['value']
            param = site.variable['variableCode'][0]['value']
            if (param not in headers):
                headers[param] = {}
            headers[param] = {
                'siteName':site.sourceinfo['siteName'],
                'site':site.variable['variableDescription'],
                'siteType':site_types[code],
                'siteCode':site_code,
                'param':param,
                'latitude':site.sourceinfo['geoLocation']['geogLocation']['latitude'],
                'longitude':site.sourceinfo['geoLocation']['geogLocation']['longitude'],
                'unit':unit
            }
            for si in site.values:
                for s in si['value']:
                    # get all dates and add them to a dict
                    current_date = datetime.strftime(parse(s['dateTime']), "%Y-%m-%d %H:%M")
                    if (current_date not in dates):
                        dates[current_date] = {}
                    dates[current_date][param] = s['value']
                                    
        if not os.path.exists('../scripts/output/'+str(basin)):
            os.makedirs('../scripts/output/'+str(basin))
        current_filename = '../scripts/output/'+str(basin)+'/usgs_instant_data_'+str(site_id)+'_'+str(start_date)+'-'+str(end_date)
        data_to_csv(headers, dates, current_filename, instant=True)
    
    site_ids = SitesForHucIO(basin=basin)
    for site_id in site_ids:
        instant_values(site_id.sourceinfo['siteCode'][0]['value'])
    
