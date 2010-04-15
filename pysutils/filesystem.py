from os import path
from pysutils.strings import randchars

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