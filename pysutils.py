import sys
import site
import random
import hashlib
from os import path
from pprint import PrettyPrinter
import re
import imp
import time
from functools import update_wrapper
import inspect, itertools

def tolist(x, default=[]):
    if x is None:
        return default
    if not isinstance(x, (list, tuple)):
        return [x]
    else:
        return x
    
def toset(x):
    if x is None:
        return set()
    if not isinstance(x, set):
        return set(tolist(x))
    else:
        return x

def pprint( stuff, indent = 4):
    pp = PrettyPrinter(indent=indent)
    print pp.pprint(stuff)

def pformat(stuff, indent = 4):
    pp = PrettyPrinter(indent=indent)
    return pp.pformat(stuff)

def randchars(n = 12):
    charlist = u'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return u''.join(random.choice(charlist) for _ in range(n))

def randnumerics(n = 12):
    charlist = '0123456789'
    return u''.join(random.choice(charlist) for _ in range(n))

def randhash():
    return hashlib.md5(str(random.random()) + str(time.clock())).hexdigest()

def randfile(fdir, ext=None, length=12, fullpath=False):
    if not ext:
        ext = ''
    else:
        ext = '.' + ext.lstrip('.')
    while True:
        file_name = randchars(length) + ext
        fpath = path.join(fdir, file_name)
        if not path.exists(fpath):
            if fullpath:
                return fpath
            else:
                return file_name

def prependsitedir(projdir, *args):
    """
        like sys.addsitedir() but gives the added directory preference
        over system directories.  The paths will be normalized for dots and
        slash direction before being added to the path.

        projdir: the path you want to add to sys.path.  If its a
            a file, the parent directory will be added

        *args: additional directories relative to the projdir to add
            to sys.path.
    """
    libpath = None

    # let the user be lazy and send a file, we will convert to parent directory
    # of file
    if path.isfile(projdir):
        projdir = path.dirname(projdir)

    projdir = path.abspath(projdir)

    # any args are considered paths that need to be joined to the
    # projdir to get to the correct directory.
    libpaths = []
    for lpath in args:
        libpaths.append(path.join(projdir, path.normpath(lpath)))

    # add the path to sys.path with preference over everything that currently
    # exists in sys.path
    syspath_orig = set(sys.path)
    site.addsitedir(projdir)
    for lpath in libpaths:
        site.addsitedir(lpath)
    syspath_after = set(sys.path)
    new_paths = list(syspath_after.difference(syspath_orig))
    sys.path = new_paths + sys.path

def setup_virtual_env(pysmvt_libs_module, lib_path, *args):
    # load the system library that corresponds with the version requested
    libs_mod = __import__(pysmvt_libs_module)
    prependsitedir(libs_mod.__file__)
    
    # load the local 'libs' directory
    prependsitedir(lib_path, *args)



class NotGivenBase(object):
    """ an empty sentinel object that acts like None """
    
    def __str__(self):
        return 'None'
    
    def __unicode__(self):
        return u'None'
    
    def __nonzero__(self):
        return False
    
    def __ne__(self, other):
        if other is None or isinstance(other, NotGivenBase):
            return False
        return True
    
    def __eq__(self, other):
        if other is None or isinstance(other, NotGivenBase):
            return True
        return False
NotGiven = NotGivenBase()

class NotGivenIterBase(NotGivenBase):
    """ an empty sentinel object that acts like an empty list """
    def __str__(self):
        return '[]'
    
    def __unicode__(self):
        return u'[]'
    
    def __nonzero__(self):
        return False
    
    def __ne__(self, other):
        if other == [] or isinstance(other, NotGivenBase):
            return False
        return True
    
    def __eq__(self, other):
        if other == [] or isinstance(other, NotGivenBase):
            return True
        return False
    
    # we also want to emulate an empty list
    def __iter__(self):
        return self
    
    def next(self):
        raise StopIteration
    
    def __len__(self):
        return 0
NotGivenIter = NotGivenIterBase()

def is_iterable(possible_iterable):
    if isinstance(possible_iterable, basestring):
        return False
    try:
        iter(possible_iterable)
        return True
    except TypeError:
        return False

