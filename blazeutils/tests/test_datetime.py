import datetime as dt

from blazeutils.dates import safe_strftime, ensure_datetime, ensure_date, trim_mils


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


def test_ensure_date():
    dtm = dt.datetime.now()
    d = dt.date.today()

    assert ensure_date(dtm) == dtm.date()
    assert ensure_date(d) is d


class TestTrims(object):

    def test_trim_mils(self):
        thedate = dt.datetime(2010, 7, 19, 5, 6, 7, 501)
        assert trim_mils(thedate) == dt.datetime(2010, 7, 19, 5, 6, 7)

    def test_trim_mils_rounding(self):
        thedate = dt.datetime(2010, 7, 19, 5, 6, 7, 499)
        assert trim_mils(thedate, roundsecs=True) == dt.datetime(2010, 7, 19, 5, 6, 7)

        thedate = dt.datetime(2010, 7, 19, 5, 6, 7, 501)
        assert trim_mils(thedate, roundsecs=True) == dt.datetime(2010, 7, 19, 5, 6, 8)
