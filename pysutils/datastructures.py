from pysutils.sentinels import NotGiven

# copied form webhelpers
class DumbObject(object):
    """A container for arbitrary attributes.

    Usage::
    
        >>> do = DumbObject(a=1, b=2)
        >>> do.b
        2
    
    Alternatives to this class include ``collections.namedtuple`` in Python
    2.6, and ``formencode.declarative.Declarative`` in Ian Bicking's FormEncode
    package.  Both alternatives offer more featues, but ``DumbObject``
    shines in its simplicity and lack of dependencies.

    """
    def __init__(self, **kw):
        self.__dict__.update(kw)

class OrderedProperties(object):
    """An object that maintains the order in which attributes are set upon it.

    Also provides an iterator and a very basic getitem/setitem
    interface to those attributes.

    (Not really a dict, since it iterates over values, not keys.  Not really
    a list, either, since each value must have a key associated; hence there is
    no append or extend.)
    """

    def __init__(self, initialize=True):
        self._data = OrderedDict()
        self._initialized=initialize

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return self._data.itervalues()

    def __add__(self, other):
        return list(self) + list(other)

    def __setitem__(self, key, object):
        self._data[key] = object

    def __getitem__(self, key):
        return self._data[key]

    def __delitem__(self, key):
        del self._data[key]

    def __setattr__(self, item, value):
        # this test allows attributes to be set in the __init__ method
        if self.__dict__.has_key('_initialized') == False or self.__dict__['_initialized'] == False:
            self.__dict__[item] = value
        # any normal attributes are handled normally when they already exist
        # this would happen if they are given different values after initilization
        elif self.__dict__.has_key(item):       
            self.__dict__[item] = value
        # attributes added after initialization are stored in _data
        else:
            self._set_data_item(item, value)

    def _set_data_item(self, item, value):
        self._data[item] = value

    def __getstate__(self):
        return {'_data': self.__dict__['_data']}

    def __setstate__(self, state):
        self.__dict__['_data'] = state['_data']

    def __getattr__(self, key):
        try:
            return self._data[key]
        except KeyError:
            raise AttributeError(key)

    def __delattr__(self, key):
        if self.__dict__.has_key(key):
            del self.__dict__[key]
        else:
            try:
                del self._data[key]
            except KeyError:
                raise AttributeError(key)

    def __contains__(self, key):
        return key in self._data

    def update(self, value):
        self._data.update(value)

    def get(self, key, default=None):
        if key in self:
            return self[key]
        else:
            return default

    def keys(self):
        return self._data.keys()

    def has_key(self, key):
        return self._data.has_key(key)

    def clear(self):
        self._data.clear()

    def todict(self):
        return self._data

class OrderedDict(dict):
    """A dict that returns keys/values/items in the order they were added."""

    def __init__(self, ____sequence=None, **kwargs):
        self._list = []
        if ____sequence is None:
            if kwargs:
                self.update(**kwargs)
        else:
            self.update(____sequence, **kwargs)

    def clear(self):
        self._list = []
        dict.clear(self)

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        return OrderedDict(self)

    def sort(self, *arg, **kw):
        self._list.sort(*arg, **kw)

    def update(self, ____sequence=None, **kwargs):
        if ____sequence is not None:
            if hasattr(____sequence, 'keys'):
                for key in ____sequence.keys():
                    self.__setitem__(key, ____sequence[key])
            else:
                for key, value in ____sequence:
                    self[key] = value
        if kwargs:
            self.update(kwargs)

    def setdefault(self, key, value):
        if key not in self:
            self.__setitem__(key, value)
            return value
        else:
            return self.__getitem__(key)

    def __iter__(self):
        return iter(self._list)

    def values(self):
        return [self[key] for key in self._list]

    def itervalues(self):
        return iter(self.values())

    def keys(self):
        return list(self._list)

    def iterkeys(self):
        return iter(self.keys())

    def items(self):
        return [(key, self[key]) for key in self.keys()]

    def iteritems(self):
        return iter(self.items())

    def __setitem__(self, key, object):
        if key not in self:
            self._list.append(key)
        dict.__setitem__(self, key, object)

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self._list.remove(key)

    def pop(self, key, *default):
        present = key in self
        value = dict.pop(self, key, *default)
        if present:
            self._list.remove(key)
        return value

    def popitem(self):
        item = dict.popitem(self)
        self._list.remove(item[0])
        return item

class HtmlAttributeHolder(object):
    def __init__(self, **kwargs):
        self._cleankeys(kwargs)
        #: a dictionary that represents html attributes
        self.attributes = kwargs
        
    def setm(self, **kwargs ):
        self._cleankeys(kwargs)
        self.attributes.update(kwargs)
    
    def set(self, key, value):
        if key.endswith('_'):
            key = key[:-1]
        self.attributes[key] = value
        
    def setdefault(self, key, value):
        if key.endswith('_'):
            key = key[:-1]
        self.attributes.setdefault(key, value)
    
    def add(self, key, value):
        """
            Creates a space separated string of attributes.  Mostly for the
            "class" attribute.
        """
        if key.endswith('_'):
            key = key[:-1]
        if self.attributes.has_key(key):
            self.attributes[key] = self.attributes[key] + ' ' + value
        else:
            self.attributes[key] = value
        
    def delete(self, key):
        if key.endswith('_'):
            key = key[:-1]
        del self.attributes[key]
    
    def get(self, key, defaultval = NotGiven):
        try:
            if key.endswith('_'):
                key = key[:-1]
            return self.attributes[key]
        except KeyError:
            if defaultval is not NotGiven:
                return defaultval
            raise
    
    def _cleankeys(self, dict):
        """
            When using kwargs, some attributes can not be sent directly b/c
            they are Python key words (i.e. "class") so that have to be sent
            in with an underscore at the end (i.e. "class_").  We want to
            remove the underscore before saving
        """
        for key, val in dict.items():
            if key.endswith('_'):
                del dict[key]
                dict[key[:-1]] = val