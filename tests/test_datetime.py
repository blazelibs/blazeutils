import datetime as dt

from blazeutils.dates import safe_strftime, ensure_datetime

def test_safe_strftime():
    assert safe_strftime(None) == ''

def test_ensure_datetime():
    dtm = dt.datetime.now()
    d = dt.date.today()

    assert ensure_datetime(dtm) is dtm
    nd = ensure_datetime(d)
    assert isinstance(nd, dt.datetime)
    assert dt.time(0, 0, 0) == nd.time()
    assert d == nd.date()
