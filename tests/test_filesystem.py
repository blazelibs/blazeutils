from os import path
from tempfile import gettempdir
from pysutils import randfile

def test_randfile():
    fpath = randfile(gettempdir(), '.txt')
    assert len(fpath) == 16
    fpath = randfile(gettempdir(), '.txt', fullpath=True)
    assert len(fpath) > 16
    assert path.isabs(fpath)