from wq.io import CsvNetIO
from datetime import datetime


class OwrdWaterIO(CsvNetIO):
    delimiter = '\t'
    debug = True
    max_header_row = 15
    filename = ''
    burl = 'http://filepickup.wrd.state.or.us/files/Publications/obswells/data'

    @property
    def url(self):
        return '%s/%s' % (self.burl, self.filename)

    '''
    @property
    def filename(self):
        return self.base_url + self.text_file
        # water_level_data_url = base_url + 'owrd_wls.txt'
        # well_data_url = base_url + 'owrd_master.txt'
        # owrd_redrils_url = base_url + 'owrd_redrills.txt'
    '''


class OwrdFlowIO(CsvNetIO):
    delimiter = '\t'
    debug = True
    station_nbr = ''
    dataset = ''
    start_date = ''
    burl1 = 'http://apps.wrd.state.or.us/apps/sw/hydro_near_real_time/'
    burl2 = 'hydro_download.aspx'

    @property
    def url(self):
        return '%s%s' (self.burl1, self.burl2) % self.params

    @property
    def params(self):
        return {
            'station_nbr': self.station_nbr,
            'dataset': self.dataset,
            'format': 'tsv',
            'start_date': self.start_date,
            'end_date': datetime.strftime(datetime.today(), '%m/%d/%Y')
        }
