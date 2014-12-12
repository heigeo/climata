# -*- coding: utf-8 -*-

# Constants as specified in http://data.rcc-acis.org/doc/


# Authority Codes
# http://data.rcc-acis.org/doc/#title2
AUTHORITIES = [
    ('1', "WBAN", "Weather Bureau Army Navy"),
    ('2', "COOP", "Cooperative Observer Network"),
    ('3', "FAA", "Federal Aviation Administration"),
    ('4', "WMO", "World Meteorological Organization"),
    ('5', "ICAO", "International Civil Aviation Organization"),
    ('6', "GHCN", "Global Historical Climate Network"),
    ('7', "NWSLI", "National Weather Service Location Identifier"),
    ('8', "RCC", "Regional Climate Centers"),
    ('9', "ThreadEx", "NOAA ThreadEx"),
    ('10', "CoCoRaHS", "Community Collaborative Rain, Hail and Snow Network"),
]

AUTHORITY_BY_ID = {
    id: {
        'id': id,
        'name': name,
        'desc': desc
    } for id, name, desc in AUTHORITIES
}

AUTHORITY_BY_NAME = {
    auth['name']: auth
    for auth in list(AUTHORITY_BY_ID.values())
}

# Element Codes
# http://data.rcc-acis.org/doc/#title5
ELEMENTS = (
    ('1', "maxt", "Maximum temperature (°F)"),
    ('2', "mint", "Minimum temperature (°F)"),
    ('43', "avgt", "Average temperature (°F)"),
    ('3', "obst", "Obs time temperature (°F)"),
    ('4', "pcpn", "Precipitation (inches)"),
    ('10', "snow", "Snowfall (inches)"),
    ('11', "snwd", "Snow depth (inches)"),
    ('7', None, "Pan evap (inches)"),
    ('44', "cdd", "Degree days above base (CDD) (default base 65)"),
    ('45', "hdd", "Degree days below base (HDD) (default base 65)"),
    (None, "gdd", "Growing Degree Days (base 50)")
)

ELEMENT_BY_ID = {
    id: {
        'id': id,
        'name': name,
        'desc': desc
    } for id, name, desc in ELEMENTS if id is not None
}

ELEMENT_BY_NAME = {
    name: {
        'id': id,
        'name': name,
        'desc': desc
    } for id, name, desc in ELEMENTS if name is not None
}

# Metadata fields
# http://www.rcc-acis.org/docs_webservices.html#title4
DEFAULT_META_FIELDS = (
    'name',  # Station name
    'state',  # 2-letter state
    'sids',  # Station ids (with Authority codes)
    'll',  # Long, Lat
    'elev',  # Elevation
    'uid',  # Unique ACIS id
    'county',  # County (FIPS) code
    'climdiv',  # Climate division code
)

ALL_META_FIELDS = DEFAULT_META_FIELDS + (
    # Period of record (by parameter code, which is effectively required)
    'valid_daterange',
)

# Additional flags for individual values
# http://www.rcc-acis.org/docs_webservices.html#title13
ADD_IDS = (
    'f',  # Flags,
    't',  # Time of observation
    'i',  # Station ID assoc. w/data
    'v',  # Var minor
    'n',  # Network
)
