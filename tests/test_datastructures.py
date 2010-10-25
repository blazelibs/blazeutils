import cPickle as pickle
from blazeutils.datastructures import DumbObject, OrderedProperties, OrderedDict, \
    HtmlAttributeHolder, LazyOrderedDict, LazyDict, UniqueList

def test_dumbobject():
    assert DumbObject(a=1).a == 1

def test_orderedproperties():
    o = OrderedProperties()
    o.a = 1
    o.b = 2
    for i, attr in enumerate(o):
        if i == 0:
            assert attr == 1
        else:
            assert attr == 2

def test_ordereddict():
    o = OrderedDict(a=1, b=2)
    for i, v in enumerate(o.values()):
        if i == 0:
            assert v == 1
        else:
            assert v == 2

def test_ordereddict_pickle():
    o = OrderedDict(a=1, b=2)

    ostr = pickle.dumps(o, pickle.HIGHEST_PROTOCOL)
    o = pickle.loads(ostr)

    for i, v in enumerate(o.values()):
        if i == 0:
            assert v == 1
        else:
            assert v == 2


def test_ordereddict_lazy():

    o = LazyOrderedDict(a=1, b=2)
    for i, v in enumerate(o.values()):
        if i == 0:
            assert v == 1
        else:
            assert v == 2, v
    assert o.a == 1
    assert o.b == 2
    o.c = 3
    assert o.c == 3, o.c
    assert o['c'] == 3
    try:
        o.d
        assert False
    except AttributeError:
        pass

def test_lazy_dict():

    o = LazyDict(a=1, b=2)

    ostr = pickle.dumps(o, pickle.HIGHEST_PROTOCOL)
    o = pickle.loads(ostr)

    assert o.a == 1
    assert o.b == 2
    o.c = 3
    assert o.c == 3, o.c
    assert o['c'] == 3
    try:
        o.d
        assert False
    except AttributeError:
        pass

def test_lazy_dict_with_setter_property():

    class CustomLD(LazyDict):
        def __init__(self):
            self._x = True
            LazyDict.__init__(self)
        def getx(self):
            return self._x
        def setx(self, value):
            self._x = value
        x = property(getx, setx)

    o = CustomLD()
    assert o.x
    o.x = False
    assert not o.x

def test_unique_list():
    ul = UniqueList([1, 1, 2, 2, 3])
    ul.append(2)
    ul.append(5)
    ul.extend([6,7, 7, 1])
    assert ul == [1,2,3,5,6,7]
