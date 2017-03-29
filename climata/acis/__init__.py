import json
from wq.io import JsonParser, BaseIO, TupleMapper, TimeSeriesMapper
from climata.base import (
    WebserviceLoader, FilterOpt, DateOpt, ChoiceOpt,
    parse_date, fill_date_range,
)
from .constants import (
    ELEMENT_BY_ID,
    ELEMENT_BY_NAME,
    ALL_META_FIELDS,
    DEFAULT_META_FIELDS,
    AUTHORITY_BY_ID,
    ADD_IDS,
)


class ParameterOpt(ChoiceOpt):
    multi = True
    url_param = 'elems'
    choices = list(ELEMENT_BY_ID.keys()) + list(ELEMENT_BY_NAME.keys())


class AcisIO(WebserviceLoader, JsonParser, TupleMapper, BaseIO):
    """
    Base class for loading data from ACIS web services
    See http://data.rcc-acis.org/doc/
    """

    path = None  # ACIS web service path

    # (Re-)define some default WebserviceLoader options
    state = FilterOpt(multi=True)
    county = FilterOpt(multi=True)
    basin = FilterOpt(multi=True)
    station = FilterOpt(ignored=True)

    # Additional ACIS-specific option
    meta = ChoiceOpt(
        multi=True,
        choices=ALL_META_FIELDS,
        default=DEFAULT_META_FIELDS,
    )

    @property
    def url(self):
        """
        URL for wq.io.loaders.NetLoader
        """
        return "http://data.rcc-acis.org/%s" % self.path

    def serialize_params(self, params, complex):
        if complex:
            # ACIS web service supports JSON object as "params" parameter
            nparams = {}
            for key, val in list(params.items()):
                url_param = self.get_url_param(key)
                if len(val) == 1 and isinstance(val[0], str):
                    val = val[0]
                nparams[url_param] = val
            return {'params': json.dumps(nparams)}
        else:
            # Simpler queries can use traditional URL parameters
            return super(AcisIO, self).serialize_params(params)


class StationMetaIO(AcisIO):
    """
    Retrieves metadata about the climate stations in a region.
    See http://data.rcc-acis.org/doc/#title8
    """

    namespace = "meta"  # For wq.io.parsers.text.JsonParser
    path = "StnMeta"

    # These options are not required for StationMetaIO
    start_date = DateOpt(url_param='sdate')
    end_date = DateOpt(url_param='edate')
    parameter = ParameterOpt()

    def parse(self):
        """
        Convert ACIS 'll' value into separate latitude and longitude.
        """
        super(AcisIO, self).parse()

        # This is more of a "mapping" step than a "parsing" step, but mappers
        # only allow one-to-one mapping from input fields to output fields.
        for row in self.data:
            if 'meta' in row:
                row = row['meta']
            if 'll' in row:
                row['longitude'], row['latitude'] = row['ll']
                del row['ll']

    def map_value(self, field, value):
        """
        Clean up some values returned from the web service.
        (overrides wq.io.mappers.BaseMapper)
        """

        if field == 'sids':
            # Site identifiers are returned as "[id] [auth_id]";
            # Map to auth name for easier usability
            ids = {}
            for idinfo in value:
                id, auth = idinfo.split(' ')
                auth = AUTHORITY_BY_ID[auth]
                ids[auth['name']] = id
            return ids

        if field == 'valid_daterange':
            # Date ranges for each element are returned in an array
            # (sorted by the order the elements were were requested);
            # Convert to dictionary with element id as key
            elems, complex = self.getlist('parameter')
            ranges = {}
            for elem, val in zip(elems, value):
                if val:
                    start, end = val
                    ranges[elem] = (parse_date(start), parse_date(end))
                else:
                    ranges[elem] = None, None
            return ranges
        return value


