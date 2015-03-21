from __future__ import absolute_import
from __future__ import unicode_literals

from blazeutils.numbers import moneyfmt, decimalfmt, ensure_int, convert_int


def test_moneyfmt():
    assert moneyfmt('-0.02', neg='<', trailneg='>') == '<0.02>'
    assert decimalfmt('-1234567.8901', places=0, sep='.', dp='', neg='', trailneg='-') == '1.234.568-'
    # handles floats too
    assert decimalfmt(-1234567.8901) == '-1,234,567.89'


def test_ensure_int():
    assert ensure_int(10) == 10
    assert ensure_int('10') == 10
    assert ensure_int('foo') == 0
    assert ensure_int(None) == 0


def test_convert_int():
    assert convert_int(10) == 10
    assert convert_int('10') == 10
    assert convert_int('foo') is None
    assert convert_int(None) is None
