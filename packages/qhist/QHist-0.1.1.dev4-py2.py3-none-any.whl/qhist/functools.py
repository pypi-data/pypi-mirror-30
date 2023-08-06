#!/usr/bin/env python

"""

Functools: Collections of useful functions/functors

"""

import hashlib
import time
import types
import inspect
from array import array
from itertools import izip_longest
from cStringIO import StringIO
from . import utils

#===============================================================================

def hashtimestamp():
  """
  Return a hash string based on curent timestamp.
  """
  return hashlib.sha1(str(int(time.time()*1e6))).hexdigest()

def prop(default, doc=""):
  """
  To be used inside the class to provide complete set of get/set/del in one go.

  Usage:

  >>> class Foo:
  ...   xbin = prop(10 , "Number of bins on x-axis")
  >>>
  >>> foo = Foo()
  >>> foo.xbin
  10
  >>> foo.xbin = 20
  >>> foo.xbin
  20

  """
  key = '__prop_'+hashtimestamp()
  getx = lambda self: getattr(self, key, default)
  setx = lambda self, val: setattr(self, key, val)
  delx = lambda self: delattr(self, key)
  return property(getx, setx, delx, doc)

#===============================================================================

## Metaclass: Unsettable
class Unsettable_type(type):
  def __setattr__(cls, attr, value):
    raise AttributeError("Setting attribute on this class is prohibited.")

def staticprop(key0, doc):
  """
  Like `prop` above, but allow the value to be set only once.
  The second set will raise AttributeError.
  Default value of every attribute is None.
  """
  key  = '_staticprop_'+key0
  getx = lambda self: getattr(self, key, None)
  delx = lambda self: delattr(self, key)
  def setx(self, value):
    """
    Guard here against already-set value
    """
    if hasattr(self, key):
      raise AttributeError('Attribute "%s" already set to %r' % (key0,getattr(self,key)))
    setattr(self, key, value)
  return property(getx, setx, delx, doc)

## instance method to be bound
def clear(self): # Same name as dict.clear
  """
  Reset all its attribute values to default.
  """
  for key in self.__slots__:
    if hasattr(self, key):
      delattr(self, key)

#-------------------------------------------------------------------------------

WIDTH_FULL    = 80
WIDTH_PANE    = 18
TEMPLATE_TOP  = '{:-^%i}'%WIDTH_FULL
TEMPLATE_HEAD = '        KEY       |   VALUE  ( * differs from default )'
TEMPLATE_ROW  = '{key:%i}| {star} {strval}'%WIDTH_PANE

## instance method to be bound
def __str__(self):

  def msg(key, defval, strval):
    star = '*' if defval!=strval else ' '
    if strval=='':
      strval = "''"
    key = key[:WIDTH_PANE]  # Cutoff width
    return TEMPLATE_ROW.format(**locals())

  def is_excluded(key):
    """Exclude these fields."""
    if key.startswith('_'): # Internal
      return True
    # if key in ('stats', 'wrapper', 'anchors', 'debug_messages', 'xarr', 'yarr', 'zarr'):  # Proxy
    #   return True
    return False

  def is_good_keyval(key, val):
    """Return True if this key-val should be listed."""
    if inspect.ismethod(val):  # method
      return False
    if isinstance(val, types.BuiltinFunctionType):
      return False
    return True

  cls = self.__class__
  default_instance = cls()
  fullmsg     = StringIO()
  addressmsg  = '%s.%s @ %s'%(cls.__module__, cls.__name__, hex(id(self)))
  print >>fullmsg, TEMPLATE_TOP.format(addressmsg)
  print >>fullmsg, TEMPLATE_HEAD
  for key in sorted(dir(self)):
    ## skip some entries by its key/val
    if is_excluded(key):
      continue

    ## Obtain the value, skip unnecessary ones.
    # val = getattr(self, key, None)
    try:
      val = getattr(self, key, None)
    except:
      val = 'EXCEPTION' # some attribute may not be ready yet
    if not is_good_keyval(key, val):
      continue
    strval = str(val)

    ## Start printing, prep default value & current value
    # defval = str(getattr(default_instance, key, None))
    try:
      defval = str(getattr(default_instance, key, None))
    except:
      defval = 'EXCEPTION'

    ## Pretty array
    if isinstance(val, array):
      print >>fullmsg, msg(key, defval, utils.pretty_array(val))
      continue

    ## Pretty paragraph string
    if '\n' in strval:
      defval = defval.strip().split('\n')
      strval = strval.strip().split('\n')
      for i, (dval, sval) in enumerate(izip_longest(defval, strval)):
        line = msg(key if i==0 else '', dval, sval)
        print >> fullmsg, line
      continue

    ## Break into several lines instead if it's a long list
    if len(strval)>60 and isinstance(val, (list, tuple)):
      for i,subval in enumerate(val):
        if i==0:
          line = msg(key, defval, str(subval))
        else:  # Omit the key+defval
          line = msg('', None, str(subval))
        print >>fullmsg, line
      continue      

    ## Default printing
    print >>fullmsg, msg(key, defval, strval)

  ## Finally, line break & return
  print >>fullmsg, '-'*WIDTH_FULL
  return fullmsg.getvalue()

