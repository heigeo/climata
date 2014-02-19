from wq.io import CsvFileIO
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from wq.io.parsers import readers
from ftplib import FTP
from passfile import server, username, password
import os

####################################################
# The passfile module contains username and
# password for the ftp server. It is not in
# the repository.
# Also, extract_file.sh is required for this script.
####################################################


class DownloadExtract(object):
    ######################################
    # datestr must be in YYYYMMDD format
    # This class does not return anything.
    # It just downloads the tar.Z file.
    ######################################
    datestr = ''

    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)
        ftp = FTP(server)
        ftp.login(user=username, passwd=password)
        ftp.cwd('/outbound')
        file_retrieved = ftp.retrbinary(
            'RETR %s' % self.tarfilename,
            open('%s' % self.tarfilename, 'w').write
            )

    @property
    def tarfilename(self):
        #print 'all_espts.datacard.%s.tar.Z' % self.datestr
        return 'all_espts.datacard.%s.tar.Z' % self.datestr


class CNRFCFileIO(object):
    datestr = ''
    site = ''
    values_for_month = {}
    time_series = []

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        os.system('cnrfc/extract_file.sh %s %s' % (self.datestr, self.site))
        self.parsefile()
        self.timeseries()

    def parsefile(self):
        f = open('all_%s.datacard' % (self.site))
        months_seen = set()
        current_month_values = []
        for line in f:
            if line[:5] == self.site:
                moyr = line[12:16].replace(' ', '0')
                if moyr not in months_seen:
                    months_seen.add(moyr)
                    #print months_seen
                    try:
                        self.values_for_month[r_date] = current_month_values
                    except NameError:
                        continue
                    current_month_values = []
                for value in str.split(line[20:]):
                    if value != '-999.0':
                        current_month_values.append(value)
                r_date = moyr
            else:
                pass
        return self.values_for_month

    def timeseries(self):
        for key, values in self.values_for_month.items():
            kdate = datetime.strptime(key, '%m%y')
            if kdate.year > datetime.today().year:
                kdate = kdate - relativedelta(years=100)
            for value in values:
                ts = {}
                ts['date'] = datetime.strftime(kdate, '%Y-%m-%d')
                ts['value'] = value
                self.time_series.append(ts)
                kdate = kdate + timedelta(days=1)
        return self.time_series

site_list = {
    "BTYO3": "SPRAGUE RIVER - BEATTY (BTYO3)",
    "WMSO3": "WILLIAMSON RIVER - CHILOQUIN (WMSO3)",
    "KLAO3": "KLAMATH RIVER - UPPER KLAMATH LAKE (KLAO3)",
    "KEOO3L": "KLAMATH RIVER - KENO (KEOO3) *LOCAL*",
    "BOYO3L": "KLAMATH RIVER - BELOW JC POWER PLANT (BOYO3) *LOCAL*",
    "IRGC1L": "KLAMATH RIVER - IRON GATE RESERVOIR (IRGC1) *LOCAL*",
    "YREC1": "SHASTA RIVER - YREKA (YREC1)",
    "FTJC1": "SCOTT RIVER - FORT JONES (FTJC1)",
    "SBRC1": "SALMON RIVER - SOMES BAR (SBRC1)",
    "CEGC1": "TRINITY RIVER - TRINITY LAKE (CEGC1)",
    "HYMC1": "SOUTH FORK TRINITY RIVER - HYAMPOM (HYMC1)",
    "CREC1": "SMITH RIVER - JED SMITH NEAR CRESCENT CITY (CREC1)",
    "KLMC1W": "KLAMATH RIVER - KLAMATH (KLMC1) *EXCLUDING RESERVOIR RELEASES*",
    "FTDC1": "SMITH RIVER - DOCTOR FINE BRIDGE (FTDC1)",
    "ORIC1": "REDWOOD CREEK - ORICK (ORIC1)",
    "ARCC1": "MAD RIVER - ARCATA (ARCC1)",
    "PLBC1": "EEL RIVER - LAKE PILLSBURY (PLBC1)",
    "DOSC1": "MIDDLE FORK EEL RIVER - DOS RIOS (DOSC1)",
    "FTSC1": "EEL RIVER - FORT SEWARD (FTSC1)",
    "MRNC1": "SOUTH FORK EEL RIVER - MIRANDA (MRNC1)",
    "SCOC1": "EEL RIVER - SCOTIA (SCOC1)",
    "BRGC1": "VAN DUZEN RIVER - BRIDGEVILLE (BRGC1)",
    "FRNC1": "EEL RIVER - FERNBRIDGE (FRNC1)",
    }
