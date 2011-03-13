from os import path
from nose.tools import eq_
from blazeutils import find_path_package, import_split, posargs_limiter

def test_find_path_package():
    import email
    import email.mime
    import email.mime.base
    import test
    assert email is find_path_package(email.__file__)
    assert email is find_path_package(path.dirname(email.__file__))
    assert email is find_path_package(email.mime.__file__)
    assert email is find_path_package(email.mime.base.__file__)
    assert None is find_path_package(path.join(path.dirname(__file__), 'notthere.py'))
    assert None is find_path_package(path.dirname(__file__))
    assert test is find_path_package(path.join(path.dirname(test.__file__), 'output', 'test_cgi'))

    drive, casepath = path.splitdrive(path.dirname(email.__file__))
    if drive:
        assert email is find_path_package(drive.upper() + casepath)
        assert email is find_path_package(drive.lower() + casepath)

def test_import_split():
    assert import_split('path') == ('path', None, None)
    assert import_split('path.part.object') == ('path.part', 'object', None)
    assert import_split('path.part:object') == ('path.part', 'object', None )
    eq_(import_split('path.part:object.attribute'),
        ('path.part', 'object', 'attribute') )
    
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