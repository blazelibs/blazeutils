from __future__ import absolute_import
from __future__ import unicode_literals

import csv
import difflib
from pprint import PrettyPrinter
import six
import time

from blazeutils.datastructures import OrderedDict
from blazeutils.sentinels import NotGivenIter


def tolist(x, default=NotGivenIter):
    if default is NotGivenIter:
        default = []
    if x is None:
        return default
    if not isinstance(x, (list, tuple)):
        return [x]
    else:
        return x


def ensure_list(x, default=NotGivenIter):
    if default is NotGivenIter:
        default = []
    if x is None:
        return default
    if isinstance(x, tuple):
        return list(x)
    if not isinstance(x, list):
        return [x]
    else:
        return x


def ensure_tuple(x):
    if x is None:
        return ()
    if isinstance(x, tuple):
        return x
    return (x,)


def toset(x):
    if x is None:
        return set()
    if not isinstance(x, set):
        return set(tolist(x))
    else:
        return x


def pprint(stuff, indent=4):
    pp = PrettyPrinter(indent=indent)
    pp.pprint(stuff)


def pformat(stuff, indent=4):
    pp = PrettyPrinter(indent=indent)
    return pp.pformat(stuff)


def is_iterable(possible_iterable):
    if isinstance(possible_iterable, six.string_types):
        return False
    try:
        iter(possible_iterable)
        return True
    except TypeError:
        return False


def is_empty(value):
    """ a boolean test except 0 and False are considered True """
    if not value and value != 0 and value is not False:
        return True
    return False


def multi_pop(d, *args):
    """ pops multiple keys off a dict like object """
    retval = {}
    for key in args:
        if key in d:
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
                if key not in at:
                    at[key] = OrderedDict()
                at = at[key]
            else:
                if key not in at:
                    at[key] = []
                at[key].append(record)

    for record in records:
        setup_grouping(record, *fields)
    return grouped_records


class Tee(object):
    """A file-like that writes to all the file-likes it has."""

    def __init__(self, *files):
        """Make a Tee that writes to all the files in `files.`"""
        self.files = files

    def write(self, data):
        """Write `data` to all the files."""
        for f in self.files:
            f.write(data)


def csvtolist(inputstr):
    """ converts a csv string into a list """
    reader = csv.reader([inputstr], skipinitialspace=True)
    output = []
    for r in reader:
        output += r
    return output


class Timer(object):

    def __init__(self):
        self.timers = {}

    def start(self, name='default'):
        self.timers[name] = time.time()

    def elapsed(self, name='default'):
        return time.time() - self.timers[name]


def unique(seq, preserve_order=True):
    """
        Take a sequence and make it unique.  Not preserving order is faster, but
        that won't matter so much for most uses.

        copied from: http://www.peterbe.com/plog/uniqifiers-benchmark/uniqifiers_benchmark.py
    """
    if preserve_order:
        # f8 by Dave Kirby
        # Order preserving
        seen = set()
        seen_add = seen.add  # lookup method only once
        return [x for x in seq if x not in seen and not seen_add(x)]
    # f9
    # Not order preserving
    return list({}.fromkeys(seq).keys())


def prettifysql(sql):
    """Returns a prettified version of the SQL as a list of lines to help
    in creating a useful diff between two SQL statements."""
    pretty = []
    for line in sql.split('\n'):
        pretty.extend(["%s,\n" % x for x in line.split(',')])
    return pretty


def diff(actual, expected):
    """
        normalize whitespace in actual and expected and return unified diff
    """
    return '\n'.join(list(
        difflib.unified_diff(actual.splitlines(), expected.splitlines())
    ))
