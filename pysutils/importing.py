import sys
import site
from os import path
import imp

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

# from werkzeug
def import_string(import_name, silent=False):
    """Imports an object based on a string.  This is useful if you want to
    use import paths as endpoints or something similar.  An import path can
    be specified either in dotted notation (``xml.sax.saxutils.escape``)
    or with a colon as object delimiter (``xml.sax.saxutils:escape``).

    If `silent` is True the return value will be `None` if the import fails.

    :param import_name: the dotted name for the object to import.
    :param silent: if set to `True` import errors are ignored and
                   `None` is returned instead.
    :return: imported object
    """
    # force the import name to automatically convert to strings
    if isinstance(import_name, unicode):
        import_name = str(import_name)
    try:
        if ':' in import_name:
            module, obj = import_name.split(':', 1)
        elif '.' in import_name:
            module, obj = import_name.rsplit('.', 1)
        else:
            return __import__(import_name)
        # __import__ is not able to handle unicode strings in the fromlist
        # if the module is a package
        if isinstance(obj, unicode):
            obj = obj.encode('utf-8')
        return getattr(__import__(module, None, None, [obj]), obj)
    except (ImportError, AttributeError):
        if not silent:
            raise