#-------------------------------------------------------------------------------

def static_struct(typename, **kwargs):
  """
  Helper method to generate static class (inspired by collections.namedtuple),
  to be used exclusively in conjunction with staticprop.

  By static, it means:

  - All attribute is declared when class is created.
  - No attribute can be added furthermore, either at class-level or instance-level.
  - Attribute, once assigned, cannot be changed.
  - Unassigned attribute has 'None' as default value.

  Need this wrapper in order to properly generate ``__slots__`` with keys
  populated from staticprop

  Usage::

      >>> ## Define the class first
      >>> Cls = static_struct('MyClass', attr1='doc', attr2='doc2')
      >>> Cls
      <class 'qhist.functools.MyClass'>

      ## Dynamic properties are populated and inspectable.
      >>> [ x for x in dir(Cls) if not x.startswith('_') ]
      ['attr1', 'attr2', 'clear', 'keys', 'reset']

      ## Create class instance
      >>> obj = Cls()

      ## Default value is None
      >>> obj.attr1 == None
      True

      ## Set the value. Set again will fail
      >>> obj.attr1 = 42  # set the value
      >>> obj.attr1
      42
      >>> obj.attr1 = 555
      Traceback (most recent call last):
      ...
      AttributeError: Attribute "attr1" already set to 42

      ## Setting 'None' respect the no-repeat rule above
      >>> obj_none = Cls()
      >>> obj_none.attr1 = None
      >>> obj_none.attr1 = None # again
      Traceback (most recent call last):
      ...
      AttributeError: Attribute "attr1" already set to None

      ## Get/Set will fail if value is not defined.
      >>> obj.unknown
      Traceback (most recent call last):
      ...
      AttributeError: 'MyClass' object has no attribute 'unknown'
      >>> obj.unknown = 42
      Traceback (most recent call last):
      ...
      AttributeError: 'MyClass' object has no attribute 'unknown'

      ## Cannot set on the class directly, for value safety
      >>> Cls.attr1 = 'some value'
      Traceback (most recent call last):
      ...
      AttributeError: ...
      >>> Cls.attr1
      <property object at ...>

      ## Check independence between instance.
      >>> obj2 = Cls()
      >>> obj.attr2  = 111
      >>> obj2.attr2 = 222
      >>> obj.attr2
      111
      >>> obj2.attr2
      222

      ## This is like a dictionary
      >>> obj.keys()
      ['attr1', 'attr2']

      ## Use clear/reset to clear the values back to unset
      # This is independent for different instance
      >>> obj.clear()
      >>> obj.attr1 == obj.attr2 == None
      True
      >>> obj2.attr2
      222

      ## Attributes can be pretty-print as table
      >>> print(str(obj2))
      -------------------...
              KEY       |   VALUE  ( * differs from default )
      attr1             |   None
      attr2             | * 222
      -------------------------------------------------------...

  """
  ## Instantiate the props first
  props = { key:staticprop(key,val) for key,val in kwargs.iteritems() }

  ## Fixed the attributes of the class.
  # Setter-on-class is disable from this point.
  attrs = dict(props)
  attrs['clear'] = clear
  attrs['reset'] = clear # alias
  attrs['keys']  = lambda _: sorted(kwargs.keys())  # like a dictionary
  attrs['__slots__'] = tuple(['_staticprop_'+key for key in props]) # same as above
  attrs['__str__']   = __str__
  Cls = Unsettable_type(typename, (), attrs)
  return Cls

#===============================================================================
