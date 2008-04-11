"""
clearquest.util: module for any miscellaneous utilities (methods, classes etc)
"""

#===============================================================================
# Imports
#===============================================================================

import os
from inspect import ismethod
from functools import wraps
from itertools import repeat

#===============================================================================
# Globals
#===============================================================================

__rcsid__ = '$Id$'
__rcsurl__ = '$URL$'
__copyright__ = 'Copyright 2008 OnResolve Ltd'

#===============================================================================
# Helper Methods
#===============================================================================

def listToMap(l):
    return dict(zip(l, repeat(1)))

def symbols(c):
    return [ s for s in dir(c) if not s.startswith('_') ]

def symbolMap(c):
    return listToMap(symbols(c))

def toList(l):
    return [l] if not type(l) == list else l

def iterable(i):
    return (i,) if not hasattr(i, '__iter__') else i

def concat(arg1, *other):
    if not other:
        return arg1
    args = [arg1] + list(other)
    s = ["{fn CONCAT(%s, %s)}" % ((args.pop(len(args)-2), args.pop()))]
    for v in reversed(args):
        s.insert(0, "{fn CONCAT(%s, " % v)
        s.append(")}")
    return "".join(s)

def joinPath(*args):
    return os.path.normpath(os.path.join(*args))

def connectStringToMap(connectString):
    m = dict([ v.split('=') for v in connectString.split(';') ])
    if 'DATABASE' in m:
        m['DB'] = m['DATABASE']
    elif 'DB' in m:
        m['DATABASE'] = m['DB']
    elif 'SID' in m:
        m['DATABASE'] = m['SID']
    else:
        raise ValueError, "could not find value for 'DATABASE', 'DB' or 'SID' "\
                          " in connection string"
    return m

def spliceWork(dataOrSize, nchunks):
    if type(dataOrSize) in (list, tuple):
        max = len(dataOrSize)
    else:
        max = dataOrSize
    size = max / nchunks
    results = []
    results.append((0, size))
    for i in range(1, nchunks-1):
        results.append((i*size, (i+1)*size))
    results.append(((nchunks-1)*size, max-1))
    return results

#===============================================================================
# Decorators
#===============================================================================
def cache(f):
    @wraps(f)
    def newf(*_args, **_kwds):
        self = _args[0]
        cacheName = '_cache_' + f.func_name
        if not hasattr(self, cacheName):
            self.__dict__[cacheName] = dict()
        cache = self.__dict__[cacheName]
        id = '%s,%s' % (repr(_args[1:]), repr(_kwds))
        if not id in cache:
            # If there's a method with the same name but prefixed with a '_',
            # use this to derive the cacheable value.  Otherwise, use the method
            # we've been asked to decorate.  We take this approach to support
            # certain API methods that need to be wrapped with @returns, which
            # makes them unsuitable to also be wrapped with @cache.  In these
            # situations, the public API method will be an empty 'pass' block
            # with a @cache decorator, and the actual API method wrapped with
            # @returns(<typename>) with be prefixed with a '_'.
            if hasattr(self, '_' + f.func_name):
                args = _args[1:]
                method = getattr(self, '_' + f.func_name)
            else:
                args = _args
                method = f
            cache[id] = method(*args, **_kwds)
        return cache[id]
    return newf

def cache2(f):
    @wraps(f)
    def newf(*_args, **_kwds):
        self = _args[0] if _args else None
        try:
            if ismethod(getattr(self, f.func_name)):
                c = self.__dict__
        except:
            c = f.__dict__
        
        cache = c.setdefault('_cache_%s' % f.func_name, dict())
        id = '%s,%s' % (repr(_args[1:]), repr(_kwds))
        
        if not id in cache:
            # If there's a method with the same name but prefixed with a '_',
            # use this to derive the cacheable value.  Otherwise, use the method
            # we've been asked to decorate.  We take this approach to support
            # certain API methods that need to be wrapped with @returns, which
            # makes them unsuitable to also be wrapped with @cache.  In these
            # situations, the public API method will be an empty 'pass' block
            # with a @cache decorator, and the actual API method wrapped with
            # @returns(<typename>) with be prefixed with a '_'.
            if self:
                if hasattr(self, '_' + f.func_name):
                    args = _args[1:]
                    method = getattr(self, '_' + f.func_name)
                else:
                    args = _args
                    method = f
            cache[id] = method(*args, **_kwds)
        return cache[id]
    return newf


#===============================================================================
# Classes
#===============================================================================

class Dict(dict):
    def __init__(self, *args, **kwds):
        dict.__init__(self, *args)
        self.__dict__.update(**kwds)
    def __getattr__(self, name):
        return self.__getitem__(name)
    def __setattr__(self, name, value):
        return self.__setitem__(name, value)    
        

