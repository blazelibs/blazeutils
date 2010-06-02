from pysutils import posargs_limiter

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
