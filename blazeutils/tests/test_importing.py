from __future__ import absolute_import
from __future__ import unicode_literals

from os import path

from blazeutils.importing import find_path_package, import_split, import_string

src_dirname = path.dirname(path.dirname(path.dirname(__file__)))


def test_find_path_package():
    import email
    import email.mime
    import email.mime.base
    import test
    assert email is find_path_package(email.__file__)
    assert email is find_path_package(path.dirname(email.__file__))
    assert email is find_path_package(email.mime.__file__)
    assert email is find_path_package(email.mime.base.__file__)
    assert None is find_path_package(path.join(src_dirname, 'notthere.py'))
    assert None is find_path_package(src_dirname)
    assert test is find_path_package(path.join(path.dirname(test.__file__), 'output', 'test_cgi'))

    drive, casepath = path.splitdrive(path.dirname(email.__file__))
    if drive:
        assert email is find_path_package(drive.upper() + casepath)
        assert email is find_path_package(drive.lower() + casepath)


def test_import_split():
    assert import_split('path') == ('path', None, None)
    assert import_split('path.part.object') == ('path.part', 'object', None)
    assert import_split('path.part:object') == ('path.part', 'object', None)
    assert import_split('path.part:object.attribute') == \
        ('path.part', 'object', 'attribute')


class TestImportString(object):

    def test_string_import(self):
        assert import_string('blazeutils.importing.import_split') is import_split

