from wq.io import CsvNetIO
from collections import OrderedDict


class CountyIO(CsvNetIO):
    url = "http://www.census.gov/geo/reference/codes/files/national_county.txt"


counties = OrderedDict(sorted([
    (c.stateansi + c.countyansi, c)
    for c in CountyIO()
]))


def state_counties(state):
    result = OrderedDict()
    for fips, county in counties.items():
        if county.stateansi == state or county.state == state:
            result[fips] = county
    return result
