from __future__ import absolute_import

# Copyright (c) 2010-2018 Andrew Dalke Scientific, AB (Sweden)
# See the contents of "chemfp/__init__.py" for full license details.

# Backwards-compatibility support for older versions of Python

_missing = object
try:
    next = next
except NameError:
    def next(it, default=_missing):
        if default is _missing:
            return it.next()
        
        try:
            return it.next()
        except StopIteration:
            return default
        
try:
    enumerate("a", 1)
    enumerate = enumerate
except TypeError:
    _system_enumerate = enumerate
    def enumerate(seq, start=0):
        return ((i+start, value) for (i, value) in _system_enumerate(seq))

# Using the six API, though not the code.

try:
    unichr
except NameError:
    # Python 3.x
    PY2 = False
    PY3 = True
    text_type = str
    unicode_type = str
    string_types = (str,)
    bytes_type = bytes
    integer_types = (int,)
    filename_types = (str, bytes) # not in six
    class_types = (type,)
    def int2byte(c):
        return bytes((c,))

    ints2bytes = bytes
    def u(s):
        return s

    from io import BytesIO, StringIO
    xrange = range
    maketrans = bytes.maketrans
    exec("def raise_tb(exc, tb=None): raise exc from None")
    ## def raise_tb(exc, tb):
    ##     raise exc
    
    def iterbytes(s):
        for i in range(len(s)):
            yield s[i:i+1]

    izip = zip

    def indexbytes(buf, i):
        "return the byte at index i of buf as an integer"
        return buf[i]

    def myrepr(s):
        t = repr(s)
        if t.startswith("b"):
            return t[1:]
        return t
    
    def tobytes(x):
        return x.tobytes()
        
else:
    # Python 2.x
    import types, __builtin__, string
    PY2 = True
    PY3 = False
    text_type = unicode
    unicode_type = unicode
    bytes_type = str
    string_types = (str, unicode)
    integer_types = (int, long)
    filename_types = basestring
    int2byte = chr
    def ints2bytes(ints):
        return b"".join(map(chr, ints))
    def u(s):
        return unicode(s)
    from StringIO import StringIO as BytesIO, StringIO as StringIO

    class_types = (type, types.ClassType)

    xrange = __builtin__.xrange
    maketrans = string.maketrans
    exec("def raise_tb(exc, tb): raise exc, None, tb")
    def iterbytes(s):
        return iter(s)
    
    from itertools import izip
    
    def indexbytes(buf, i):
        "return the byte at index i of buf as an integer"
        return ord(buf[i])

    def myrepr(s):
        t = repr(s)
        if t.startswith("u"):
            return t[1:]
        return t

    def tobytes(x):
        return x.tostring()
    
