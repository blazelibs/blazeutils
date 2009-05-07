import sys
import site
import random
from os import path
from pprint import PrettyPrinter
import re

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
    
def randchars(n = 12):
    charlist = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choice(charlist) for _ in range(n))

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