from pysutils import safe_strftime

def test_safe_strftime():
    assert safe_strftime(None) == ''
