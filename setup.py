from os.path import join, dirname
from setuptools import setup, find_packages
import sys


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

if sys.version_info[0] >= 3:
    OWSLIB = "OWSLib==0.8-dev"
    DEP_LINKS = [
        "https://github.com/tbicr/OWSLib/tarball/python3#egg=OWSLib-0.8-dev"
    ]
else:
    OWSLIB = "OWSLib"
    DEP_LINKS = []


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
    packages=find_packages(exclude=['tests']),
    description=DESCRIPTION,
    long_description=long_description(),
    install_requires=[
        'wq.io>=0.7.0',
        OWSLIB,
        "suds-jurko",
    ],
    dependency_links=DEP_LINKS,
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
    ],
    test_suite='tests',
    tests_require='httpretty',
)
