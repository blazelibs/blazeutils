from __future__ import absolute_import

from blazeutils.functional import posargs_limiter
import blazeutils.functional as func


def test_posargs_limiter():
    def take0():
        return 0

    def take1(first):
        return first

    def take2(first, second):
        return first + second

    def take3(first, second, third):
        return first + second + third
    assert posargs_limiter(take0, 1, 2, 3) == 0
    assert posargs_limiter(take1, 1, 2, 3) == 1
    assert posargs_limiter(take2, 1, 2, 3) == 3
    assert posargs_limiter(take3, 1, 2, 3) == 6

    class TheClass(object):
        def take0(self):
            return 0

        def take1(self, first):
            return first

        def take2(self, first, second):
            return first + second

        def take3(self, first, second, third):
            return first + second + third
    tc = TheClass()
    assert posargs_limiter(tc.take0, 1, 2, 3) == 0
    assert posargs_limiter(tc.take1, 1, 2, 3) == 1
    assert posargs_limiter(tc.take2, 1, 2, 3) == 3
    assert posargs_limiter(tc.take3, 1, 2, 3) == 6


def test_compose():
    assert func.compose(lambda _: 'Python')(0.99) == 'Python'
    assert func.compose(lambda x: x + 1, lambda x: x - 1)(0) == 0
    assert func.compose(lambda x: x - 1, lambda x: x * 2)(1) == 1
    assert func.compose(lambda x: x * 2, lambda x: x - 1)(1) == 0


def test_count_iter():
    assert func.len_iter([]) == 0
    assert func.len_iter([1]) == 1
    assert func.len_iter([2]) == 1
    assert func.len_iter([1, 2]) == 2
    assert func.len_iter({1, 2}) == 2
    assert func.len_iter({1: 2, 3: 4}) == 2
    assert func.len_iter(x for x in [1, 2, 9]) == 3


def test_first_where():
    assert func.first_where(lambda _: False, []) is None
    assert func.first_where(lambda _: True, []) is None
    assert func.first_where(lambda _: False, [1]) is None
    assert func.first_where(lambda _: True, [1]) == 1
    assert func.first_where(lambda x: x % 2 == 0, [1, 3, 3, 7, 9, 44, 3]) == 44
    assert func.first_where(lambda x: x % 2 == 0, (x for x in [1, 3, 3, 7, 9, 44, 3])) == 44


def test_partition_list():
    test_list = [1, 2, 3, 4, 5]
    assert func.partition_list(lambda x: x < 3, test_list) == ([1, 2], [3, 4, 5])
    assert func.partition_list(lambda x: x < 4, test_list) == ([1, 2, 3], [4, 5])
    assert func.partition_list(lambda x: x < 10, test_list) == ([1, 2, 3, 4, 5], [])
    assert func.partition_list(lambda x: x < 1, test_list) == ([], [1, 2, 3, 4, 5])


def test_unzip():
    assert func.unzip([(1, 'a', '!'), (2, 'b', '@')]) == [[1, 2], ['a', 'b'], ['!', '@']]
    assert func.unzip([(1, 'a', '!'), (2, 'b')]) == [[1, 2], ['a', 'b']]


def test_flatten():
    assert func.flatten([]) == []
    assert func.flatten([[1], [2, 3], [4]]) == [1, 2, 3, 4]


def test_split_every():
    assert list(func.split_every(1, [])) == []
    assert list(func.split_every(1, [1])) == [[1]]
    assert list(func.split_every(1, [1, 2])) == [[1], [2]]
    assert list(func.split_every(2, [1, 2])) == [[1, 2]]
    assert list(func.split_every(3, [1, 2])) == [[1, 2]]
    assert list(func.split_every(2, [1, 2, 3])) == [[1, 2], [3]]


def test_unique():
    assert list(func.unique([])) == []
    assert list(func.unique([5, 4, 4, 3, 4, 2, 1])) == [5, 4, 3, 2, 1]
    assert list(func.unique('Lorem ipsum dolor')) == list('Lorem ipsudl')
    assert list(func.unique('AbaCBc', key=str.lower)) == list('AbC')
