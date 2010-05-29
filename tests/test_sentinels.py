from pysutils import NotGiven, NotGivenIter, is_notgiven
from pysutils.helpers import is_iterable

def test_notgiven():
    assert not None
    assert not NotGiven
    assert NotGiven != False
    assert None != False
    assert NotGiven is NotGiven
    assert NotGiven == NotGiven
    assert None is not NotGiven
    assert None == NotGiven
    assert not None != NotGiven
    assert NotGiven == None
    assert str(NotGiven) == 'None'
    assert unicode(NotGiven) == u'None'

def test_notgiveniter():
    assert not NotGivenIter
    assert NotGivenIter != False
    assert NotGivenIter is NotGivenIter
    assert NotGivenIter == NotGivenIter
    assert NotGivenIter == NotGiven
    assert NotGiven == NotGivenIter
    assert not [] != NotGivenIter
    assert NotGivenIter == []
    assert str(NotGivenIter) == '[]'
    assert unicode(NotGivenIter) == u'[]'
    assert is_iterable(NotGivenIter)
    assert len(NotGivenIter) == 0

    for v in NotGivenIter:
        self.fail('should emulate empty')
    else:
        assert True, 'should emulate empty'
    
def test_is_notgiven():
    assert is_notgiven(NotGiven)
    assert is_notgiven(NotGivenIter)
    assert not is_notgiven(None)