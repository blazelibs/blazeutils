import re


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
