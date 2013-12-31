#!/usr/bin/env python
from climata.usgs import USGSIO
import sys
import csv
from datetime import date, timedelta
from climata.usgs.constants import *  # data_type_cd, summary_header_fields
from climata.usgs import *


def load_data(basin):
    sites = USGSIO(
        basin=basin,
    )

    parms = ParamIO()

    sys.stdout.write('"'+'","'.join(summary_header_fields)+'"')
    sys.stdout.write("\n")
    for row in sites:
        parameter_code = [row.parm_cd]
        if row.agency_cd != 'USGS':  # This skips the first row
            pass
        else:
            if row.data_type_cd in data_type_cd:
                dtc = data_type_cd[row.data_type_cd]
            else:
                dtc = row.data_type_cd
            if (row.parm_cd == '' or row.parm_cd == '00000'
                    or row.parm_cd == 0 or row.parm_cd is None):
                prmc = 'N/A'
            else:
                pc = row.parm_cd
                prmc = parms[pc].group + ':' + parms[pc].parm_nm
            rowprint = (
                row.agency_cd,
                row.site_no,
                row.station_nm,
                row.site_tp_cd,
                row.dec_lat_va,
                row.dec_long_va,
                row.coord_acy_cd,
                row.dec_coord_datum_cd,
                row.alt_va,
                row.alt_acy_va,
                row.alt_datum_cd,
                dtc,
                prmc,
                row.stat_cd,
                row.dd_nu,
                row.loc_web_ds,
                row.medium_grp_cd,
                row.parm_grp_cd,
                row.srs_id,
                row.access_cd,
                row.begin_date,
                row.end_date,
                row.count_nu,
            )
            sys.stdout.write('"' + '","'.join(rowprint) + '"')
            sys.stdout.write("\n")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        load_data(*sys.argv[1:])
        exit()
    load_data(*sys.argv[1:])
