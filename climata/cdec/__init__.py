from wq.io import CsvNetIO

class CDECMetaIO(CsvNetIO):
    debug = True
    quotechar = "'"
    url = 'http://cdec.water.ca.gov/misc/all_stations.csv'
    field_names = ['station_code', 'url', 'description', 'no_of_records', 'lat', 'long', 'extra']
    
    def usable_item(self, item):
        if item['extra'] is not None:
            item['no_of_records'] = item['lat']
            item['lat'] = item['long']
            item['long'] = item['extra']
            item['extra'] = ''
        else:
            item['extra'] = ''
        return super(CDECMetaIO, self).usable_item(item)
    