climata
=======

climata is a pythonic interface for loading and processing time series data
from the Applied Climate Information System (ACIS).  climata leverages the
webservices available at http://data.rcc-acis.org.

Getting Started
---------------

::

    pip install climata

See https://github.com/heigeo/climata to report any issues.
climata is powered by `wq.io <http://wq.io/wq.io>`_.

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

    from climata import StationDataIO

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

