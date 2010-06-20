from nose.tools import eq_

from pysutils.datastructures import DumbObject, OrderedProperties, OrderedDict, \
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

def test_unique_list():
    ul = UniqueList([1, 1, 2, 2, 3])
    ul.append(2)
    ul.append(5)
    ul.extend([6,7, 7, 1])
    assert ul == [1,2,3,5,6,7]
