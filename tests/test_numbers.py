from pysutils import moneyfmt
from pysutils.numbers import decimalfmt

def test_moneyfmt():
    assert moneyfmt('-0.02', neg='<', trailneg='>') == '<0.02>'
    assert decimalfmt('-1234567.8901', places=0, sep='.', dp='', neg='', trailneg='-') == '1.234.568-'