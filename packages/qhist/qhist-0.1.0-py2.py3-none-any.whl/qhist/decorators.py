"""

Helper decorators for QHist.Core

TODO: IDEA: Lifecycle decorator at each stage...

"""

from __future__ import absolute_import
import functools

#===============================================================================
# UTILS
#===============================================================================

def get_base_proto(cls, func):
  """
  Helper function: for getter/setter of QHistV3, given the current class and function,
  return the base class to the last level before staticclass.
  This extra stage is needed because of the delegated class definition of
  QHistV3 which is too long.
  """
  ## Dig the base class, check from the getter's name
  name = getattr(cls.__base__, func.__name__).fget.__name__
  ## The name will be the same if it's not dig deep enough.
  if name == func.__name__:
    return get_base_proto(cls.__base__, func) # continue digging
  ## Dig deep enough, the name is '<lambda>'. 
  ## Return the child class before this point
  return cls 

#-------------------------------------------------------------------------------

def isinstance2( obj, t ):
  """
  Patched isinstance method to disable bool-is-int inheritance.

  >>> isinstance2( True, bool )
  True
  >>> isinstance2( True, int )
  False

  """
  if isinstance( t, (tuple,list)):
    need_bool = bool in t 
    need_int  = int in t 
  else:
    need_bool = t is bool 
    need_int  = t is int
  res = isinstance( obj, t ) # original result
  if not need_bool and need_int: # The particular case
    res &= not isinstance( obj, bool )
  return res

#===============================================================================

def override_getter_default(func):
  """
  Helper decorator for GETTER to return value from inherited class 
  if that value is not None, otherwise perform the computation in 
  the decorated method.
  """
  @functools.wraps(func)
  def wrap(self):
    ## Dig to the base class
    cls = get_base_proto(self.__class__, func)
    ## Obtain the value from staticclass
    val0 = getattr(super(cls, self), func.__name__)
    ## Check if it's EXPLICITLY set or not.
    if val0 is not None:
      return val0
    ## Not set explicitly, return the implicit value from func.
    return func(self)
  return wrap

#===============================================================================

def getter_plus_doc(prop):
  """
  Workaround for subclass.attr.getter (property overriding by subclass) 
  such that the documentation in subclass is also combined into that of
  the baseclass, allowing the doctest to pickup properly.
  """
  def wrap(fget):
    doc = prop.__doc__
    if fget.__doc__:
      doc += '\n'+fget.__doc__
    return type(prop)(fget, prop.fset, prop.fdel, doc)
  return wrap

#===============================================================================

def _equiplist_nullcheck_typecheck(*typecheck, **kwargs):
  """
  Decorator to do following jobs... 
  - Allow setter to treat single-value and list/tuple altogeter by equip single item to list.
  - Perform null-value-check for each item. (optional)
    - Note: However, the equipped-list is check for non-zero-length anyway
      regardless the nulllcheck flag.
  - Perform type-check for each item.

  """
  def decorator( setter ):
    @functools.wraps(setter)
    def fset( self, val ):
      # ## Reject immediate the <set> instance, usually bad, unless explicitly allow.
      # if not allowset and isinstance( val, set ):
      #   raise TypeError('Cannot equip type <set> into <list>')
      ## Allow now, as hidden feature, easy the decorator syntax

      ## Equip to tuple if needed
      if not isinstance( val, (tuple,set)):
        ## If it's already a list, prefer tuple.
        if isinstance( val, list ):
          val = tuple(val)
        else:
          val = (val,)  # Make a tuple. Dont do tuple(str)!
      ## Null-list check
      if not val:
        raise AttributeError('Require non-empty list for %r'%setter)
      ## Validation: Type & Value
      nullcheck = kwargs.get('nullcheck', True)
      for x in val:
        # Check type first, ease the unittest typecheck syntax.
        if not isinstance2( x, typecheck ):
          raise TypeError('Required type %r for %r. Received: %r' % (typecheck, setter, type(x)))
        if nullcheck and not x:
          raise AttributeError('Required non-null value for %r'%setter)
      ## Finally
      return setter( self, val )
    return fset
  return decorator

## Public
equiplist_nullcheck_typecheck = functools.partial(_equiplist_nullcheck_typecheck, nullcheck=True)
equiplist_typecheck           = functools.partial(_equiplist_nullcheck_typecheck, nullcheck=False)

#===============================================================================

def setter_isinstance(*types):
  """
  For decoration on class's setter. Perform isinstace check.
  """
  def decorator(setter):
    @functools.wraps(setter)
    def fset(self, val):
      if not isinstance2(val, types):
        raise TypeError('Required type %r for %r' % (types, setter))
      return setter(self, val)
    return fset 
  return decorator

#===============================================================================

def setter_from_return(shysetter):
  """
  For decoration on subclass's setter, for less verbose fset
  call on its motherclass.

  - Shysetter is decorated setter function, expected to perform
    validation / casting logic.
  - If there's a return value (i.e., not None), this will be used
    as setter's value.
  - Otherwise, the input is used directly. Thus, the overriding function may 
    purposefully return nothing, only doing its validation on the input.

  This consequently means the lazy-syntax is not usable if the setter truly
  wants to assign 'None' to that attribute.

  """
  @functools.wraps(shysetter)
  def wrap(self, val):
    ## Evaluate the value from explicit setter
    res = shysetter(self, val)
    ## Dig for the pre-staticclass
    cls = get_base_proto(self.__class__, shysetter)
    ## Get the property object
    attr = getattr(cls.__base__, shysetter.__name__)
    ## Call the setter, pass value to explicit setter than using directly.
    return attr.fset(self, res if res is not None else val)
  return wrap

#===============================================================================

def setter_from_return_plus_doc(prop):
  """
  Like above. 
  Also embed the simplify syntax where the return value of the overriding
  function (if not None) is pass to prop.fset.
  """
  def wrap(fset):
    doc = prop.__doc__
    if fset.__doc__:
      doc += '\n'+fset.__doc__
    return type(prop)(prop.fget, setter_from_return(fset), prop.fdel, doc)
  return wrap
