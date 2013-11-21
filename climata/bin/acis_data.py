#!/usr/bin/env python
from climata.acis import StationMetaIO, StationDataIO, ELEMENT_BY_NAME
from climata.util import parse_date
import sys
from datetime import date, timedelta

curyear = date.today().year
one_day = timedelta(days=1)


def load_data(basin, elem, syear=1950, eyear=curyear,
              inactive=False, years=30):
    syear = int(syear)
    eyear = int(eyear)
    inactive = bool(inactive)
    years = int(years)
    if not basin.isdigit() or len(basin) != 8:
        from climata.huc8 import get_huc8
        basin = get_huc8(basin)

    sites = StationMetaIO(
        basin=basin,
        sdate='%s-01-01' % syear,
        edate='%s-12-31' % eyear,
        elems=elem,
    )
    include_sites = []
    seen_auths = set()
    for site in sites:
        start, end = site.valid_daterange[elem]
        exclude = False
        if end.year < eyear - years and not inactive:
            sys.stderr.write("Site not active: %s (last %s)" % (
                site.name, end.date()
            ))
            sys.stderr.write("\n")
            exclude = True
        elif end.year - start.year + 1 < years:
            sys.stderr.write("Not enough data: %s (%s years)" % (
                site.name, end.year - start.year
            ))
            sys.stderr.write("\n")
            exclude = True

        if exclude:
            continue
        include_sites.append(site)
        for auth in site.sids.keys():
            seen_auths.add(auth)

    # Sort sites by longitude
    include_sites = sorted(include_sites, key=lambda s: s.ll[0])
    seen_auths = sorted(seen_auths)

    def get_val(site, field):
        if hasattr(site, field):
            return getattr(site, field)
        elif field == "latitude":
            return site.ll[1]
        elif field == "longitude":
            return site.ll[0]
        else:
            return site.sids.get(field, "")

    def header(field):
        vals = [get_val(site, field) for site in include_sites]
        sys.stdout.write(",".join([field + ":"] + map(str, vals)))
        sys.stdout.write("\n")

    header("name")
    for auth in seen_auths:
        header(auth)
    header("latitude")
    header("longitude")

    for year in range(syear, eyear + 1):
        load_year_data(basin, elem, year, include_sites)


def load_year_data(basin, elem, year, include_sites):
    sys.stderr.write("Loading %s data...\n" % year)
    sdate = parse_date('%s-01-01' % year).date()
    edate = parse_date('%s-12-31' % year).date()
    sitedata = StationDataIO(
        basin=basin,
        sdate=sdate,
        edate=edate,
        elems=elem,
    )
    sitedata = {site.uid: site for site in sitedata}
    dates = {}
    date = sdate
    while date <= edate:
        dates[date] = {}
        date += one_day

    for site in include_sites:
        if site.uid not in sitedata:
            continue
        data = sitedata[site.uid].data
        for row in data:
            dates[row.date][site.uid] = getattr(row, elem)

    date = sdate
    while date <= edate:
        data = map(str, [
            dates[date].get(site.uid, "")
            for site in include_sites
        ])
        sys.stdout.write(",".join([str(date)] + data))
        sys.stdout.write("\n")
        date += one_day


def usage():
    sys.stderr.write("""
Usage: acis_data.py basin elem [syear] [eyear] [inact] [years]

 basin:\tbasin(s) (HUC8, required)
 elem:\telement code (required, see below)
 syear:\tStart year (default 1950)
 eyear:\tEnd year (default %s)
 inact:\tInclude inactive sites (default false)
 years:\tOnly include sites with this many years of data (default 30)

Inactive sites are considered to be sites that have not had any data for n
years, where n is the same as the years argument.

Available elem codes:
""" % curyear)

    for elem in sorted(ELEMENT_BY_NAME.keys()):
        sys.stderr.write(" %s:\t%s\n" % (elem, ELEMENT_BY_NAME[elem]['desc']))
    exit()

if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[2] not in ELEMENT_BY_NAME:
        usage()
        exit()
    load_data(*sys.argv[1:])
