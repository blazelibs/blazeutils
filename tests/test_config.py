from nose.tools import eq_
from pysutils.config import QuickSettings

class Base(QuickSettings):
    
    def __init__(self):
        QuickSettings.__init__(self)
        
        # name of the website/application
        self.name.full = 'full'
        self.name.short = 'short'
        
        # application modules from our application or supporting applications
        self.modules.users.enabled = True
        self.modules.users.var2 = 'not bar'
        self.modules.users.routes = []
        self.modules.users.level2.var2 = 'not bar'
        self.modules.users.level3 = 'string value to merge'
        self.modules.users.level4 = (('var2', 'not bar'), ('var3', 'baz'))
        self.modules.users.level5.level1.var1.notlikely = 'foo'
        self.modules.users.level5.level2.var1 = 'not_bar'
        self.modules.apputil.enabled = True
        self.modules.inactivemod.enabled = False
        
        #######################################################################
        # ROUTING
        #######################################################################
        # default routes
        self.routing.routes = [1, 2]
        
        # route prefix
        self.routing.prefix = ''
        
        #######################################################################
        # DATABASE
        #######################################################################
        self.db.echo = False
        
        #######################################################################
        # SESSIONS
        #######################################################################
        #beaker session options
        #http://wiki.pylonshq.com/display/beaker/Configuration+Options
        self.beaker.type = 'dbm'
        self.beaker.data_dir = 'session_cache'

        #######################################################################
        # TEMPLATE & VIEW
        #######################################################################
        self.template.default = 'default.html'
        self.template.admin = 'admin.html'
        self.trap_view_exceptions = True
        
        #######################################################################
        # LOGGING & DEBUG
        #######################################################################
        # currently support 'debug' & 'info'
        self.logging.levels = ()
        
        # no more values can be added
        self.lock()
        
class Default(Base):

    def __init__(self):
        Base.__init__(self)
        
        # supporting applications
        self.supporting_apps = ['rcsappbase']
        
        # application modules from our application or supporting applications
        self.unlock()
        self.modules.contentbase.enabled = True
        self.modules.lagcontent.enabled = True
        self.lock()
        
        #######################################################################
        # ROUTING
        #######################################################################
        self.routing.routes.extend([3,4])
        
        #######################################################################
        # DATABASE
        #######################################################################
        self.db.echo = True
        
        #######################################################################
        # LOGGING & DEBUG
        #######################################################################
        self.logging.levels = ('info', 'debug')
        self.trap_view_exceptions = False
        self.hide_exceptions = False

class UserSettings(QuickSettings):
    
    def __init__(self):
        QuickSettings.__init__(self)
        
        self.routes = ([
            '/test1',
            '/test2',
        ])
        
        self.var1 = 'foo'
        self.var2 = 'bar'
        
        self.level2.var1 = 'foo'
        self.level2.var2 = 'bar'
        
        self.level3.var1 = 'foo'
        self.level3.var2 = 'bar'
        
        self.level4.var1 = 'foo'
        self.level4.var2 = 'bar'
        
        self.level5.level1.var1 = 'foo'
        self.level5.level2.var1 = 'bar'
        self.level5.level2.var2 = 'baz'
        self.level5.level3.var1 = 'bob'
        
        # no more values can be added
        self.lock()

