from __future__ import absolute_import
from __future__ import unicode_literals

import six.moves.cPickle as pickle

from blazeutils.containers import LazyDict, HTMLAttributes


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

    del o.c
    assert not hasattr(o, 'c')


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


class TestAttributes(object):

    def check_eq(self, expected, **kwargs):
        assert expected == kwargs

    def test_attribute_access(self):
        at = HTMLAttributes()
        at.name = 'foo'
        self.check_eq({'name': 'foo'}, **at)

    def test_underscore_attribute_access(self):
        at = HTMLAttributes()
        at.class_ = 'foo'
        self.check_eq({'class': 'foo'}, **at)

    def test_add_attribute_access_starting_with_nothing(self):
        at = HTMLAttributes()
        at.class_ += 'foo'
        at.class_ += 'bar'
        self.check_eq({'class': 'foo bar'}, **at)

    def test_add_attribute_access_staring_with_unicode(self):
        at = HTMLAttributes()
        at.class_ = 'foo'
        at.class_ += 'bar'
        self.check_eq({'class': 'foo bar'}, **at)

    def test_key_access(self):
        at = HTMLAttributes()
        at['name'] = 'foo'
        self.check_eq({'name': 'foo'}, **at)

    def test_underscore_key_access(self):
        at = HTMLAttributes()
        at['class_'] = 'foo'
        self.check_eq({'class': 'foo'}, **at)

    def test_key_access_starting_with_nothing(self):
        at = HTMLAttributes()
        at['class_'] += 'foo'
        at['class_'] += 'bar'
        self.check_eq({'class': 'foo bar'}, **at)

    def test_key_access_starting_with_unicode(self):
        at = HTMLAttributes()
        at['class_'] = 'foo'
        at['class_'] += 'bar'
        self.check_eq({'class': 'foo bar'}, **at)

    def test_init_from_dict(self):
        at = HTMLAttributes({'name': 'foo', 'class_': 'bar baz'})
        self.check_eq({'class': 'bar baz', 'name': 'foo'}, **at)

    def test_init_from_kwargs(self):
        at = HTMLAttributes(name='foo', class_='bar baz')
        self.check_eq({'class': 'bar baz', 'name': 'foo'}, **at)
