from __future__ import absolute_import
from __future__ import unicode_literals
import six.moves.cPickle as pickle
import random

from blazeutils.datastructures import DumbObject, OrderedProperties, OrderedDict, \
    LazyOrderedDict, LazyDict, UniqueList
from six.moves import range


# leave this here it ensures that LazyDict is available from .datastructures
# even though the code was moved to .containers.
assert LazyDict


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


class TestOrderedDict(object):

    def test_ordereddict(self):
        o = OrderedDict((('a', 'a'), ('b', 'b')))

        # add a bunch of random junk so that a passing test is less likely to be accidentally valid
        for value in range(random.randint(100, 1000)):
            o[value] = value

        o['c'] = 'c'

        for i, v in enumerate(o.values()):
            if i == 0:
                assert v == 'a'
            elif i == 1:
                assert v == 'b'

        assert o.values()[-1] == 'c'

    def test_ordereddict_pickle(self):
        o = OrderedDict((('a', 'a'), ('b', 'b')))

        # add a bunch of random junk so that a passing test is less likely to be accidentally valid
        for value in range(random.randint(100, 1000)):
            o[value] = value

        o['c'] = 'c'

        ostr = pickle.dumps(o, pickle.HIGHEST_PROTOCOL)
        o = pickle.loads(ostr)

        for i, v in enumerate(o.values()):
            if i == 0:
                assert v == 'a'
            elif i == 1:
                assert v == 'b'

        assert o.values()[-1] == 'c'

    def test_ordereddict_lazy(self):

        o = LazyOrderedDict((('a', 'a'), ('b', 'b')))
        for i, v in enumerate(o.values()):
            if i == 0:
                assert v == 'a'
            elif i == 1:
                assert v == 'b', v
        assert o.a == 'a'
        assert o.b == 'b'
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
    ul.extend([6, 7, 7, 1])
    assert ul == [1, 2, 3, 5, 6, 7]