def is_notgiven(object):
    """ checks for either of our NotGiven sentinel objects """
    return isinstance(object, NotGivenBase)
    
def is_empty(value):
    """ a boolean test except 0 and False are considered True """
    if not value and value is not 0 and value is not False:
        return True
    return False

def multi_pop(d, *args):
    """ pops multiple keys off a dict like object """
    retval = {}
    for key in args:
        if d.has_key(key):
            retval[key] = d.pop(key)
    return retval

# next four functions from: http://code.activestate.com/recipes/66009/
def case_cw2us(x):
    """ capwords to underscore notation """
    return re.sub(r'(?<=[a-z])[A-Z]|(?<!^)[A-Z](?=[a-z])', r"_\g<0>", x).lower()

def case_mc2us(x):
    """ mixed case to underscore notation """
    return case_cw2us(x)

def case_us2mc(x):
    """ underscore to mixed case notation """
    return re.sub(r'_([a-z])', lambda m: (m.group(1).upper()), x)

def case_us2cw(x):
    """ underscore to capwords notation """
    s = case_us2mc(x)
    return s[0].upper()+s[1:]

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

def find_path_package(thepath):
    """
        Takes a file system path and returns the module object of the python
        package the said path belongs to. If the said path can not be
        determined, it returns None.
    """
    pname = find_path_package_name(thepath)
    if not pname:
        return None
    return __import__(pname, globals(), locals(), [''])

_py_suffixes = [suffix for suffix, _, _ in imp.get_suffixes()]

def find_path_package_name(thepath):
    """
        Takes a file system path and returns the name of the python package
        the said path belongs to.  If the said path can not be determined, it
        returns None.
    """
    module_found = False
    last_module_found = None
    continue_ = True
    while continue_:
        module_found = is_path_python_module(thepath)
        next_path = path.dirname(thepath)
        if next_path == thepath:
            continue_ = False
        if module_found:
            init_names = ['__init__%s' % suffix.lower() for suffix in _py_suffixes]
            if path.basename(thepath).lower() in init_names:
                last_module_found = path.basename(path.dirname(thepath))
            else:
                last_module_found = path.basename(thepath)
        if last_module_found and not module_found:
            continue_ = False
        thepath = next_path
    return last_module_found

def is_path_python_module(thepath):
    """
        Given a path, find out of the path is a python module or is inside
        a python module.
    """
    thepath = path.normpath(thepath)

    if path.isfile(thepath):
        base, ext = path.splitext(thepath)
        if ext in _py_suffixes:
            return True
        return False

    if path.isdir(thepath):
        for suffix in _py_suffixes:
            if path.isfile(path.join(thepath, '__init__%s' % suffix)):
                return True
    return False

def import_split(import_name):
    """ takes a dotted string path and returns the components:
        import_split('path') == 'path', None, None
        import_split('path.part.object') == 'path.part', 'object', None
        import_split('path.part:object') == 'path.part', 'object', None
        import_split('path.part:object.attribute')
            == 'path.part', 'object', 'attribute'
    """
    obj = None
    attr = None
    if ':' in import_name:
        module, obj = import_name.split(':', 1)
        if '.' in obj:
            obj, attr = obj.rsplit('.', 1)
    elif '.' in import_name:
        module, obj = import_name.rsplit('.', 1)
    else:
        module = import_name
    return module, obj, attr

