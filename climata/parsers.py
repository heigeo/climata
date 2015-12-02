from wq.io import CsvParser, BaseIO, TimeSeriesMapper
from wq.io.parsers.base import BaseParser
from owslib.waterml.wml11 import WaterML_1_1 as WaterML


class RdbParser(CsvParser):
    """
    Parser for RDB format (basically TSV with an extra header row)
    """
    max_header_row = 100
    delimiter = '\t'

    def parse(self):
        super(RdbParser, self).parse()
        # Skip second row which contains column lengths (5s, 10s, etc.)
        self.data = self.data[1:]


class TimeSeriesIO(TimeSeriesMapper, BaseIO):
    """
    Inner IO class for use by WaterMlParser.
    """

    # owslib already handles date parsing
    date_formats = []


class WaterMlParser(BaseParser):
    """
    wq.io-compatible Parser mixin for WaterML timeseries data.
    Generates a nested IO for each actual time series.

    Leverages owslib.waterml internally.
    """

    nested = True
    no_pickle_parser = ['response']

    def parse(self):
        response = WaterML(self.file.read().encode('utf-8')).response
        self.response = response
        self.data = list(map(self.parse_timeseries, response.time_series))

    def parse_timeseries(self, ts):
        site = ts.source_info
        param = ts.variable
        lng, lat = list(map(float, site.location.geo_coords[0]))

        # FIXME: This assumes there is only one values array, which might not
        # always be the case? (Same for site_codes below and geo_coords above.)
        values = ts.values[0]
        data = [{
            'date': date,
            'value': value,
        } for date, value in values.get_date_values()]

        return {
            'site_name': site.site_name,
            'site_code': site.site_codes[0],
            'variable_name': param.variable_name,
            'variable_code': param.variable_code,
            'unit': param.unit.code,
            'latitude': lat,
            'longitude': lng,
            'data': TimeSeriesIO(data=data)
        }
