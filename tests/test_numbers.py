from nose.tools import eq_

from blazeutils import moneyfmt
from blazeutils.numbers import decimalfmt

def test_moneyfmt():
    assert moneyfmt('-0.02', neg='<', trailneg='>') == '<0.02>'
    assert decimalfmt('-1234567.8901', places=0, sep='.', dp='', neg='', trailneg='-') == '1.234.568-'
    # handles floats too
    eq_(decimalfmt(-1234567.8901), '-1,234,567.89')
