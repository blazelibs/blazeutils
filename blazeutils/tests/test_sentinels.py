from blazeutils.sentinels import NotGiven, NotGivenIter, is_notgiven
from blazeutils.helpers import is_iterable


def test_notgiven():
    assert not None
    assert not NotGiven
    assert NotGiven != False  # noqa
    assert NotGiven is NotGiven
    assert NotGiven == NotGiven
    assert None is not NotGiven
    assert None == NotGiven  # noqa
    assert not None != NotGiven  # noqa
    assert NotGiven == None  # noqa
    assert str(NotGiven) == 'None'
    assert str(NotGiven) == 'None'


def test_notgiveniter():
    assert not NotGivenIter
    assert NotGivenIter != False  # noqa
    assert NotGivenIter is NotGivenIter
    assert NotGivenIter == NotGivenIter
    assert NotGivenIter == NotGiven
    assert NotGiven == NotGivenIter
    assert not [] != NotGivenIter
    assert NotGivenIter == []
    assert str(NotGivenIter) == '[]'
    assert is_iterable(NotGivenIter)
    assert len(NotGivenIter) == 0

    for v in NotGivenIter:
        assert False, 'should emulate empty'
    else:
        assert True, 'should emulate empty'


def test_is_notgiven():
    assert is_notgiven(NotGiven)
    assert is_notgiven(NotGivenIter)
    assert not is_notgiven(None)
