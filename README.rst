.. image:: https://raw.githubusercontent.com/heigeo/climata-viewer/master/app/images/logo-small.png
    :target: http://climata.houstoneng.net
    :alt: Climata
    :align: center

**climata** is a pythonic interface for loading and processing time series data
from climate and flow monitoring stations and observers. climata leverages 
a number of webservices as listed below.  climata is powered by
`wq.io <http://wq.io/wq.io>`_, and shares its goal of maximizing the reusability of
data parsing code, by smoothing over some of the differences between various data formats.

.. image:: https://travis-ci.org/heigeo/climata.svg?branch=master
    :target: https://travis-ci.org/heigeo/climata

.. image:: https://pypip.in/version/climata/badge.svg?style=flat
    :target: https://pypi.python.org/pypi/climata/
    :alt: Latest Version
    
Tested on Python 2.7 and 3.4.

Getting Started
---------------

::

    pip3 install climata

See https://github.com/heigeo/climata to report any issues.

Available Services
------------------

=================== ================================================================ ============== ============
 Module             Classes                                                          Data Source     Agency/Org.
=================== ================================================================ ============== ============
climata.acis_       ``StationMetaIO``, ``StationDataIO``                             ACIS_           NOAA RCCs
climata.cocorahs_   ``CocorahsIO``                                                   CoCoRaHS_       CoCoRaHS
climata.hydromet_   ``DailyDataIO``, ``InstantDataIO``, ``AgrimetRecentIO``          Hydromet_       USBR
climata.nws_        ``HydroForecastIO``, ``EnsembleForecastIO``, ``EnsembleSiteIO``  CNRFC_          NWS
climata.snotel_     ``StationIO``, ``StationDailyDataIO``, ``RegionDailyDataIO``     `SNOTEL AWDB`_  NRCS
climata.usgs_       ``SiteIO``, ``DailyValueIO``, ``InstantValueIO``                 NWIS_           USGS
=================== ================================================================ ============== ============

Usage
-----
Command-line interface:

::

    # Load metadata for sites in Mississippi Headwaters HUC4
    acis_sites.py 0701 > sites.csv

    # Load daily average temperature for these sites
    acis_data.py 0701 avgt > data.csv


Python API:

::

    from climata.acis import StationDataIO

    # Load average temperature for sites in Mississippi Headwaters HUC8
    sites = StationDataIO(
        basin="07010101",
        start_date="2012-12-01",
        end_date="2012-12-31",
        parameter="avgt"
    )

    # Display site information and time series data
    for site in sites:
        print site.name
        for evt in site.data:
            print evt.date, evt.avgt


More Python code examples are available via the `climata-viewer website`_.

.. _ACIS: http://data.rcc-acis.org/
.. _CoCoRaHS: http://data.cocorahs.org/cocorahs/export/exportmanager.aspx
.. _Hydromet: http://www.usbr.gov/pn/hydromet/arcread.html
.. _CNRFC: http://www.cnrfc.noaa.gov/
.. _SNOTEL AWDB: http://www.wcc.nrcs.usda.gov/web_service/awdb_web_service_landing.htm
.. _NWIS: http://waterdata.usgs.gov/nwis
.. _climata.acis: https://github.com/heigeo/climata/blob/master/climata/acis/__init__.py
.. _climata.cocorahs: https://github.com/heigeo/climata/blob/master/climata/cocorahs/__init__.py
.. _climata.hydromet: https://github.com/heigeo/climata/blob/master/climata/hydromet/__init__.py
.. _climata.nws: https://github.com/heigeo/climata/blob/master/climata/nws/__init__.py
.. _climata.snotel: https://github.com/heigeo/climata/blob/master/climata/snotel/__init__.py
.. _climata.usgs: https://github.com/heigeo/climata/blob/master/climata/usgs/__init__.py
.. _climata-viewer website: http://climata.houstoneng.net/datarequests/
