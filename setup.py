import os
from setuptools import setup, find_packages

LONG_DESCRIPTION = """
Library for iterating over Applied Climate Information System time series data
"""

def long_description():
    """Return long description from README.rst if it's present
    because it doesn't get installed."""
    try:
        return open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
    except IOError:
        return LONG_DESCRIPTION


setup(
    name='climata',
    version='0.1.0-dev',
    author='HEI Geo',
    author_email='gis@houstoneng.com',
    url='https://github.com/heigeo/climata',
    license='MIT',
    packages=find_packages(),
    description='Load Applied Climate Information System time series data',
    long_description=long_description(),
    install_requires=['wq.io>=0.3.0'],
    scripts=['climata/bin/acis_sites.py', 'climata/bin/acis_data.py'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
    ]
)
