from os.path import join, dirname
from setuptools import setup, find_packages


SERVICES = (
    "ACIS (NOAA RCCs)",
    "CoCoRaHS",
    "Hydromet (USBR)",
    "SNOTEL AWDB (NRCS)",
    "NWIS (USGS)",
)
SVC_STR = ", ".join(SERVICES[:-1]) + " and " + SERVICES[-1]

DESCRIPTION = "Loads climate and hydrology data from %s." % SVC_STR

LONG_DESCRIPTION = """
A pythonic library for iterating over climate time series data from %s.
Powered by wq.io.
""" % SVC_STR


def long_description():
    """Return long description from README.rst if it's present
    because it doesn't get installed."""
    try:
        return open(join(dirname(__file__), 'README.rst')).read()
    except IOError:
        return LONG_DESCRIPTION


def get_version():
    version = open(join(dirname(__file__), "climata", "version.py")).read()
    version = version.strip().replace("VERSION = ", '')
    version = version.replace('"', '')
    return version

setup(
    name='climata',
    version=get_version(),
    author='HEI Geo',
    author_email='gis@houstoneng.com',
    url='https://github.com/heigeo/climata',
    license='MIT',
    packages=find_packages(),
    description=DESCRIPTION,
    long_description=long_description(),
    install_requires=['wq.io>=0.5.1', 'owslib', 'SOAPpy'],
    scripts=['climata/bin/acis_sites.py', 'climata/bin/acis_data.py'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Natural Language :: English',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: System :: Networking :: Monitoring',
    ]
)
