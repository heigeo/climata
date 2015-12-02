from wq.io import (
    XmlNetIO, XmlParser, BaseIO,
    TupleMapper, TimeSeriesMapper
)
from climata.base import (
    WebserviceLoader, ZipWebserviceLoader,
    FilterOpt, DateOpt, ChoiceOpt
)
from .parsers import EnsembleCsvParser


class HydroForecastIO(WebserviceLoader, XmlParser, TimeSeriesMapper, BaseIO):
    """
    Loads hydrograph forecast data (next 3 days) from weather.gov
    """

    ###########################################
    # valid is the time of the forecast in UTC
    # primary is the stage in ft
    # secondary is the flow in kcfs
    # It appears to return 3 days forecast in the future
    ###########################################

    start_date = DateOpt(ignored=True)
    end_date = DateOpt(ignored=True)
    state = FilterOpt(ignored=True)
    county = FilterOpt(ignored=True)
    station = FilterOpt(url_param='gage')
    parameter = FilterOpt(ignored=True)
    basin = FilterOpt(ignored=True)

    root_tag = "forecast"
    date_formats = [
        '%Y-%m-%dT%H:%M:%S'
    ]
    url = 'http://water.weather.gov/ahps2/hydrograph_to_xml.php'

    def parse_item(self, elem):
        valid = elem.find('valid')
        primary = elem.find('primary')
        secondary = elem.find('secondary')
        return {
            'date': valid.text.replace('-00:00', ''),
            primary.attrib['name']: primary.text,
            secondary.attrib['name']: secondary.text,
        }


class EnsembleForecastIO(ZipWebserviceLoader, EnsembleCsvParser,
                         TupleMapper, BaseIO):

    """
    Load ensemble forecast zip files from the CNRFC website.
     - start_date and basin are required to specify the zip file;
     - station and end_date can be used to filter the downloaded data.
    """

    nested = True

    start_date = DateOpt(required=True)
    end_date = DateOpt()

    # Region filters
    state = FilterOpt(ignored=True)
    county = FilterOpt(ignored=True)

    # FIXME: this isn't actually a HUC8 basin
    basin = FilterOpt(required=True)

    station = FilterOpt(multi=True)
    parameter = FilterOpt(ignored=True)

    region = ChoiceOpt(
        default="cnrfc",
        choices=["cnrfc"]
    )

    urls = {
        "cnrfc": (
            "http://www.cnrfc.noaa.gov/csv/" +
            "{date}12_{basin}_hefs_csv_daily.zip"
        )
    }

    @property
    def params(self):
        # Don't actually need params, but ensure validation logic is called
        super(EnsembleForecastIO, self).params
        return None

    @property
    def url(self):
        url = self.urls[self.getvalue("region")]
        return url.format(
            date=self.getvalue("start_date").strftime("%Y%m%d"),
            basin=self.getvalue("basin"),
        )

    def parse(self):
        super(EnsembleForecastIO, self).parse()

        # Optionally filter by station id
        site_filter = self.getvalue('station')
        date_filter = self.getvalue('end_date')
        if not site_filter:
            return
        self.data = [
            item for item in self.data
            if item['site'] in site_filter
        ]
        if not date_filter:
            return
        date_filter = date_filter.strftime('%Y-%m-%d') + " 23:59:59"
        for item in self.data:
            item['data'] = [
                row for row in item['data']
                if row['date'] <= date_filter
            ]

    def usable_item(self, item):
        item = item.copy()
        item['data'] = TimeSeriesIO(data=item['data'])
        return super(EnsembleForecastIO, self).usable_item(item)


class TimeSeriesIO(TimeSeriesMapper, BaseIO):
    date_formats = ["%Y-%m-%d %H:%M:%S"]

    def usable_item(self, item):
        uitem = super(TimeSeriesIO, self).usable_item(item)
        # Convert KCFS to CFS
        return uitem._replace(value=uitem.value * 1000)


class SiteIO(XmlNetIO):
    """
    Base class for CNRFC site layers.  Use ForecastSiteIO or EnsembleSiteIO.
    """
    layer = None
    key_field = "id"
    region = "cnrfc"
    urls = {
        "cnrfc": "http://www.cnrfc.noaa.gov/data/kml/%s.xml"
    }

    @property
    def url(self):
        if self.region not in self.urls:
            raise Exception("Region %s not currently supported!" % self.region)
        return self.urls[self.region] % self.layer

    def parse_item(self, item):
        return item.attrib


class ForecastSiteIO(SiteIO):
    """
    CNRFC sites with deterministic forecasts.
    """
    layer = "riverFcst"


class EnsembleSiteIO(SiteIO):
    """
    CNRFC sites with ensemble forecasts.
    """
    layer = "ensPoints"
