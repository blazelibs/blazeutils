from blazeutils import curry, decorator

def test_curry():
    
    @curry
    def myfunc(a, b, c):
        return a+b+c;
    
    f = myfunc(1)
    f = f(2)
    assert f(3) == 6
    
def test_decorator():
    
    @decorator
    def mydec(fn, toadd):
        return 4 + fn(toadd)
    
    @mydec
    def myfunc(toreturn):
        return toreturn
    
    assert myfunc(5) == 9