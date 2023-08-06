import re
import math
from collections import OrderedDict
from nameparser import HumanName
from functools import lru_cache

from vital.debug import prepr

from cargo.exceptions import *
from cargo.expressions import Expression
from cargo.fields import Array, Bool, Text, Field
from cargo.fields.sequence import arraylist


__all__ = ('Settings', 'Location', 'Name')


class Settings(Array):

    def __init__(self, *settings, type=Bool(), **kwargs):
        """ `Settings`
            ==================================================================
            @*settings: (#tuple pairs (setting name, setting default)) -
                these will be ordered within the DB in the same order as
                provided
            @type: (:class:Field) storage type for the settings. The
                recommended types are :class:Bool (1 byte per setting) or
                :class:SmallInt (2 bytes per setting)
            ==================================================================
            :see::meth:cargo.Field.__init__
        """
        if not len(settings):
            raise FieldError('`%s`: You must include *settings '
                             'argument on initialization.' %
                             self.__class__.__name__)
        self.defaults = []
        self.names = []
        self.value = []

        for name, default in settings:
            self.add(name, default)

        kvalue = kwargs.get('value')
        value = self.value

        if kvalue is not None:
            del kwargs['value']
            super().__init__(type=type, value=kvalue, **kwargs)
        else:
            super().__init__(type=type, **kwargs)
            if value:
                self.value = value

    def __call__(self, value=Array.empty):
        try:
            self._make_list()
            if not len(self.value):
                self.value = self.defaults
            for name, val in (value.items() if hasattr(value, 'items') else
                              value):
                try:
                    self.value[self.get_index(name)] = self.type(val)
                except ValueError:
                    raise IndexError('Could not find `%s` in setting names.' %
                                     name)
            return self.value
        except (ValueError, TypeError, AttributeError):
            return super().__call__(value)

    def __getstate__(self):
        return self.__dict__

    def __getattr__(self, name):
        if name in dir(self):
            return self.__getattribute__(name)
        else:
            try:
                return self.value[self.get_index(name)]
            except ValueError:
                raise AttributeError()

    def __setattr__(self, name, value):
        if 'names' not in self.__dict__ or (
           'names' in self.__dict__ and name not in self.names):
            return super().__setattr__(name, value)
        else:
            try:
                self.value[self.get_index(name)] = self.type(value)
            except ValueError:
                raise AttributeError()

    def items(self):
        return ((name, value) for name, value in zip(self.names, self.value))

    def to_dict(self):
        return OrderedDict(self.items())

    for_json = to_dict

    def to_list(self):
        return list(self.items())

    def add(self, name, default):
        self.defaults.append(default)
        self.value.append(default)
        self.names.append(name.lower())

    def remove(self, name):
        self.value.pop(self.get_index(name))
        self.defaults.pop(self.get_index(name))
        self.names.remove(name)

    def update(self, settings):
        settings = settings.items() if hasattr(settings, 'items') else settings
        for name, value in settings:
            self.add(name, value)

    def at_index(self, index, **kwargs):
        """ -> (:class:Expression) field name with field index """
        return Expression(self, '[%s]' % index, self.empty, **kwargs)

    def at_name(self, name, **kwargs):
        """ -> (:class:Expression) field name with field index
            ..
                user.settings.activated = True
                user.settings.add('activated', False)
                user.settings.get_index('activated')
                # 0
                str(user.settings.at_name('activated'))
                # 'user.settings [1]'
                user.set(user.settings.at_name('activated') == False)
                user.save()
                # 'UPDATE user SET user.settings [1] = %(0x8be8a0)s ...'
            ..
        """
        return self.at_index(self.get_index(name), **kwargs)

    def get_index(self, name):
        """ -> (#int) Array index with Postgres, not the local list index """
        return self.names.index(name.lower())

    def clear_copy(self, **kwargs):
        return Field.clear_copy(self, *self.items(), **kwargs)

    def clear(self):
        super().clear()
        self.__call__(self.defaults)
        return self

    def reset(self):
        super().reset()
        self.__call__(self.defaults)
        return self


class distfloat(float):

    def to_miles(self):
        return self * 0.62140951185

    def to_feet(self):
        return self.to_miles() * 5280

    def to_meters(self):
        return self * 1000


