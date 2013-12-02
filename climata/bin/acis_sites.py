#!/usr/bin/env python
import sys
from datetime import date
from climata.acis import StationMetaIO, ELEMENT_BY_NAME, ELEMENT_BY_ID

elems = ELEMENT_BY_NAME.copy()

# Eloement 7 (pan evap) does not have a name, copy from ID listing
elems['7'] = ELEMENT_BY_ID['7']


def load_sites(*basin_ids):
    """
    Load metadata for all sites in given basin codes.
    """

    # Resolve basin ids to HUC8s if needed
    basins = []
    for basin in basin_ids:
        if basin.isdigit() and len(basin) == 8:
            basins.push(basin)
        else:
            from climata.huc8 import get_huc8
            basins.extend(get_huc8(basin))

    # Load sites with data since 1900
    sites = StationMetaIO(
        basin=basins,
        elems=elems.keys(),
        sdate='1900-01-01',
        edate=date.today(),
    )

    # Load all sites (to get sites without data)
    seen_sites = [site.uid for site in sites]
    nodata_sites = [
        site for site in StationMetaIO(basin=basins)
        if site.uid not in seen_sites
    ]

    # Determine the following from the site lists:
    seen_auths = set()  # Which authority codes are actually used by any site
    seen_elems = set()  # Which elems actually have data in any site
    ranges = {}  # The overall period of record for each site
    for site in sites:

        for auth in site.sids.keys():
            seen_auths.add(auth)

        start, end = None, None
        for elem in site.valid_daterange:
            s, e = site.valid_daterange[elem]
            seen_elems.add(elem)
            if s is None or e is None:
                continue
            if start is None or s < start:
                start = s
            if end is None or e > end:
                end = e
        ranges[site.uid] = [start, end]

    # Check for authority codes that might not be in sites with data
    for site in nodata_sites:
        for auth in site.sids.keys():
            seen_auths.add(auth)

    # Print CSV headers (FIXME: use CsvFileIO for this?)
    seen_auths = sorted(seen_auths)
    seen_elems = sorted(seen_elems)
    print ",".join(
        ['ACIS uid', 'name']
        + seen_auths
        + ['latitude', 'longitude', 'start', 'end', 'years']
        + [elems[elem]['desc'] for elem in seen_elems]
    )

    # Print sites with data
    for site in sites:

        # Determine if elems are available for entire period or shorter range
        start, end = ranges[site.uid]
        if start and end:
            years = end.year - start.year + 1
        elem_ranges = []
        for elem in seen_elems:
            estart, eend = site.valid_daterange[elem]
            if estart is None:
                erange = ""
            elif estart == start and eend == end:
                erange = "period"
            else:
                erange = "%s to %s" % (estart.date(), eend.date())
            elem_ranges.append(erange)

        # Output CSV row
        print ",".join(map(str,
            [site.uid, site.name]
            + [site.sids.get(auth, "") for auth in seen_auths]
            + [site.ll[1], site.ll[0]]
            + [start.date(), end.date(), years]
            + elem_ranges
        ))

    # Print CSV rows for sites without data
    for site in nodata_sites:
        print ",".join(map(str,
            [site.uid, site.name]
            + [site.sids.get(auth, "") for auth in seen_auths]
            + [site.ll[1], site.ll[0]]
            + ["NO DATA"]
        ))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: acis_sites.py basin"
        exit()
    load_sites(*sys.argv[1:])
