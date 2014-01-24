from wq.io import CsvNetIO

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