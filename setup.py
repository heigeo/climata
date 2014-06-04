from os.path import join, dirname
from setuptools import setup, find_packages

LONG_DESCRIPTION = """
A python library for iterating over Applied Climate Information System (ACIS),
Hydromet (USBR), and CoCoRaHS time series data.  Powered by wq.io.
"""


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
    description='A pythonic interface for loading data from various climate webservices',
    long_description=long_description(),
    install_requires=['wq.io>=0.4.0'],
    scripts=['climata/bin/acis_sites.py', 'climata/bin/acis_data.py'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
    ]
)
