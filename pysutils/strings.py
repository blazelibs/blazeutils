import hashlib
import random
import re
import time

class StringIndenter(object):

    def __init__(self):
        self.output = []
        self.level = 0
        self.indent_with = '    '
    
    def dec(self, value, level=None):
        self.level -= 1
        return self.render(value, level=level)
            
    def inc(self, value, level=None):
        self.render(value, level=level)
        self.level += 1
    
    def __call__(self, value, level=None):
        self.render(value, level=level)
    
    def render(self, value, level=None):
        self.output.append('%s%s' % (self.indent(level), value) )
    
    def indent(self, level = None):
        if level == None:
            return self.indent_with * self.level
        else:
            return self.indent_with * level
    
    def get(self):
        retval = '\n'.join(self.output)
        self.output = []
        return retval
    
def simplify_string(s, length=None, replace_with='-'):
    #$slug = str_replace("&", "and", $string);
    # only keep alphanumeric characters, underscores, dashes, and spaces
    s = re.compile( r'[^\/a-zA-Z0-9_ \\-]').sub('', s)
    # replace forward slash, back slash, underscores, and spaces with dashes
    s = re.compile(r'[\/ \\_]+').sub(replace_with, s)
    # make it lowercase
    s = s.lower()
    if length is not None:
        return s[:length-1].rstrip(replace_with)
    else:
        return s

# next four functions from: http://code.activestate.com/recipes/66009/
def case_cw2us(x):
    """ capwords to underscore notation """
    return re.sub(r'(?<=[a-z])[A-Z]|(?<!^)[A-Z](?=[a-z])', r"_\g<0>", x).lower()

def case_mc2us(x):
    """ mixed case to underscore notation """
    return case_cw2us(x)

def case_us2mc(x):
    """ underscore to mixed case notation """
    return re.sub(r'_([a-z])', lambda m: (m.group(1).upper()), x)

def case_us2cw(x):
    """ underscore to capwords notation """
    s = case_us2mc(x)
    return s[0].upper()+s[1:]
    
def reindent(s, numspaces):
    """ reinidents a string (s) by the given number of spaces (numspaces) """
    leading_space = numspaces * ' '
    lines = [ leading_space + line.strip()
                for line in s.splitlines()]
    return '\n'.join(lines)
    
def randchars(n = 12, chartype='alphanumeric', alphacase='both', unique=False):
    if alphacase == 'both':
        alphalist = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    elif alphacase == 'upper':
        alphalist = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    elif alphacase == 'lower':
        alphalist = 'abcdefghijklmnopqrstuvwxyz'
    else:
        raise ValueError('alphacase "%s" not recognized' % alphacase)
        
    if chartype == 'alphanumeric':
        charlist = alphalist + '0123456789'
    elif chartype == 'alpha':
        charlist = alphalist
    elif chartype == 'numeric':
        charlist = '0123456789'
    else:
        raise ValueError('chartype "%s" not recognized' % chartype)

    retval = []
    for _ in range(n):
        chosen = random.choice(charlist)
        if unique:
            charlist = charlist.replace(chosen, '')
        retval.append(chosen)
    return u''.join(retval)

def randnumerics(n = 12):
    charlist = '0123456789'
    return u''.join(random.choice(charlist) for _ in range(n))

def randhash():
    return hashlib.md5(str(random.random()) + str(time.clock())).hexdigest()