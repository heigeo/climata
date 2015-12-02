from wq.io import NetLoader, TupleMapper, BaseIO
from climata.base import WebserviceLoader, FilterOpt, DateOpt, ChoiceOpt
from climata.parsers import RdbParser, WaterMlParser
from .constants import SITE_TYPES


# Base/mixin classes (not meant to be called directly)

class NwisLoader(WebserviceLoader):
    """
    Base class for loading data from the USGS NWIS REST services.
    """

    # Map WebserviceLoader options to NWIS equivalents
    start_date = DateOpt(url_param='startDT')
    end_date = DateOpt(url_param='endDT')

    state = FilterOpt(url_param='stateCd')
    county = FilterOpt(url_param='countyCd', multi=True)
    basin = FilterOpt(url_param='huc', multi=True)

    station = FilterOpt(url_param='site', multi=True)
    parameter = FilterOpt(url_param='parameterCd', multi=True)

    # Additional options unique to NWIS
    sitetype = ChoiceOpt(
        url_param='siteType',
        multi=True,
        choices=list(SITE_TYPES.keys()),
    )

    # Each NWIS webservice uses the same base URL, with a service path
    service = None

    @property
    def url(self):
        return "http://waterservices.usgs.gov/nwis/%s/" % self.service


class NwisWaterMlIO(NwisLoader, WaterMlParser, TupleMapper, BaseIO):
    """
    Base class for loading WaterML data from the USGS web services.  Use
    DailyValuesIO or InstantValuesIO instead depending on your needs.
    """

    default_params = {
        'format': 'waterml,1.1',
    }


class ParameterIO(NetLoader, RdbParser, TupleMapper, BaseIO):
    """
    Base class for loading USGS NWIS parameter code definitions.  Use
    FixedParameterIO or NumericParameterIO instead depending on your needs.
    """
    query = None
    params = {'fmt': 'rdb'}

    @property
    def url(self):
        return "http://help.waterdata.usgs.gov/code/%s" % self.query


# Preset classes for commonly used NWIS web services

class SiteIO(NwisLoader, RdbParser, TupleMapper, BaseIO):
    """
    Loads USGS site metadata from NWIS webservices (via RDB format).

    Usage:

        site_params = SiteIO(basin='02070010')
        for site_param in site_params:
            print site_param.site_no, site_param.parm_cd, site_param.end_date
    """

    service = "site"
    default_params = {
        'format': 'rdb,1.0',
        'outputDataTypeCd': 'all',
        'siteStatus': 'active',
    }


class DailyValueIO(NwisWaterMlIO):
    """
    Load USGS daily values from NWIS webservices (via WaterML format).

    Usage:

        dvals = DailyValueIO(basin='02070010')
        for dval in dvals:
            print
            print dval.site_code, dval.variable_code
            for row in dval.data:
                print row.date, row.value
    """

    service = 'dv'


class InstantValueIO(NwisWaterMlIO):
    """
    Load USGS instant values from NWIS webservices (via WaterML format).

    Usage:

        ivals = InstantValueIO(basin='02070010')
        for ival in ivals:
            print
            print ival.site_code, ival.variable_code
            for row in ival.data:
                print row.date, row.value
    """

    service = 'iv'


# Preset classes for USGS waterdata code definitions

class FixedParameterIO(ParameterIO):
    """
    Loads USGS fixed (text) parameters and value definitions.
    """

    query = "fixed_parms_query"


class NumericParameterIO(ParameterIO):
    """
    Loads USGS numeric parameter definitions.
    """

    query = "parameter_cd_query"
    params = {'fmt': 'rdb', 'group_cd': '%'}