def format_argspec_plus(fn, grouped=True):
    """Returns a dictionary of formatted, introspected function arguments.

    A enhanced variant of inspect.formatargspec to support code generation.

    fn
       An inspectable callable or tuple of inspect getargspec() results.
    grouped
      Defaults to True; include (parens, around, argument) lists

    Returns:

    args
      Full inspect.formatargspec for fn
    self_arg
      The name of the first positional argument, varargs[0], or None
      if the function defines no positional arguments.
    apply_pos
      args, re-written in calling rather than receiving syntax.  Arguments are
      passed positionally.
    apply_kw
      Like apply_pos, except keyword-ish args are passed as keywords.

    Example::

      >>> format_argspec_plus(lambda self, a, b, c=3, **d: 123)
      {'args': '(self, a, b, c=3, **d)',
       'self_arg': 'self',
       'apply_kw': '(self, a, b, c=c, **d)',
       'apply_pos': '(self, a, b, c, **d)'}

    """
    spec = callable(fn) and inspect.getargspec(fn) or fn
    args = inspect.formatargspec(*spec)
    if spec[0]:
        self_arg = spec[0][0]
    elif spec[1]:
        self_arg = '%s[0]' % spec[1]
    else:
        self_arg = None
    apply_pos = inspect.formatargspec(spec[0], spec[1], spec[2])
    defaulted_vals = spec[3] is not None and spec[0][0-len(spec[3]):] or ()
    apply_kw = inspect.formatargspec(spec[0], spec[1], spec[2], defaulted_vals,
                                     formatvalue=lambda x: '=' + x)
    if grouped:
        return dict(args=args, self_arg=self_arg,
                    apply_pos=apply_pos, apply_kw=apply_kw)
    else:
        return dict(args=args[1:-1], self_arg=self_arg,
                    apply_pos=apply_pos[1:-1], apply_kw=apply_kw[1:-1])

def unique_symbols(used, *bases):
    used = set(used)
    for base in bases:
        pool = itertools.chain((base,),
                               itertools.imap(lambda i: base + str(i),
                                              xrange(1000)))
        for sym in pool:
            if sym not in used:
                used.add(sym)
                yield sym
                break
        else:
            raise NameError("exhausted namespace for symbol base %s" % base)

def decorator(target):
    """A signature-matching decorator factory."""

    def decorate(fn):
        spec = inspect.getargspec(fn)
        names = tuple(spec[0]) + spec[1:3] + (fn.func_name,)
        targ_name, fn_name = unique_symbols(names, 'target', 'fn')

        metadata = dict(target=targ_name, fn=fn_name)
        metadata.update(format_argspec_plus(spec, grouped=False))

        code = 'lambda %(args)s: %(target)s(%(fn)s, %(apply_kw)s)' % (
                metadata)
        decorated = eval(code, {targ_name:target, fn_name:fn})
        decorated.func_defaults = getattr(fn, 'im_func', fn).func_defaults
        return update_wrapper(decorated, fn)
    return update_wrapper(decorate, target)

def curry(fn, *args, **kwargs):
    """
    Decorator that returns a function that keeps returning functions
    until all arguments are supplied; then the original function is
    evaluated.
    """
    argscount = fn.func_code.co_argcount
    cargs = []
    def tocall(*args):
        cargs = tocall.cargs + list(args)
        tocall.cargs = cargs
        if len(tocall.cargs) < argscount:
            return tocall
        else:
            fnargs = tuple(tocall.cargs)
            tocall.cargs = []
            return fn(*fnargs)
    tocall.cargs = cargs
    return tocall

def posargs_limiter(func, *args):
    """ takes a function a positional arguments and sends only the number of
    positional arguments the function is expecting
    """
    posargs = inspect.getargspec(func)[0]
    length = len(posargs)
    if inspect.ismethod(func):
        length -= 1
    if length == 0:
        return func()
    return func(*args[0:length])
    
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

class StringIndenter(object):

    def __init__(self):
        self.output = []
        self.level = 0
        self.indent_with = '    '
    
    def dec(self, value):
        self.level -= 1
        return self.render(value)
            
    def inc(self, value):
        self.render(value)
        self.level += 1
    
    def __call__(self, value, **kwargs):
        self.render(value)
    
    def render(self, value, **kwargs):
        self.output.append('%s%s' % (self.indent(**kwargs), value) )
    
    def indent(self, level = None):
        if level == None:
            return self.indent_with * self.level
        else:
            return self.indent_with * self.level
    
    def get(self):
        retval = '\n'.join(self.output)
        self.output = []
        return retval

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

    def sort(self, fn=None):
        self._list.sort(fn)

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

def safe_strftime(value, format='%m/%d/%Y %H:%M', on_none=''):
    if value is None:
        return on_none
    return value.strftime(format)
    