class Location(Settings):

    def __init__(self, *args, type=None, **kwargs):
        """`Location`
            ==================================================================
            Provides several convenience features for working with locations,
            namely geodistance, formatting and segmentation. This field is
            backed by the SQL type |TEXT[]| and is |GIN| indexable.
            ==================================================================
            :see::meth:cargo.Field.__init__
        """
        super().__init__(('latitude', '0.0'),
                         ('longitude', '0.0'),
                         ('postal_code', '0'),
                         ('country_code3', ''),
                         ('country_code', ''),
                         ('region', ''),
                         ('city', ''),
                         *args,
                         type=Text(),
                         **kwargs)

    def __repr__(self):
        return '<%s, %s, %s>' % (self.city, self.region, self.country_code3)

    def to_dict(self):
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'postal_code': self.postal_code,
            'country_code3': self.country_code3,
            'country_code': self.country_code,
            'region': self.region,
            'city': self.city
        }

    for_json = to_dict

    @property
    def latitude(self):
        return float(self.value[self.get_index('latitude')])

    @latitude.setter
    def latitude(self, value):
        self.value[self.get_index('latitude')] = str(value)

    @property
    def longitude(self):
        return float(self.value[self.get_index('longitude')])

    @longitude.setter
    def longitude(self, value):
        self.value[self.get_index('longitude')] = str(value)

    @property
    def postal_code(self):
        return int(self.value[self.get_index('postal_code')])

    @postal_code.setter
    def postal_code(self, value):
        self.value[self.get_index('postal_code')] = str(value)

    @property
    def coord(self):
        return (self.latitude, self.longitude)

    @coord.setter
    def coord(self, value):
        self.value[self.get_index('latitude')] = str(value[0])
        self.value[self.get_index('longitude')] = str(value[1])

    def distance(self, latitude, longitude=None):
        """ Provides the distance between (@latitude, @longitude) and
            the field's :prop:latitude and :prop:longitude in km.
            @latitude: (#float or :class:Location)
            @longitude: (#float)
            -> (:class:distfloat) distance between the field lat/long
               and @latitude/@longitude
        """
        if isinstance(latitude, Location):
            latitude, longitude = latitude.latitude, latitude.longitude
        R = 6371  # Earth Radius in Km
        d_lat = math.radians(latitude - self.latitude)
        d_long = math.radians(longitude - self.longitude)
        lat1 = math.radians(self.latitude)
        latitude = math.radians(latitude)
        a = math.sin(d_lat/2) * math.sin(d_lat/2) + math.sin(d_long/2) * \
            math.sin(d_long/2) * math.cos(lat1) * math.cos(latitude)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        d = R * c
        return distfloat(d)

    @property
    def full(self):
        return ", ".join(filter(lambda x: x, (self.city,
                                              self.region,
                                              self.country_code3,
                                              str(self.postal_code),
                                              str(self.coord))))

    @property
    def postal(self):
        return "{}, {} {}\n{}".format(self.city, self.region, self.postal_code,
                                      self.country_code3)


