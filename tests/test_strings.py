from nose.tools import eq_
from pysutils import StringIndenter, simplify_string, case_cw2us, case_mc2us, \
    case_us2mc, case_us2cw, reindent, randchars, randnumerics, randhash

def test_string_indent_helper():
    s = StringIndenter()
    
    s.inc('1.0')
    s('1.1')
    s('1.2')
    s.dec('2.0')
    s.inc('2.1', level=3)
    s.dec('3.0')
    output = s.get()
    expected = """
1.0
    1.1
    1.2
2.0
            2.1
3.0
    """.strip()
    eq_(expected, output)
    
def test_simplify_string():
    assert simplify_string('foo bar') == 'foo-bar'
    
def test_case_changes():
    eq_(case_cw2us('FooBar'), 'foo_bar')
    eq_(case_mc2us('fooBar'), 'foo_bar')
    eq_(case_us2mc('foo_bar'), 'fooBar')
    eq_(case_us2cw('foo_bar'), 'FooBar')
    
def test_reindent():
    expected = """    foo
    bar"""
    test = """
foo
        bar
    """.strip()
    eq_(reindent(test, 4), expected)

def test_randoms():
    assert len(randchars()) == 12
    assert len(randchars(4)) == 4
    assert randchars() != randchars()
    assert len(randnumerics()) == 12
    assert len(randnumerics(4)) == 4
    assert randnumerics() != randnumerics()
    assert len(randhash()) == 32
    assert randhash() != randhash()
    