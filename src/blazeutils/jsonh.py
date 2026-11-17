"""
json helpers

can't name the module just "json" because 'import json' will not work
"""

###
#   json code from Flask:
###

# try to load the best simplejson implementation available.
json_available = True
try:
    import simplejson as jsonmod
except ImportError:
    try:
        import json as jsonmod  # noqa
    except ImportError:
        json_available = False


def assert_have_json():
    """Helper function that fails if JSON is unavailable."""
    if not json_available:
        raise RuntimeError('simplejson required but not installed')