class Name(Array):
    __slots__ = (list(Array.__slots__) + ['default_format', 'capitalize'])
    names = ('title', 'first', 'middle', 'last', 'suffix', 'nickname')

    def __init__(self, *args, type=None, capitalize=True,
                 default_format='{f} {l}', **kwargs):
        """`Name`
            ==================================================================
            Provides several convenience features for working with names,
            including parsing, capitalization and formatting. This field is
            backed by the SQL type |TEXT[]| and is |GIN| indexable.
            ==================================================================
            @capitalize: (#bool) True to automatically capitalize the name.
            @default_format: (#str) default format to use when |__str__| method
                is called. See :meth:format for options and examples.
            ==================================================================
            :see::meth:cargo.Field.__init__
        """
        super().__init__(*args, type=Text(), **kwargs)
        self.default_format = default_format
        self.capitalize = capitalize

    def __repr__(self):
        if not self.value:
            return super().__repr__()
        return '<%s>' % self.full

    def __call__(self, value=Array.empty):
        try:
            value = value if isinstance(value, str) else ' '.join(value)
            value = self._to_list(self._get_human_name(value))
        except TypeError:
            pass
        return super().__call__(value)

    def __str__(self):
        return self.format(self.default_format)

    def _to_list(self, val):
        name = [val.title,
                val.first,
                val.middle,
                val.last,
                val.suffix,
                ('"%s"' % val.nickname) if val.nickname else ""]
        return name

    def to_list(self):
        return self.value

    def to_dict(self):
        d = self.human.as_dict()
        d['full'] = self.full
        return d

    for_json = to_dict

    @staticmethod
    @lru_cache(1)
    def _get_human_name(*values, capitalize=True):
        human = HumanName(' '.join(values) or '')
        if capitalize:
            human.capitalize()
        return human

    @property
    def human(self):
        self._make_list()
        return self._get_human_name(*self.value, capitalize=self.capitalize)

    @property
    def title(self):
        return self.human.title

    @title.setter
    def title(self, value):
        self._make_list()
        self.human.title = value
        self.__call__(self._to_list(self.human))

    @property
    def nickname(self):
        return self.human.nickname

    @nickname.setter
    def nickname(self, value):
        self._make_list()
        self.human.nickname = value
        self.__call__(self._to_list(self.human))

    @property
    def given(self):
        return self.human.first

    @given.setter
    def given(self, value):
        self._make_list()
        self.human.first = value
        self.__call__(self._to_list(self.human))

    first = given

    @property
    def first_initial(self):
        try:
            return ''.join(m[0] + '.' for m in self.first.split(' '))
        except (TypeError, IndexError):
            return None

    @property
    def middle(self):
        return self.human.middle

    @middle.setter
    def middle(self, value):
        self._make_list()
        self.human.middle = value
        self.__call__(self._to_list(self.human))

    second = middle

    @property
    def middle_initial(self):
        try:
            return ''.join(m[0] + '.' for m in self.middle.split(' '))
        except (TypeError, IndexError):
            return None

    @property
    def family(self):
        try:
            return self.human.last
        except IndexError:
            return None

    @family.setter
    def family(self, value):
        self._make_list()
        self.human.last = value
        self.__call__(self._to_list(self.human))

    last = family
    surname = family

    @property
    def last_initial(self):
        try:
            return ''.join(m[0] + '.' for m in self.last.split(' '))
        except (TypeError, IndexError):
            return None

    @property
    def full(self):
        return str(self.human)

    @full.setter
    def full(self, value):
        self._make_list()
        self.human.full_name = value
        self.__call__(self._to_list(self.human))

    @property
    def suffix(self):
        return self.human.suffix

    @suffix.setter
    def suffix(self, value):
        self._make_list()
        self.human.suffix = value
        self.__call__(self._to_list(self.human))

    def format(self, format):
        """ Formats the name using shortcuts
            @format: (#str) e.g. First name, middle initial, last
                name |'{f} {mi} {l}'|

            ``Formats``
            - |f | first name
            - |fi| first initial
            - |m | middle name
            - |mi| middle initials
            - |l | last name
            - |li| last initial
            - |n | nickname
            - |t | title
            - |s | suffix

            ..
                name('Gregory James Stevens Willard III')
                name.format('{f} {mi} {l}')
            ..
            |Gregory J.S. Willard|
        """
        formats = {
            '{f}': self.first or "",
            '{fi}': self.first_initial or "",
            '{m}': self.middle or "",
            '{mi}': self.middle_initial or "",
            '{l}': self.last or "",
            '{li}': self.last_initial or "",
            '{n}': self.nickname or "",
            '{t}': self.title or "",
            '{s}': self.suffix or "",
        }
        out = ""
        for word in format.split(' '):
            try:
                fmt = re.search(r'(\{[fimlnts]{,2}\})', word)
                out_ = word.replace(fmt.group(0), formats[fmt.group(0)])
            except KeyError:
                out_ = word
            if out_:
                out += out_ + ' '
        return out.rstrip()

    at_index = Settings.at_index
    at_name = Settings.at_name
    get_index = Settings.get_index

    def clear_copy(self, *args, **kwargs):
        return super().clear_copy(*args, default_format=self.default_format,
                                  **kwargs)
