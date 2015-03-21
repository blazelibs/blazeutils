from __future__ import absolute_import
from __future__ import unicode_literals

from os import path
from blazeutils.strings import randchars


def randfile(fdir, ext=None, length=12, fullpath=False):
    if not ext:
        ext = ''
    else:
        ext = '.' + ext.lstrip('.')
    while True:
        file_name = randchars(length) + ext
        fpath = path.join(fdir, file_name)
        if not path.exists(fpath):
            if fullpath:
                return fpath
            else:
                return file_name
