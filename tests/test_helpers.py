from blazeutils import multi_pop, is_iterable, grouper, is_empty, pformat, \
    pprint, tolist, toset
from blazeutils.helpers import unique, prettifysql, diff
from blazeutils.strings import normalizews

def test_multi_pop():
    start = {'a':1, 'b':2, 'c':3}
    assert {'a':1, 'c':3} == multi_pop(start, 'a', 'c')
    assert start == {'b':2}

def test_is_iterable():
    assert is_iterable([])
    assert is_iterable(tuple())
    assert is_iterable({})
    assert not is_iterable('asdf')

def test_grouper():
    data = (
        {'color': 'red', 'number': 1, 'status':'active', 'link':'yes'},
        {'color': 'green', 'number': 2, 'status':'active', 'link':'yes'},
        {'color': 'blue', 'number': 3, 'status':'active', 'link':'no'},
        {'color': 'red', 'number': 4, 'status':'dead', 'link':'no'},
        {'color': 'green', 'number': 5, 'status':'dead', 'link':'yes'},
        {'color': 'blue', 'number': 6, 'status':'dead', 'link':'yes'},
    )
    assert grouper(data, 'status') == {
        'active' : [
            {'color': 'red', 'number': 1, 'status':'active', 'link':'yes'},
            {'color': 'green', 'number': 2, 'status':'active', 'link':'yes'},
            {'color': 'blue', 'number': 3, 'status':'active', 'link':'no'},
        ],
        'dead' : [
            {'color': 'red', 'number': 4, 'status':'dead', 'link':'no'},
            {'color': 'green', 'number': 5, 'status':'dead', 'link':'yes'},
            {'color': 'blue', 'number': 6, 'status':'dead', 'link':'yes'},
        ]
    }

def test_tolist():
    assert [1] == tolist(1)
    l = [1,2]
    assert l is tolist(l)
    t = (1,2)
    #TODO: this is wrong I think as we could actually be wanting a mutable list
    assert t == tolist(t)

def test_toset():
    assert set([1]) == toset(1)

def test_pformat():
    # just making sure no errors
    pformat('')

def test_pprint():
    # just making sure no errors
    pprint('')

def test_is_empty():
    assert is_empty('')
    assert not is_empty('1')
    assert not is_empty(0)
    assert not is_empty('0')
    #TODO: this seems weird, I would consider False empty
    assert not is_empty(False)

def test_unique():
    testdata = ['f','g','c','c', 'd','b','a','a']
    assert unique(testdata) == ['f', 'g', 'c', 'd', 'b', 'a']
    assert len(unique(testdata, False)) == 6

def test_diff():
    res = diff("one\ntwo\nthree", "one\n2\nthree").strip()
    expect = """
---

+++

@@ -1,3 +1,3 @@

 one
-two
+2
 three
""".strip()
    assert normalizews(res) == normalizews(expect)

def test_prettifysql():
    sql = """
    select foo,
    bar,
    baz from bill""".strip()
    expect = ['select foo,\n', ',\n', '    bar,\n', ',\n', '    baz from bill,\n']
    res = prettifysql(sql)
    assert expect == res
