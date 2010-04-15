from pysutils.datastructures import OrderedProperties

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