import json
from datetime import datetime, date, timedelta
from wq.io import JsonNetIO, BaseIO, TimeSeriesMapper
from climata.util import parse_date
from .constants import *


class AcisIO(JsonNetIO):
    """
    Base class for loading data from ACIS web services
    See http://data.rcc-acis.org/doc/
    """

    path = None  # ACIS web service path
    basin = None  # HUC8 watershed
    elems = None  # Requested element codes
    meta = None  # Requested metadata

    @property
    def url(self):
        """
        URL for wq.io.loaders.NetLoader
        """
        return "http://data.rcc-acis.org/%s" % self.path

    def getdate(self, name):
        """
        Retrieve given property from class/instance, ensuring it is a date
        """
        value = getattr(self, name, None)

        if value is None:
            return None

        if isinstance(value, basestring):
            value = parse_date(value)

        if isinstance(value, datetime):
            value = value.date()

        return value

    def getlist(self, name):
        """
        Retrieve given property from class/instance, ensuring it is a list.
        Also determine whether the list contains simple text/numeric values or
        nested dictionaries (a "complex" list)
        """
        value = getattr(self, name, None)
        complex = False

        def str_value(val):
            if isinstance(val, dict):
                complex = True
                return val
            else:
                return unicode(val)

        if value is None:
            pass
        elif isinstance(value, list):
            value = [str_value(val) for val in value]
        else:
            value = [str_value(value)]

        return value, complex

    def set_param(self, into, name):
        """
        Set parameter key, noting whether list value is "complex"
        """
        value, complex = self.getlist(name)
        if value is not None:
            into[name] = value
        return complex

    def get_params(self):
        """
        Get parameters for web service, noting whether any are "complex"
        """
        params = {}
        complex = False

        if self.basin is None:
            # FIXME: Support other region types
            raise NotImplementedError("No region specified")

        for param in ('basin', 'meta', 'elems'):
            if self.set_param(params, param):
                complex = True
        for param in ('sdate', 'edate'):
            value = self.getdate(param)
            if value:
                params[param] = [unicode(value)]
        return params, complex

    @property
    def params(self):
        """
        URL parameters for wq.io.loaders.NetLoader
        """
        params, complex = self.get_params()
        if complex:
            # ACIS web service supports JSON object as "params" parameter
            params = {
                key: val[0]
                if len(val) == 1 and isinstance(val[0], basestring)
                else val
                for key, val in params.items()
            }
            return {'params': json.dumps(params)}
        else:
            # Simpler queries can use traditional URL parameters
            return {
                key: ','.join(val)
                for key, val in params.items()
            }


class StationMetaIO(AcisIO):
    """
    Retrieves metadata about the climate stations in a region.
    See http://data.rcc-acis.org/doc/#title8
    """

    namespace = "meta"  # For wq.io.parsers.text.JsonParser
    path = "StnMeta"
    elems = None

    @property
    def meta(self):
        """
        Request all available metadata by default
        """
        meta = ['name', 'state', 'sids', 'll',
                'elev', 'uid', 'county', 'climdiv']
        if self.elems is not None:
            meta.append('valid_daterange')
        return meta

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
            elems, complex = self.getlist('elems')
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

    namespace = "data"  # For wq.io.parsers.text.JsonParser
    path = "MultiStnData"

    sdate = None  # Start date
    edate = None  # End date
    add = None  # Additional information for daily results

    def get_field_names(self):
        """
        ACIS web service returns "meta" and "data" for each station;
        Use meta attributes as field names
        """
        field_names = super(StationDataIO, self).get_field_names()
        if field_names == ['meta', 'data']:
            field_names = self.data[0]['meta'].keys()
        return field_names

    def get_params(self):
        if self.sdate is None or self.edate is None:
            raise NotImplementedError("sdate and edate must be set!")
        params, complex = super(StationDataIO, self).get_params()

        # If self.add is defined, set it for each requested element
        if self.add is not None:
            add, add_is_complex = self.getlist('add')
            complex = True
            elems = []
            for elem in params.get('elems', []):
                if not isinstance(elem, dict):
                    elem = {'name': elem}
                elem['add'] = ",".join(add)
                elems.append(elem)
            params['elems'] = elems

        return params, complex

    def usable_item(self, data):
        """
        ACIS web service returns "meta" and "data" for each station; use meta
        attributes as item values, and add an IO for iterating over "data"
        """

        # Use metadata as item
        item = data['meta']

        # Add nested IO for data
        elems, elems_is_complex = self.getlist('elems')
        if elems_is_complex:
            elems = [elem['name'] for elem in elems]

        add, add_is_complex = self.getlist('add')
        item['data'] = DataIO(
            data=data['data'],
            elems=elems,
            add=add,
            sdate=self.getdate('sdate'),
            edate=self.getdate('edate')
        )

        # TupleMapper will convert item to namedtuple
        return super(StationDataIO, self).usable_item(item)


class DataIO(TimeSeriesMapper, BaseIO):
    """
    IO for iterating over ACIS time series data.
    Created internally by StationDataIO; not meant to be used directly.
    """

    # Inherited from parent
    elems = []
    add = []
    sdate = None
    edate = None

    date_formats = []  # For TimeSeriesMapper

    def load_data(self, data):
        """
        MultiStnData data results are arrays without explicit dates;
        Infer time series based on start date.
        """

        date = self.sdate
        day = timedelta(days=1)
        for row in data:
            data = {'date': date}
            if self.add:
                # If self.add is set, results will contain additional
                # attributes (e.g. flags). In that case, create one row per
                # result, with attributes "date", "elem", "value", and one for
                # each item in self.add.
                for elem, vals in zip(self.elems, row):
                    data['elem'] = elem
                    for add, val in zip(['value'] + self.add, vals):
                        data[add] = val
                    yield data
            else:
                # Otherwise, return one row per date, with "date" and each
                # element's value as attributes.
                for elem, val in zip(self.elems, row):
                    # namedtuple doesn't like numeric field names
                    if elem.isnumeric():
                        elem = "e%s" % elem
                    data[elem] = val
                yield data
            date += day

    def __init__(self, *args, **kwargs):
        data = kwargs.pop('data')
        self.data = self.load_data(data)
        super(DataIO, self).__init__(*args, **kwargs)

    def get_field_names(self):
        """
        Different field names depending on self.add setting (see load_data)
        For BaseIO
        """
        if self.add:
            return ['date', 'elem', 'value'] + [flag for flag in self.add]
        else:
            field_names = ['date']
            for elem in self.elems:
                # namedtuple doesn't like numeric field names
                if elem.isnumeric():
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
