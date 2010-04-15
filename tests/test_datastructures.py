from pysutils import DumbObject, OrderedProperties, OrderedDict, \
    HtmlAttributeHolder

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