from __future__ import absolute_import
from __future__ import unicode_literals

import random

import pytest
from six.moves import range
import six.moves.cPickle as pickle

from blazeutils.datastructures import DumbObject, OrderedProperties, OrderedDict, \
    LazyOrderedDict, LazyDict, UniqueList

# leave this here it ensures that LazyDict is available from .datastructures
# even though the code was moved to .containers.
assert LazyDict


def test_dumbobject():
    assert DumbObject(a=1).a == 1


class TestOrderedProps(object):
    def test_basics(self):
        o = OrderedProperties()
        o.a = 1
        o.b = 2
        for i, attr in enumerate(o):
            if i == 0:
                assert attr == 1
            else:
                assert attr == 2

    def test_list(self):
        o = OrderedProperties()
        o.a = 1
        o.b = 2

        assert list(o) == [1, 2]

    def test_add(self):
        o1 = OrderedProperties()
        o2 = OrderedProperties()

        o1.a = 1
        o1.c = 3
        o2.b = 2
        o2.d = 4

        result = o1 + o2

        assert result == [1, 3, 2, 4]

    def test_del(self):
        o = OrderedProperties()
        assert 'a' not in o
        o.a = 1
        assert 'a' in o
        del o.a
        assert 'a' not in o

    def test_del_item(self):
        o = OrderedProperties()
        assert 'a' not in o
        o.a = 1
        assert 'a' in o
        del o['a']
        assert 'a' not in o

    def test_pickle(self):
        o = OrderedProperties()
        o.a = 1
        o.b = 2

        ostr = pickle.dumps(o, pickle.HIGHEST_PROTOCOL)
        po = pickle.loads(ostr)

        assert po.a == 1
        assert po.b == 2
        assert list(po) == [1, 2]

    def test_attribute_error(self):
        o = OrderedProperties()
        with pytest.raises(AttributeError, match='foo'):
            o.foo

    def test_del_attribute_error(self):
        o = OrderedProperties()
        with pytest.raises(AttributeError, match='foo'):
            del o.foo

    def test_initilization(self):
        o = OrderedProperties(initialize=False)
        o.a = 1
        o._initialized = True
        o.b = 2

        assert o.a == 1
        assert list(o) == [2]

        del o.a

        try:
            o.a
            assert False, 'expected exception'
        except AttributeError:
            pass

    def test_update(self):
        o = OrderedProperties()
        o.a = 1
        o.update(dict(b=2))
        assert o.b == 2

        assert list(o) == [1, 2]

    def test_has_key(self):
        o = OrderedProperties()
        o.a = 1
        assert 'a' in o

    def test_clear(self):
        o = OrderedProperties()
        o.a = 1
        assert 'a' in o
        o.clear()
        assert 'a' not in o


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
