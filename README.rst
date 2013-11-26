climata
=======

climata is a pythonic interface for loading and processing time series data
from climate and flow monitoring stations and observers. climata leverages 
a number of webservices as listed below.  climata is powered by
`wq.io <http://wq.io/wq.io>`_, and shares its goal of maximizing the reusability of
data parsing code, by smoothing over some of the differences between various data formats.

Getting Started
---------------

::

    pip install climata

See https://github.com/heigeo/climata to report any issues.

Available Services
------------------

=================== ======================================================= ==========
 Module             Classes                                                  Data Source
=================== ======================================================= ==========
climata.acis_       ``StationMetaIO``, ``StationDataIO``                     ACIS_
climata.cocorahs_   ``CocorahsIO``                                           CoCoRaHS_
climata.hydromet_   ``DailyDataIO``, ``InstantDataIO``, ``AgrimetRecentIO``  Hydromet_   
=================== ======================================================= ==========

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
        sdate="2012-12-01",
        edate="2012-12-31",
        elems="avgt"
    )

    # Display site information and time series data
    for site in sites:
        print site.name
        for evt in site.data:
            print evt.date, evt.avgt


.. _ACIS: http://data.rcc-acis.org/
.. _CoCoRaHS: http://data.cocorahs.org/cocorahs/export/exportmanager.aspx
.. _Hydromet: http://www.usbr.gov/pn/hydromet/arcread.html
.. _climata.acis: https://github.com/heigeo/climata/blob/master/climata/acis/__init__.py
.. _climata.cocorahs: https://github.com/heigeo/climata/blob/master/climata/cocorahs/__init__.py
.. _climata.hydromet: https://github.com/heigeo/climata/blob/master/climata/hydromet/__init__.py
