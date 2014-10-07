from wq.io.parsers.base import TableParser
from csv import reader


class EnsembleCsvParser(TableParser):
    header_row = 0
    max_header_row = 0
    start_row = 2

    def parse(self):
        csvdata = reader(self.file)
        first_line = next(csvdata)
        self.data = []
        sitedata = {}
        years = []
        for col in first_line[1:]:
            if col not in sitedata:
                sitedata[col] = []
                year = 1950
            else:
                year += 1
            years.append(year)

        # Skip second row
        next(csvdata)
        self.data = []

        for row in csvdata:
            date = row[0]
            for site, val, year in zip(first_line[1:], row[1:], years):
                data = {
                    'date': date,
                    'year': year,
                    'value': val,
                }
                sitedata[site].append(data)

        self.data = [{
            'site': site,
            'data': data
        } for site, data in sitedata.items()]
