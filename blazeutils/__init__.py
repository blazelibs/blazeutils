# flake8: noqa

from __future__ import absolute_import
from os import path as osp

## legacy imports, future imports should use the full import path
from blazeutils.datastructures import DumbObject, OrderedProperties, OrderedDict, \
    HtmlAttributeHolder
from blazeutils.dates import safe_strftime
from blazeutils.decorators import decorator, curry
from blazeutils.error_handling import tb_depth_in, traceback_depth
from blazeutils.filesystem import randfile
from blazeutils.functional import posargs_limiter
from blazeutils.helpers import tolist, toset, grouper, is_empty, is_iterable, \
    multi_pop, pformat, pprint
from blazeutils.importing import find_path_package, find_path_package_name,\
    import_split, is_path_python_module, prependsitedir, setup_virtual_env
from blazeutils.numbers import moneyfmt, round_down_to_n
from blazeutils.sentinels import NotGiven, NotGivenBase, NotGivenIter, NotGivenIterBase, \
    is_notgiven
from .spreadsheets import XlwtHelper
from blazeutils.strings import StringIndenter, simplify_string, case_cw2us, \
    case_mc2us, case_us2cw, case_us2mc, randchars, \
    randhash, randnumerics, reindent, simplify_string
from blazeutils.version import VERSION