def simplify_string(s, length=None, replace_with='-'):
    #$slug = str_replace("&", "and", $string);
    # only keep alphanumeric characters, underscores, dashes, and spaces
    s = re.compile( r'[^\/a-zA-Z0-9_ \\-]').sub('', s)
    # replace forward slash, back slash, underscores, and spaces with dashes
    s = re.compile(r'[\/ \\_]+').sub(replace_with, s)
    # make it lowercase
    s = s.lower()
    if length is not None:
        return s[:length-1].rstrip(replace_with)
    else:
        return s

def reindent(s, numspaces):
    """ reinidents a string (s) by the given number of spaces (numspaces) """
    leading_space = numspaces * ' '
    lines = [ leading_space + line.strip()
                for line in s.splitlines()]
    return '\n'.join(lines)
    
def tb_depth_in(depths):
    """
    looks at the current traceback to see if the depth of the traceback
    matches any number in the depths list.  If a match is found, returns
    True, else False.
    """
    depths = tolist(depths)
    if traceback_depth() in depths:
        return True
    return False

def traceback_depth(tb=None):
    if tb == None:
        _, _, tb = sys.exc_info()
    depth = 0
    while tb.tb_next is not None:
        depth += 1
        tb = tb.tb_next
    return depth

def grouper(records, *fields):
    grouped_records = OrderedDict()
    
    def setup_grouping(record, *fields):
        location = []
        for field in fields:
            location.append(record[field])
        save_at_location(record, location)
    
    def save_at_location(record, location):
        at = grouped_records
        final_kpos = len(location)-1
        for kpos, key in enumerate(location):
            if kpos != final_kpos:
                if not at.has_key(key):
                    at[key] = OrderedDict()
                at = at[key]
            else:
                if not at.has_key(key):
                    at[key] = []
                at[key].append(record)

    for record in records:
        setup_grouping(record, *fields)
    return grouped_records

try:
    import xlwt
    
    class XlwtHelper(object):
        """
            code from : http://panela.blog-city.com/pyexcelerator_xlwt_cheatsheet_create_native_excel_from_pu.htm
        """
        
        STYLE_FACTORY = {}
        FONT_FACTORY = {}
        
        def __init__(self):
            self.ws = None
            
        def set_sheet(self, ws):
            self.ws = ws
        
        def write(self, row, col, data, style=None):
            """
            Write data to row, col of worksheet (ws) using the style
            information.
    
            Again, I'm wrapping this because you'll have to do it if you
            create large amounts of formatted entries in your spreadsheet
            (else Excel, but probably not OOo will crash).
            """
            ws = self.ws
            if not ws:
                raise Exception('you must use set_sheet() before write()')
                
            if style:
                s = self.get_style(style)
                ws.write(row, col, data, s)
            else:
                ws.write(row, col, data)
        
        def get_style(self, style):
            """
            Style is a dict maping key to values.
            Valid keys are: background, format, alignment, border
    
            The values for keys are lists of tuples containing (attribute,
            value) pairs to set on model instances...
            """
            #print "KEY", style
            style_key = tuple(style.items())
            s = self.STYLE_FACTORY.get(style_key, None)
            if s is None:
                s = xlwt.XFStyle()
                for key, values in style.items():
                    if key == "background":
                        p = xlwt.Pattern()
                        for attr, value in values:
                            p.__setattr__(attr, value)
                        s.pattern = p
                    elif key == "format":
                        s.num_format_str = values
                    elif key == "alignment":
                        a = xlwt.Alignment()
                        for attr, value in values:
                            a.__setattr__(attr, value)
                        s.alignment = a
                    elif key == "border":
                        b = xlwt.Formatting.Borders()
                        for attr, value in values:
                            b.__setattr__(attr, value)
                        s.borders = b
                    elif key == "font":
                        f = self.get_font(values)
                        s.font = f
                self.STYLE_FACTORY[style_key] = s
            return s
    
        def get_font(self, values):
            """
            'height' 10pt = 200, 8pt = 160
            """
            font_key = values
            f = self.FONT_FACTORY.get(font_key, None)
            if f is None:
                f = xlwt.Font()
                for attr, value in values:
                    f.__setattr__(attr, value)
                self.FONT_FACTORY[font_key] = f
            return f
except ImportError:
    pass