class TestQuickSettings(object):

    def test_level1(self):
        es = QuickSettings()
        es.a = 1
        assert es.a == 1
        
    def test_level2(self):
        es = QuickSettings()
        es.a.a = 1
        assert es.a.a == 1
        
    def test_email(self):
        es = QuickSettings()
        es.email.smtp.server = 'example.com'
        es.email.smtp.user_name = 'myself'
        es.email.smtp.password = 'pass'
        
        assert es.email.smtp.server == 'example.com'
        assert es.email.smtp.user_name == 'myself'
        assert es.email.smtp.password == 'pass'
        
    def test_settings(self):
        s = Default()
        
        assert s.name.full == 'full'
        assert s.name.short == 'short'
        assert s.modules.keys() == ['users', 'apputil','inactivemod','contentbase', 'lagcontent'], s.modules.keys()
        assert s.routing.routes == [1,2,3,4]
        
        assert s.db.echo == True
    
        assert s.logging.levels == ('info', 'debug')
        assert s.trap_view_exceptions == False
        assert s.hide_exceptions == False
        
        assert s.template.default == 'default.html'
        assert s.template.admin == 'admin.html'
        
        assert s.beaker.type == 'dbm'
        assert s.beaker.data_dir == 'session_cache'

    def test_lock(self):
        s = Default()
        
        try:
            foo = s.not_there
        except AttributeError, e:
            assert str(e) == "object has no attribute 'not_there' (object is locked)"
        else:
            assert False, "lock did not work, expected AttributeError"
        
        # make sure lock went to children
        try:
            foo = s.db.not_there
        except AttributeError, e:
            assert str(e) == "object has no attribute 'not_there' (object is locked)"
        else:
            assert False, "lock did not work on child, expected AttributeError"

    def test_unlock(self):
        s = Default()
        s.unlock()
        
        s.new_attr = 'new_attr'
        s.db.new_attr = 'new_attr'
        
        assert s.db.new_attr == 'new_attr'
        assert s.new_attr == 'new_attr'
        
        s.lock()
        
        try:
            foo = s.not_there
        except AttributeError, e:
            assert str(e) == "object has no attribute 'not_there' (object is locked)"
        else:
            assert False, "lock did not work, expected AttributeError"
        
        # make sure lock went to children
        try:
            foo = s.db.not_there
        except AttributeError, e:
            assert str(e) == "object has no attribute 'not_there' (object is locked)"
        else:
            assert False, "lock did not work on child, expected AttributeError"
        
    def test_dict_convert(self):
        s = Default()
        
        # beaker would need a dictionary, so lets see if it works
        d = {
            'type' : 'dbm',
            'data_dir' : 'session_cache'
        }
        
        assert dict(s.beaker) == d
        assert s.beaker.todict() == d
    
    def test_hasattr(self):
        s = Default()
        
        assert hasattr(s, 'alajsdf') == False
        assert hasattr(s, 'alajsdf') == False
        
        s.unlock()
        assert hasattr(s, 'alajsdf') == True        
    
    def test_modules(self):
        s = Default()
        
        s.unlock()
        s.modules.fatfingeredmod.enabledd = True
        s.lock()
        
        allmods = mods = ['users', 'apputil', 'inactivemod', 'contentbase', 'lagcontent', 'fatfingeredmod']
        eq_( mods, s.modules.keys() )
        
        eq_( len(mods), len([v for v in s.modules]))
        eq_( len(mods), len(s.modules))
        
        eq_( len(mods), len(s.modules.todict()))
        eq_( len(allmods), len(s.modules.todict()))
        
        assert 'users' in s.modules
    
    def test_merge(self):
        s = Default()
        us = UserSettings()
        
        try:
            eq_(s.modules.users.var1, 'foo')
        except AttributeError, e:
            assert str(e) == "object has no attribute 'var1' (object is locked)"
        else:
            assert False, "expected AttributeError for 'var1'"
    
        eq_(s.modules.users.var2, 'not bar')
        eq_(us.var2, 'bar')
        eq_(len(us.routes), 2)
        eq_(us.level2.var1, 'foo')
        eq_(us.level2.var2, 'bar')
        eq_(us.level3.var2, 'bar')
        eq_(us.level4.var2, 'bar')
        eq_(us.level5.level1.var1, 'foo')
        eq_(us.level5.level2.var1, 'bar')
        eq_(us.level5.level2.var2, 'baz')
        eq_(us.level5.level3.var1, 'bob')
        
        us.update(s.modules.users)
        s.modules['users'] = us
        
        eq_(s.modules.users.var2, 'not bar')
        eq_(s.modules.users.var1, 'foo')
        eq_(len(s.modules.users.routes), 0)
        eq_(s.modules.users.level2.var1, 'foo')
        eq_(s.modules.users.level2.var2, 'not bar')
        eq_(s.modules.users.level3, 'string value to merge')
        eq_(s.modules.users.level4.var1, 'foo')
        eq_(s.modules.users.level4.var2, 'not bar')
        eq_(s.modules.users.level4.var3, 'baz')
        eq_(s.modules.users.level5.level1.var1.notlikely, 'foo')
        eq_(s.modules.users.level5.level2.var1, 'not_bar')
        eq_(s.modules.users.level5.level2.var2, 'baz')
        
        eq_(s.modules.users.enabled, True)

def test_set_dotted():
    qs = QuickSettings()
    qs.set_dotted('foo.bar.wow', 'baz')
    qs.lock()
    assert qs.foo.bar.wow == 'baz'
    
    qs = QuickSettings()
    qs.set_dotted('foo', 'baz')
    qs.lock()
    assert qs.foo == 'baz'
    
    qs = QuickSettings()
    qs.set_dotted('', 'baz')