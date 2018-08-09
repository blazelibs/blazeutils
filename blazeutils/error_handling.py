from __future__ import absolute_import
from __future__ import unicode_literals

import re
import sys

from blazeutils.helpers import tolist
from blazeutils.decorators import deprecate


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
traceback_depth_in = tb_depth_in  # noqa: E305


@deprecate('tb_depth_in(), traceback_depth() deprecated, its a bad idea')
def traceback_depth(tb=None):
    if tb is None:
        _, _, tb = sys.exc_info()
    depth = 0
    while tb.tb_next is not None:
        depth += 1
        tb = tb.tb_next
    return depth


def raise_unexpected_import_error(our_import, exc):
    """
        See if our_import caused the import error, if not, raise the last
        exception
    """
    if not _uie_matches(our_import, str(exc)):
        raise


_identifier = r'[^\d\W]\w+'
_dotted_path_rx = re.compile(r'\'?({0}(\.{0})*)\'?$'.format(_identifier), re.UNICODE)


def _uie_matches(our_import, exc_str):
    match = _dotted_path_rx.search(exc_str)
    # make sure there is a match before using .group attr
    if match is None:
        return False
    dotted_part = match.group(1)
    return our_import.endswith(dotted_part)
