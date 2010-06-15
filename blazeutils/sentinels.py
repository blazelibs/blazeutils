class NotGivenBase(object):
    """ an empty sentinel object that acts like None """
    
    def __str__(self):
        return 'None'
    
    def __unicode__(self):
        return u'None'
    
    def __nonzero__(self):
        return False
    
    def __ne__(self, other):
        if other is None or isinstance(other, NotGivenBase):
            return False
        return True
    
    def __eq__(self, other):
        if other is None or isinstance(other, NotGivenBase):
            return True
        return False
NotGiven = NotGivenBase()

class NotGivenIterBase(NotGivenBase):
    """ an empty sentinel object that acts like an empty list """
    def __str__(self):
        return '[]'
    
    def __unicode__(self):
        return u'[]'
    
    def __nonzero__(self):
        return False
    
    def __ne__(self, other):
        if other == [] or isinstance(other, NotGivenBase):
            return False
        return True
    
    def __eq__(self, other):
        if other == [] or isinstance(other, NotGivenBase):
            return True
        return False
    
    # we also want to emulate an empty list
    def __iter__(self):
        return self
    
    def next(self):
        raise StopIteration
    
    def __len__(self):
        return 0
NotGivenIter = NotGivenIterBase()

def is_notgiven(object):
    """ checks for either of our NotGiven sentinel objects """
    return isinstance(object, NotGivenBase)
