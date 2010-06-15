from blazeutils.datastructures import DumbObject, OrderedProperties, OrderedDict, \
    HtmlAttributeHolder, LazyOrderedDict, LazyDict

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


def test_lazy_dict():

    o = LazyDict(a=1, b=2)
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
