from nose.tools import eq_

from blazeutils import moneyfmt
from blazeutils.numbers import decimalfmt, ensure_int, convert_int

def test_moneyfmt():
    assert moneyfmt('-0.02', neg='<', trailneg='>') == '<0.02>'
    assert decimalfmt('-1234567.8901', places=0, sep='.', dp='', neg='', trailneg='-') == '1.234.568-'
    # handles floats too
    eq_(decimalfmt(-1234567.8901), '-1,234,567.89')

def test_ensure_int():
    eq_(ensure_int(10), 10)
    eq_(ensure_int('10'), 10)
    eq_(ensure_int('foo'), 0)

def test_convert_int():
    eq_(ensure_int(10), 10)
    eq_(ensure_int('10'), 10)
    eq_(convert_int('foo'), None)
