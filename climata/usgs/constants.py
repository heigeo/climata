data_type_cd = {
    'all': 'default',
    'iv': 'instantaneous Values',
    'ut': 'Unit Values',
    'rt': 'Real Time Values',
    'dv': 'Daily Values',
    'pk': 'Peak Measurements',
    'sv': 'Site Visits',
    'gw': 'Groundwater Levels',
    'qw': 'Water Quality Data',
    'id': 'Historical Instantaneous Values',
    'aw': 'Sites Monitored by the Active Groundwater Network',
    'ad': 'Sites included in Annual Water Data Reports',
}

summary_header_fields = (
    'Agency',
    'Site Number',
    'Site Name',
    'Site Type',
    'Latitude',
    'Longitude',
    'Lat-Long Accuracy',
    'Lat-Long Datum',
    'Gage/Land Surface Altitude',
    'Altitude Accuracy',
    'Altitude Datum',
    'Data Type Code',
    'Parameter Code',
    'Statistics Code',
    'dd_nu',
    'loc_web_ds',
    'Medium Group Code',
    'Parameter Group Code',
    'Substance Registry Service ID',
    'Access Code',
    'Begin Date',
    'End Date',
    'Number of Records',
    )
'''
    sites.field_names[0] = 'Agency' #agency_cd
    sites.field_names[1] = 'Site Number' #site_no
    sites.field_names[2] = 'Site Name' #station_nm
    sites.field_names[3] = 'Site Type' #site_tp_cd
    sites.field_names[4] = 'Latitude' #dec_lat_va
    sites.field_names[5] = 'Longitude' #dec_long_va
    sites.field_names[6] = 'Lat-Long Accuracy' #coord_acy_cd
    sites.field_names[7] = 'Decimal Lat-Long Datum' #dec_coord_datum_cd
    sites.field_names[8] = 'Altitude of Gage/land surface' #alt_va
    sites.field_names[9] = 'Altitude Accuracy' #alt_acy_va
    sites.field_names[10] = 'Altitude Datum' #alt_datum_cd
    sites.field_names[11] = 'Data Type Code' #data_type_cd = This is the data_type_cd field that needs to be swapped out.
    sites.field_names[12] = 'Parameter Code' #'parm_cd' #USGS parameter code from fixed_parms_query.txt
    sites.field_names[13] = 'Statistics Code' #stat_cd http://help.waterdata.usgs.gov/stat_code
    ### This following section is part of the period of record data
    sites.field_names[14] = 'dd_nu' #dd_nu No idea what this field means
    sites.field_names[15] = 'loc_web_ds' #loc_web_ds This field has no data in any of the test data columns
    sites.field_names[16] = 'Medium Group Code' #medium_grp_cd Don't know what this means.
    sites.field_names[17] = 'Parameter Group Code' #parm_grp_cd
    ### End permit of record data unknowns
    sites.field_names[18] = 'Substance Registry Service ID' #srs_id
    sites.field_names[19] = 'Access Code' #access_cd
    sites.field_names[20] = 'Begin Date' #begin_date
    sites.field_names[21] = 'End Date' #end_date
    sites.field_names[22] = 'Number of Records' #count_nu
    '''
    
    #