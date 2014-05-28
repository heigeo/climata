from datetime import datetime
from warnings import warn
from wq.io import make_date_mapper, NetLoader
parse_date = make_date_mapper('%Y-%m-%d')


class FilterOpt(object):
    """
    Base class for describing a filter option
    """
    name = None  # Option name as defined on IO class
    url_param = None  # Actual URL parameter to use (defaults to name)

    required = False  # Whether option is equired for valid request
    multi = False  # Whether multiple values are allowed
    ignored = False  # Used on subclasses when option does not apply

    value = None  # Value provided by IO class
    default = None  # Default value

    def __init__(self, **kwargs):
        """
        Allow setting the above via kwargs
        """
        self.__dict__.update(**kwargs)

    def get_url_param(self):
        return self.url_param or self.name

    def parse(self, value):
        """
        Enforce rules and return parsed value
        """
        if self.required and value is None:
            raise ValueError("%s is required!" % self.name)
        elif self.ignored and value is not None:
            warn("%s is ignored for this class!" % self.name)
        elif (not self.multi and isinstance(value, (list, tuple))
              and len(val) > 1):
            raise ValueError("%s does not accept multiple values!" % self.name)
        return value


class DateOpt(FilterOpt):
    date_only = True

    def parse_date(self, value):
        return parse_date(value)

    def parse(self, value):
        """
        Parse date
        """
        value = super(DateOpt, self).parse(value)
        if value is None:
            return None
        if isinstance(value, basestring):
            value = self.parse_date(value)
        if isinstance(value, datetime) and self.date_only:
            value = value.date()
        return value


class ChoiceOpt(FilterOpt):
    choices = []  # Valid choices for this option

    def parse(self, value):
        value = super(ChoiceOpt, self).parse(value)
        if value is None:
            return None
        if isinstance(value, (list, tuple)):
            check_values = value
        else:
            check_values = [value]
        for cv in check_values:
            if cv not in self.choices:
                raise ValueError(
                    "%s is not a valid choice for %s!" % (cv, self.name)
                )
        return value


class WebserviceLoader(NetLoader):
    """
    NetLoader subclass with enhanced functionality for enumerating and
    validating URL arguments.
    """

    # Default filter options, common to most web services for climate data.
    # Every climata IO class is assumed to support at least these options; if
    # any are not applicable they should be overridden with ignored=True.

    # Time period filters
    start_date = DateOpt(required=True)
    end_date = DateOpt(required=True)

    # Region filters
    state = FilterOpt(multi=True)
    county = FilterOpt(multi=True)
    basin = FilterOpt(multi=True)

    # Station and parameter code filters
    station = FilterOpt(multi=True)
    parameter = FilterOpt(multi=True)

    def __init__(self, *args, **kwargs):
        """
        Initialize web service (and general IO) options
        """

        #  Validate web service parameters using FilterOpt information
        for name, opt in self.filter_options.items():
            opt.name = name
            val = kwargs.pop(name, opt.default)
            opt.value = opt.parse(val)

        # Mimic BaseIO behavior since it's not a super class of NetLoader
        if kwargs:
            self.__dict__.update(**kwargs)
        self.refresh()

    @property
    def filter_options(self):
        """
        List all filter options defined on class
        """
        options = {}
        for key in dir(self):
            if not key.startswith('__') and key not in (
                'filter_options', 'params', 'field_map', 'tuple_class',
                'tuple_prototype',
            ):
                val = getattr(self, key)
                if isinstance(val, FilterOpt):
                    options[key] = val
        return options

    def get_url_param(self, key):
        return self.filter_options[key].get_url_param()

    def getlist(self, name):
        """
        Retrieve given property from class/instance, ensuring it is a list.
        Also determine whether the list contains simple text/numeric values or
        nested dictionaries (a "complex" list)
        """
        value = self.filter_options[name].value
        complex = False

        def str_value(val):
            if isinstance(val, dict):
                complex = True
                return val
            else:
                return unicode(val)

        if value is None:
            pass
        elif isinstance(value, (list, tuple)):
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

        for name, opt in self.filter_options.items():
            if self.set_param(params, name):
                complex = True
        return params, complex

    @property
    def params(self):
        """
        URL parameters for wq.io.loaders.NetLoader
        """
        params, complex = self.get_params()
        return self.serialize_params(params, complex)

    def serialize_params(self, params, complex=False):
        """
        Serialize parameter names and values to a dict ready for urlencode()
        """
        if complex:
            # See climata.acis for an example implementation
            raise NotImplementedError("Cannot serialize %s!" % params)
        else:
            # Simpler queries can use traditional URL parameters
            return {
                self.get_url_param(key): ','.join(val)
                for key, val in params.items()
            }
