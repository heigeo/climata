from warnings import warn
from .version import VERSION
from datetime import datetime, timedelta
from wq.io import make_date_mapper, NetLoader, Zipper


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
        elif not self.multi and isinstance(value, (list, tuple)):
            if len(value) > 1:
                raise ValueError(
                    "%s does not accept multiple values!" % self.name
                )
            return value[0]
        elif self.multi and value is not None:
            if not isinstance(value, (list, tuple)):
                return [value]
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
        if isinstance(value, str):
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

    # URL params that apply to every request (if any)
    default_params = {}

    def __init__(self, *args, **kwargs):
        """
        Initialize web service (and general IO) options
        """

        #  Validate web service parameters using FilterOpt information
        self._values = {}
        for name, opt in self.filter_options.items():
            opt.name = name
            val = kwargs.pop(name, opt.default)
            self._values[name] = opt.parse(val)

        # Mimic BaseIO behavior since it's not a super class of NetLoader
        if kwargs:
            self.__dict__.update(**kwargs)
        self.refresh()

    @classmethod
    def get_filter_options(cls):
        """
        List all filter options defined on class (and superclasses)
        """
        attr = '_filter_options_%s' % id(cls)

        options = getattr(cls, attr, {})
        if options:
            return options

        for key in dir(cls):
            val = getattr(cls, key)
            if isinstance(val, FilterOpt):
                options[key] = val

        setattr(cls, attr, options)
        return options

    @property
    def filter_options(self):
        return type(self).get_filter_options()

    def get_url_param(self, key):
        return self.filter_options[key].get_url_param()

    def getvalue(self, name):
        return self._values[name]

    def getlist(self, name):
        """
        Retrieve given property from class/instance, ensuring it is a list.
        Also determine whether the list contains simple text/numeric values or
        nested dictionaries (a "complex" list)
        """
        value = self.getvalue(name)
        complex = {}

        def str_value(val):
            # TODO: nonlocal complex
            if isinstance(val, dict):
                complex['complex'] = True
                return val
            else:
                return str(val)

        if value is None:
            pass
        else:
            value = [str_value(val) for val in as_list(value)]

        return value, bool(complex)

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
            if opt.ignored:
                continue
            if self.set_param(params, name):
                complex = True
        return params, complex

    @property
    def params(self):
        """
        URL parameters for wq.io.loaders.NetLoader
        """
        params, complex = self.get_params()
        url_params = self.default_params.copy()
        url_params.update(self.serialize_params(params, complex))
        return url_params

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

    @property
    def user_agent(self):
        agent = "climata/%s %s %s" % (
            VERSION,
            super(WebserviceLoader, self).user_agent,
            "https://github.com/heigeo/climata",
        )
        return agent


class ZipWebserviceLoader(Zipper, WebserviceLoader):
    binary = True

    def load(self):
        super(ZipWebserviceLoader, self).load()
        self.unzip_file()


def fill_date_range(start_date, end_date, date_format=None):
    """
    Function accepts start date, end date, and format (if dates are strings)
    and returns a list of Python dates.
    """

    if date_format:
        start_date = datetime.strptime(start_date, date_format).date()
        end_date = datetime.strptime(end_date, date_format).date()
    date_list = []
    while start_date <= end_date:
        date_list.append(start_date)
        start_date = start_date + timedelta(days=1)
    return date_list


def as_list(value):
    if isinstance(value, (list, tuple)):
        return value
    else:
        return [value]