class StationDataIO(StationMetaIO):
    """
    Retrieve daily time series data from the climate stations in a region.
    See http://data.rcc-acis.org/doc/#title19
    """

    nested = True

    namespace = "data"  # For wq.io.parsers.text.JsonParser
    path = "MultiStnData"

    # Specify ACIS-defined URL parameters for start/end date
    start_date = DateOpt(required=True, url_param='sdate')
    end_date = DateOpt(required=True, url_param='edate')

    parameter = ParameterOpt(required=True)

    # Additional information for daily results
    add = ChoiceOpt(multi=True, choices=ADD_IDS)

    def get_field_names(self):
        """
        ACIS web service returns "meta" and "data" for each station;
        Use meta attributes as field names
        """
        field_names = super(StationDataIO, self).get_field_names()
        if set(field_names) == set(['meta', 'data']):
            meta_fields = list(self.data[0]['meta'].keys())
            if set(meta_fields) < set(self.getvalue('meta')):
                meta_fields = self.getvalue('meta')
            field_names = list(meta_fields) + ['data']
        return field_names

    def serialize_params(self, params, complex):
        # If set, apply "add" option to each requested element / parameter
        # (Rather than as a top-level URL param)
        if 'add' in params:
            complex = True
            elems = []
            for elem in params.get('parameter', []):
                if not isinstance(elem, dict):
                    elem = {'name': elem}
                elem['add'] = ",".join(params['add'])
                elems.append(elem)
            params['parameter'] = elems
            del params['add']
        return super(StationDataIO, self).serialize_params(params, complex)

    def usable_item(self, data):
        """
        ACIS web service returns "meta" and "data" for each station; use meta
        attributes as item values, and add an IO for iterating over "data"
        """

        # Use metadata as item
        item = data['meta']

        # Add nested IO for data
        elems, elems_is_complex = self.getlist('parameter')
        if elems_is_complex:
            elems = [elem['name'] for elem in elems]

        add, add_is_complex = self.getlist('add')
        item['data'] = DataIO(
            data=data['data'],
            parameter=elems,
            add=add,
            start_date=self.getvalue('start_date'),
            end_date=self.getvalue('end_date'),
        )

        # TupleMapper will convert item to namedtuple
        return super(StationDataIO, self).usable_item(item)


class DataIO(TimeSeriesMapper, BaseIO):
    """
    IO for iterating over ACIS time series data.
    Created internally by StationDataIO; not meant to be used directly.
    """

    # Inherited from parent
    parameter = []
    add = []
    start_date = None
    end_date = None

    date_formats = []  # For TimeSeriesMapper

    def load_data(self, data):
        """
        MultiStnData data results are arrays without explicit dates;
        Infer time series based on start date.
        """

        dates = fill_date_range(self.start_date, self.end_date)
        for row, date in zip(data, dates):
            data = {'date': date}
            if self.add:
                # If self.add is set, results will contain additional
                # attributes (e.g. flags). In that case, create one row per
                # result, with attributes "date", "elem", "value", and one for
                # each item in self.add.
                for elem, vals in zip(self.parameter, row):
                    data['elem'] = elem
                    for add, val in zip(['value'] + self.add, vals):
                        data[add] = val
                    yield data
            else:
                # Otherwise, return one row per date, with "date" and each
                # element's value as attributes.
                for elem, val in zip(self.parameter, row):
                    # namedtuple doesn't like numeric field names
                    if elem.isdigit():
                        elem = "e%s" % elem
                    data[elem] = val
                yield data

    def __init__(self, *args, **kwargs):
        data = kwargs.pop('data')
        super(DataIO, self).__init__(*args, **kwargs)
        self.data = list(self.load_data(data))

    def get_field_names(self):
        """
        Different field names depending on self.add setting (see load_data)
        For BaseIO
        """
        if self.add:
            return ['date', 'elem', 'value'] + [flag for flag in self.add]
        else:
            field_names = ['date']
            for elem in self.parameter:
                # namedtuple doesn't like numeric field names
                if elem.isdigit():
                    elem = "e%s" % elem
                field_names.append(elem)
            return field_names

    @property
    def key_fields(self):
        """
        Different key fields depending on self.add setting (see load_data)
        For TimeSeriesMapper
        """
        if self.add:
            return ['date', 'elem']
        else:
            return ['date']
