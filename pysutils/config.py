from pysutils.datastructures import OrderedProperties, OrderedDict

class QuickSettings(OrderedProperties):
    def __init__(self, initialize=True):
        self._locked = False
        OrderedProperties.__init__(self, initialize)
    
    def lock(self):
        self._locked = True
        for child in self._data.values():
            if isinstance(child, QuickSettings):
                child.lock()
    
    def unlock(self):
        self._locked = False
        for child in self._data.values():
            if isinstance(child, QuickSettings):
                child.unlock()
    
    def __getattr__(self, key):
        if not self._data.has_key(key):
            if not self._locked:
                self._data[key] = QuickSettings()
            else:
                raise AttributeError("object has no attribute '%s' (object is locked)" % key)
        return self._data[key]
    
    def update(self, ____sequence=None, **kwargs):
        if ____sequence is not None:
            if hasattr(____sequence, 'keys'):
                for key in ____sequence.keys():
                    try:
                        self.get(key).update(____sequence[key])
                    except (AttributeError, ValueError), e:
                        if "object has no attribute 'update'" not in str(e) and "need more than 1 value to unpack" not in str(e):
                            raise
                        self.__setitem__(key, ____sequence[key])
            else:
                for key, value in ____sequence:
                    self[key] = value
        if kwargs:
            self.update(kwargs)
    
    def set_dotted(self, key, value):
        """
                qs.set_dotted('foo.bar', 'baz')
            
            is equivelent to:
            
                qs.foo.bar = baz
        """
        parts = key.split('.')
        cobj = self
        if len(parts) > 1:
            key = parts.pop()
            for name in parts:
                cobj = getattr(cobj, name)
        setattr(cobj, key, value)
        
    def get_dotted(self, key):
        """
                obj = qs.get_dotted('foo.bar.baz')
            
            is equivelent to:
            
                obj = qs.foo.bar.baz
        """
        parts = key.split('.')
        cobj = self
        for attr in parts:
            cobj = getattr(cobj, attr)
        return cobj
    
    def expandkeys(self):
        retval = OrderedDict()
        for k in self.keys():
            v = getattr(self, k)
            if isinstance(v, QuickSettings):
                for vk, vv in v.expandkeys().iteritems():
                    new_key = '%s.%s' % (k, vk)
                    retval[new_key] = vv
            else:
                retval[k] = v
        return retval
    
    @property
    def pformat(self):
        retval = ''
        for k, v in self.expandkeys().iteritems():
            retval += '%s = %s\n' % (k, v)
        return retval.rstrip()