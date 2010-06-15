import sys
import traceback
from blazeutils.helpers import tolist

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
traceback_depth_in = tb_depth_in

def traceback_depth(tb=None):
    if tb == None:
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
    if '.' in our_import:
        last_part = our_import.split('.').pop()
    else:
        last_part = our_import
    if not str(exc).endswith(last_part):
        raise
