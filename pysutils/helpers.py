from pprint import PrettyPrinter
from pysutils.datastructures import OrderedDict

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

def is_iterable(possible_iterable):
    if isinstance(possible_iterable, basestring):
        return False
    try:
        iter(possible_iterable)
        return True
    except TypeError:
        return False
    
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