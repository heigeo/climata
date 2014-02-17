from wq.io import CsvFileIO
from datetime import datetime, timedelta
from wq.io.parsers import readers
from ftplib import FTP
import os

class NRCSForecastByYear(CsvFileIO):
    fname = '' # Filename to retrieve from the service.
    
    @property
    def filename(self):
        ftp = FTP('ftp.wcc.nrcs.usda.gov')
        ftp.login()
        ftp.cwd('/data/water/forecast/forecast_bounds_byyear/')
        file_retrieved = ftp.retrbinary('RETR %s' % self.fname, open('%s' % self.fname, 'w+').write)
        return self.fname