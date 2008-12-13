import sys
import site
import random
from os import path
from pprint import PrettyPrinter

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
        projdir = path.dirname(path.normpath(projdir))
    
    # any args are considered paths that need to be joined to the
    # projdir to get to the correct directory.
    libpaths = []
    for lpath in args:
        libpaths.append(path.join(projdir, path.normpath(lpath)))
    
    # add the path to sys.path with preference over everything that currently
    # exists in sys.path
    backupSysPath = sys.path
    sys.path = []
    site.addsitedir(projdir)
    for lpath in libpaths:
        site.addsitedir(lpath)
    sys.path.extend(backupSysPath)

def setup_virtual_env(pysmvt_libs_module, lib_path, *args):
    # load the system library that corresponds with the version requested
    libs_mod = __import__(pysmvt_libs_module)
    prependsitedir(libs_mod.__file__)
    
    # load the local 'libs' directory
    prependsitedir(lib_path, *args)
