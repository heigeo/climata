from wq.io.parsers.base import TableParser
from csv import reader


class EnsembleCsvParser(TableParser):
    header_row = 0
    max_header_row = 0
    start_row = 2

    def parse(self):
        csvdata = reader(self.file)
        sitedata = {}

        # Extract metadata from first two rows
        sites = next(csvdata)[1:]
        params = next(csvdata)[1:]
        years = []
        for site, param in zip(sites, params):
            if site not in sitedata:
                sitedata[site] = {}
            if param not in sitedata[site]:
                sitedata[site][param] = []
                year = 1950
            else:
                year += 1
            years.append(year)

        # Extract data from remaining rows
        for row in csvdata:
            date = row[0]
            for site, param, year, val in zip(sites, params, years, row[1:]):
                data = {
                    'date': date,
                    'year': year,
                    'value': val,
                }
                sitedata[site][param].append(data)

        # Repackage into IO-friendly arrays
        self.data = []
        for site in sitedata:
            siteid = site
            if len(siteid) == 6 and siteid[-1] == "L":
                siteid = siteid[:5]
            for param in sitedata[site]:
                self.data.append({
                    'site': siteid,
                    'parameter': param,
                    'data': sitedata[site][param],
                })
