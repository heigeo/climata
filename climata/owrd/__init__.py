from wq.io import CsvNetIO
from datetime import datetime

class OwrdWaterIO(CsvNetIO):
    delimiter = '\t'
    debug = True
    max_header_row = 15
    filename = ''
    
    @property
    def url(self):
        return 'http://filepickup.wrd.state.or.us/files/Publications/obswells/data/%s' % self.filename
    
    
    
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
    
    @property
    def url(self):
        return 'http://apps.wrd.state.or.us/apps/sw/hydro_near_real_time/hydro_download.aspx' % self.params
    
    @property
    def params(self):
        return {
            'station_nbr': self.station_nbr,
            'dataset': self.dataset,
            'format': 'tsv',
            'start_date': self.start_date,
            'end_date': datetime.strftime(datetime.today(), '%m/%d/%Y')
        }