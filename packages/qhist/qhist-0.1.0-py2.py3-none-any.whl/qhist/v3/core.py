#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Further implementation of QHistV3, providing the descriptor tailored for
each attribute.

"""

from __future__ import absolute_import

import os
import types
import __main__
import ROOT
from datetime import datetime

from .. import logger, utils
from ..decorators import (
  equiplist_nullcheck_typecheck,
  equiplist_typecheck,
  override_getter_default,
  getter_plus_doc,
  setter_isinstance,
  setter_from_return_plus_doc
)
from .stats import Stats
from .anchors import Anchors
from .wrappers import Wrapper
from .proto import ProtoQHist

## 3rd-party
from PythonCK.decorators import lazy_property, report_debug

#==============================================================================

class QHist(ProtoQHist):
  """
  Provide suite of small test here since most of them are already tested in
  its origin's implementation, just to make sure that the inheritance does not
  interfere with the mechanism.

  Use `prefix` field since it's simplest and has no extra mechanism

  Doctest::
      
      ## check default
      >>> h = QHist()
      >>> h.prefix is None
      True

      ## check assignment
      >>> h.prefix = 'hello'
      >>> h.prefix
      'hello'

      ## check static assigment
      >>> h.prefix = 'hola'
      Traceback (most recent call last):
      ...
      AttributeError: Attribute "prefix" already set to 'hello'

      ## Check slots protection
      >>> h.xxx = 123
      Traceback (most recent call last):
      ...
      AttributeError: 'QHist' object has no attribute 'xxx'

      ## check copying
      >>> h2 = h()
      >>> h2.prefix
      'hello'
      >>> h2.prefix = 'world'
      Traceback (most recent call last):
      ...
      AttributeError: Attribute "prefix" already set to 'hello'

      ## check clearing
      >>> h2.clear()
      >>> h2.prefix is None
      True
      >>> h2.prefix = 'hello2'
      >>> h2.prefix
      'hello2'

  """

  __slots__ = ProtoQHist.__slots__ + (
    ## From lazy_property
    '_lazy_timestamp',
    '_lazy_wrapper',
    '_lazy_filename',
    ## New attribute
    '_stats',
    '_anchors',
    '_histos',
  )

  #---------------#
  # Inner methods #
  #---------------#

  def __init__(self, **kwargs):
    """
    Allow the init with kwargs.

    Doctest::

        ## Assert that two methods are equivalent.
        >>> h1 = QHist(name='somename')
        >>> h1.name
        'somename'
        >>> h2 = QHist()
        >>> h2.name = 'somename'
        >>> h1.name == h2.name
        True

    """
    ## Note: The order below is very important.
    ## 1. Super class first
    super(QHist, self).__init__()
    ## 2. Initialize local initial value
    self._stats   = Stats()
    self._anchors = Anchors()
    self._histos  = []
    ## 3. Supplied attributes
    # prefer these first
    fast_tracks = 'tpc', 'trees', 'params'
    for key in fast_tracks:
      if key in kwargs:
        setattr(self, key, kwargs[key])
        kwargs.pop(key)
    # the rest alphabetically
    for key, val in sorted(kwargs.iteritems()):
      setattr(self, key, val)

  def __call__(self, **kwargs):
    """
    Override the functionality of copy.copy, such that only the attribute at the
    level of static_struct is transfered, not at QHist level.

    Usage::

        ## Transfer & Independent
        >>> h1 = QHist(name='myname')
        >>> h2 = h1()
        >>> h2.title = 'newtitle'
        >>> h1.name
        'myname'
        >>> h2.name
        'myname'

    """
    ## Prepare queue, list of attrs that existed only in baseclass and used for prop.
    res   = self.__class__()
    queue = ProtoQHist.__slots__
    ## Transfer queue
    for key in queue:
      if hasattr(self, key):
        setattr(res, key, getattr(self, key))
    ## Initialize local initial value
    self.__class__.__init__(res, **kwargs)
    ## Finally, return
    return res

  ## For iterator protocol
  def __len__(self):
    """
    
    >>> len(QHist())
    0
    """
    return len(self._histos)

  def __getitem__( self, index ):
    """
    Get the member histograms, available only after draw.
    """
    return self._histos[index]

  #-----------------------------#
  # Read-only property -- AdHoc #
  #-----------------------------#

  @property
  def has_name(self):
    """
    Check if name is originally provided or not.

    >>> h = QHist()
    >>> h.has_name
    False
    >>> h.name = 'analysis'
    >>> h.has_name
    True
    """
    return ProtoQHist.name.fget(self) is not None

  @property
  def is_advance_stack(self):
    """
    True if TPC stack is advance mode.
    Note to self: This is actually much easier than `is_simple_stack`.
  
    Doctest::

        ## Default fails
        >>> QHist().is_advance_stack
        False

        ## Not-advance, fails
        >>> QHist(params='PT').is_advance_stack
        False
        >>> QHist(trees=tree).is_advance_stack
        False
        >>> QHist(trees=tree, params=['PX','PY']).is_advance_stack
        False

        ## Genuine advance TPC
        >>> QHist(tpc=[[tree, 'PT', '']]).is_advance_stack
        True
        >>> QHist(tpc=tpc).is_advance_stack
        True
    
    """
    return ProtoQHist.tpc.fget(self) is not None


  @property
  def is_simple_stack(self):
    """
    True if condition of simple stack is met, i.e.,
    only one or less of (trees, params, cuts) is a collection,
    the rest is a single entry.

    Doctest::

      ## Default fails
      >>> QHist().is_simple_stack
      False

      ## Incomplete, consider True to disable advance-TPC
      >>> QHist(trees=tree).is_simple_stack
      True
      >>> QHist(params='PT').is_simple_stack
      True
      >>> QHist(cuts='c').is_simple_stack
      True

      ## TPC is valid, success
      >>> QHist(trees=tree, params='PT').is_simple_stack
      True
      >>> QHist(trees=[tree,tree], params='PT').is_simple_stack
      True
      >>> QHist(trees=tree, params=['PT','PZ']).is_simple_stack
      True

      ## False if already an advance stack
      >>> QHist(tpc=[[tree, 'PT', '']]).is_simple_stack
      False

    """
    ## Require this to avoid circular self.tree, self.params
    if self.is_advance_stack:
      return False
    ## Because I already have the setter exclude the multiple-stacking,
    # I have to only check for the empty-inital-condition.
    nt,np,nc = len(self.trees), len(self.params), len(self.cuts)
    return not (nt==0 and np==0 and nc==0)


  @lazy_property
  def filename(self):
    """
    Return the current filename (without path, nor extension),
    deduce from the script that the instance is made.

    >>> getfixture('mainfile')
    >>> QHist().filename
    'mainfile'
    """
    return os.path.splitext(os.path.split(__main__.__file__)[-1])[0]


  @property
  def dim(self):
    """
    Doctest:: 

      ## Default is zero
      >>> QHist().dim
      0

      ## Simple TPC
      >>> QHist(params='PT').dim
      1
      >>> QHist(params='PT:PZ').dim
      2
      >>> QHist(params='TMath::Log10(PT)').dim
      1
      >>> QHist(params='TMath::Log10(PT):PZ').dim
      2
      >>> QHist(params='PX:PY:PZ').dim
      3
      >>> QHist(params=('PT:PZ','P:PZ')).dim
      2

      ## 'prof' flag does not change the dim
      >>> QHist(params='PX:PY:PZ', option='prof').dim
      3

      ## Advance TPC
      >>> QHist(tpc=[(tree, 'PT', '')]).dim
      1
      >>> QHist(tpc=[(tree, 'PX:PY', 'nPVs>1')]).dim
      2

    """
    tpc = self.tpc
    if len(tpc)==0: # incomplete spec, try params
      if not self.params:
        return 0
      return utils.dim(self.params[0])
    return utils.dim(tpc[0][1])

  @property
  def height_legend_console(self):
    """
    Return expected height of legend console.
    """
    return 15*(len(self.tpc)+1)

  @property
  def height_debug_console(self):
    """Return expected height of debug console"""
    return 15*(len(list(self.debug_messages)))

  @property
  def is_profile(self):
    """
    >>> QHist().is_profile
    False
    >>> QHist(option='prof').is_profile
    True
    >>> QHist(option='blah').is_profile
    False
    >>> QHist(option='sameprof').is_profile
    True

    """
    return 'prof' in self.option

  @property
  def debug_messages(self):
    """
    Generate pair of (header,message) to be put in debug console.

    >>> getfixture('mainfile'); getfixture('freeze_time')

    >>> h = QHist()
    >>> h.trees   = tree
    >>> h.params  = 'mu_PT: DPHI'
    >>> h.cuts    = 'M > 20e3'
    >>> h.xmin    = 1
    >>> h.xmax    = 100
    >>> h.ymin    = 0.
    >>> h.ymax    = 3.14
    >>> h.ybin    = 20
    >>> h.filters = {'mu_BPVIP<0.1', 'pi_BPVIP<0.1'}
    >>> h.comment = 'trying new optmz'

    >>> for line in h.debug_messages:
    ...   print('{:12} {:}'.format(*line))
    Filters      (pi_BPVIP<0.1) | (mu_BPVIP<0.1)
    Tree         h1_mu [#303]
    Param[0]     mu_PT: DPHI
    Cut[0]       M > 20e3
    Axis         X=[ 1.0, 100.0 ]/Auto=None, Y=[ 0.0, 3.14 ]/20
    Comment      trying new optmz
    Timestamp    20200101_000000000000
    Script       /mainfile

    """

    ## Filters
    # show raw because it's with AND/OR complexity.
    yield 'Filters', utils.join(self.filters)

    ## Trees
    used_names = set()
    for t in self.trees:
      if t:
        tname = t.GetTitle()
        if tname not in used_names:
          used_names.add(tname)
          entries = t.GetEntries()
          yield 'Tree', '{} [#{}]'.format(tname, entries)

    ## Params & cuts
    for i,p in enumerate(self.params):
      yield 'Param[%i]'%i, p
    for i,c in enumerate(self.cuts):
      yield 'Cut[%i]'%i, c

    ## Axis
    qfirst = utils.prefer_first
    qround = utils.pretty_round
    xmin   = qfirst( ProtoQHist.xmin.fget(self), 'Auto=%s'%qround(self.stats.xmin))
    xmax   = qfirst( ProtoQHist.xmax.fget(self), 'Auto=%s'%qround(self.stats.xmax))
    xbin   = qfirst( ProtoQHist.xbin.fget(self), 'Auto=%s'%self.stats.nbin )
    ymin   = qfirst( ProtoQHist.ymin.fget(self), 'Auto=%s'%qround(self.stats.ymin))
    ymax   = qfirst( ProtoQHist.ymax.fget(self), 'Auto=%s'%qround(self.stats.ymax))
    ybin   = qfirst( ProtoQHist.ybin.fget(self), 'Auto=%s'%self.stats.nbin )
    fmt    = 'X=[ {}, {} ]/{}, Y=[ {}, {} ]/{}'
    yield 'Axis', fmt.format( xmin, xmax, xbin, ymin, ymax, ybin )

    ## Misc
    if self.comment:
      yield 'Comment', self.comment
    yield 'Timestamp', self.timestamp
    yield 'Script', os.path.abspath(getattr(__main__, '__file__', '(interactive)'))

  #--------------------------------------------------#
  # Read-only property -- Stored                     #
  # These has to be explicitly declared in __slots__ #
  #--------------------------------------------------#

  @lazy_property
  def wrapper(self):
    """
    Once this has been called, it's considered initialized.
    """
    return Wrapper(self)

  @lazy_property
  def timestamp(self):
    """
    Lazy-method (to freeze value) of the timestamp string.
    Note: The timestamp is thus made the first time this method is called.

    >>> ## Timestamp should be unique
    >>> h1 = QHist()
    >>> h2 = QHist()
    >>> h1.timestamp == h2.timestamp
    False

    >>> ## ...even for the clones
    >>> h3 = h2()
    >>> h3.timestamp == h2.timestamp
    False

    """
    return datetime.now().strftime("%Y%m%d_%H%M%S%f")

  @property
  def guessname(self):
    """
    Specialize method to try to return a good naming, for saving file.
    Note that it only helps in the `name` part if missing.
    It won't concern prefix/suffix, which is why this method should be called
    inside `name` getter.

    >>> ## Ignore the prefix/suffix
    >>> QHist(trees=tree, params='M', prefix='pf', suffix='sf').guessname
    'M'

    >>> ## Ignore scale
    >>> QHist(trees=tree, params='M/1e3').guessname
    'M'
    """
    ## 1. If single param
    queue = list({ p for _,p,_ in self.tpc })
    if len(queue)==1 and queue[0]:
      res = queue[0]
    else:
      res = None
    ## Correction: scale
    # note: this part is similar to safename
    if res:
      res = utils.safename(res)
    ## Finally
    return res

  ## No public setter available
  @property
  def stats(self):
    """
    Return the stats object, contains array of statistics (min, max, count)
    for each entry queue in this QHist instance.

    >>> ## Initially is empty stat
    >>> QHist().stats
    <Stats> len=0 nbin=None X=[None, None]

    >>> ## Read-only
    >>> QHist().stats = {}
    Traceback (most recent call last):
    ...
    AttributeError: can't set attribute

    """
    return self._stats

  @property
  def anchors(self):
    """
    Return the anchor object, which hold 'pointers' to different TObject 
    involved in this QHist instance.
    
    >>> ## Initially empty
    >>> print(QHist().anchors)
    ------------------...
            KEY       |   VALUE  ( * differs from default )
    canvas            |   None
    debug             |   None
    debugpad          |   None
    legend            |   None
    legendpad         |   None
    mainpad           |   None
    stack             |   None
    ----------------------------------------------------...

    >>> ## Read-only
    >>> QHist().anchors = {}
    Traceback (most recent call last):
    ...
    AttributeError: can't set attribute

    """
    return self._anchors

  @property
  def xarr(self):
    """
    Return the python list representing array of bins in xaxis

    >>> ## uninitialized case
    >>> QHist().xarr is None
    True

    >>> ## Linear bins
    >>> QHist(xmin=0, xmax=10, xbin=4).xarr
    array('d', [0.0, 2.5, 5.0, 7.5, 10.0])

    >>> ## Logarithmic bins
    >>> QHist(xmin=1, xmax=256, xbin=2).xarr
    array('d', [1.0, 16.0, 256.0])

    """
    if any(getattr(self, key) is None for key in ('xmin', 'xmax', 'xbin')):
      return None
    return utils.make_bins( self.xmin, self.xmax, self.xbin, self.xlog )

  @property
  def yarr(self):
    """
    >>> QHist().yarr is None
    True
    >>> QHist(ymin=0, ymax=10, ybin=4).yarr
    array('d', [0.0, 2.5, 5.0, 7.5, 10.0])
    >>> QHist(ymin=1, ymax=256, ybin=2).yarr
    array('d', [1.0, 16.0, 256.0])

    """
    if any(getattr(self, key) is None for key in ('ymin', 'ymax', 'ybin')):
      return None
    return utils.make_bins( self.ymin, self.ymax, self.ybin, self.ylog )

  #-------------------#
  # Overridden getter #
  #-------------------#

  @getter_plus_doc(ProtoQHist.name)
  def name(self):
    """
    >>> ## final name = prefix + name + suffix
    >>> h = QHist(name='test', prefix='prelim')
    >>> h.name
    'prelim_test'
    >>> h.suffix = 'v0'
    >>> h.name
    'prelim_test_v0'

    >>> ## Default to timestamp, ignoring prefix
    >>> getfixture('freeze_time')
    >>> QHist(prefix='blah').name
    'temp_20200101_000000000000'

    """
    ## Check if there's name, guessing if needed.
    name = ProtoQHist.name.fget(self)
    if not name:
      if self.auto_name:
        name = self.guessname
      else:
        return 'temp_'+self.timestamp
    ## Construct the name = prefix + name0 + suffix
    name = utils.concat( self.prefix, name, self.suffix )
    ## Finally, clean name (can be very weird name disturbing the namespace).
    return utils.safename(name)


  @getter_plus_doc(ProtoQHist.title)
  def title(self):
    """
    >>> ## If title is missing, fallback to name
    >>> h = QHist(name='somename')
    >>> h.title
    'somename'

    >>> ## If given, it's now different from name
    >>> h.title = 'mytitle'
    >>> h.title != h.name
    True
    >>> h.prefix = 'prelim'
    >>> h.title
    'prelim_mytitle'

    >>> ## Title doesn't need safename
    >>> QHist(title='TMath::Abs(phi)').title
    'TMath::Abs(phi)'

    """
    ## Borrow from name immediately if null
    title0 = ProtoQHist.title.fget(self)
    if not title0:
      return self.name
    ## Construct the same way as name, but no need for safename.
    #  in order to show it entirely on canvas
    return utils.concat( self.prefix, title0, self.suffix )

  ## TPC: Equiplist on default value (None)
  # By equiping, I mean the value is already a list. The check for initial
  # value is then performed on the first element, e.g., self.trees[0] is None
  # - null of trees : None
  # - null of params: blank string
  # - null of cuts  : blank string
  # Therefore, their setter has to also guard against there null value.

  @getter_plus_doc(ProtoQHist.trees)
  @override_getter_default
  def trees(self):
    """
    >>> QHist().trees
    []
    >>> QHist(tpc=tpc).trees
    [<ROOT.TTree ...>, <ROOT.TTree ...>]

    """
    if self.is_advance_stack:
      return [t for t,_,_ in self.tpc]
    return []

  @getter_plus_doc(ProtoQHist.params)
  @override_getter_default
  def params(self):
    """
    >>> QHist().params
    []
    >>> QHist(tpc=tpc).params
    ['pi_BPVIP', 'mu_BPVIP']

    """
    if self.is_advance_stack:
      return [p for _,p,_ in self.tpc]
    return []

  @getter_plus_doc(ProtoQHist.cuts)
  @override_getter_default
  def cuts(self):
    """
    >>> QHist().cuts
    []
    >>> QHist(tpc=tpc).cuts
    ['pi_BPVIP > 0', 'mu_BPVIP > 0']

    """
    if self.is_advance_stack:
      return [c for _,_,c in self.tpc]
    return []

  @getter_plus_doc(ProtoQHist.filters)
  @override_getter_default
  def filters(self):
    # return ('',)
    return []

  @getter_plus_doc(ProtoQHist.tpc)
  @override_getter_default
  def tpc(self):
    """
    Return current TPC state with given inputs.

    >>> ## Simple TPC, no stacking
    >>> h = QHist(trees=tree, params='p')
    >>> h.tpc
    [(<ROOT.TTree ...>, 'p', '')]
    >>> h.cuts = 'PT>20'
    >>> h.tpc
    [(<ROOT.TTree ...>, 'p', 'PT>20')]

    >>> ## TPC with stacking
    >>> h = QHist(trees=tree, params=['P1', 'P2'], cuts='PT>20')
    >>> h.tpc
    [(<ROOT.TTree ...>, 'P1', 'PT>20'), (<ROOT.TTree ...>, 'P2', 'PT>20')]

    """
    cuts = self.cuts if self.cuts else [''] # it's optional in TPC formulation
    return [(t,p,c) for t in self.trees for p in self.params for c in cuts]


  @getter_plus_doc(ProtoQHist.normalize)
  def normalize(self):
    """
    Always return list of matched length with TPC.
  
    Doctest::

        ## default is tuple of length-0
        >>> QHist().normalize
        ()

        ## Length to TPC, correct stack level.
        >>> QHist(tpc=tpc, normalize=True).normalize
        (True, True)
        >>> QHist(tpc=tpc, normalize=None).normalize
        (None, None)
        >>> QHist(tpc=tpc, normalize=[154, 100]).normalize
        (154, 100)

        ## In some case, TPC is not ready, but norms are given. Show them regardless.
        # The validation will make sure that the length matches.
        >>> QHist(normalize=[154, 100]).normalize
        (154, 100)

    """
    n0   = ProtoQHist.normalize.fget(self)
    ntpc = len(self.tpc)
    if ntpc == 0: # no TPC, return normally
      return n0 if n0 is not None else tuple()
    elif n0 is None:
      return (True,)*ntpc
    elif len(n0) == ntpc:
      return n0
    return n0*ntpc

  @getter_plus_doc(ProtoQHist.comment)
  @override_getter_default
  def comment(self):
    """
    No extra logic.

    >>> QHist().comment
    ''
    
    """
    return ''

  @getter_plus_doc(ProtoQHist.legends)
  @override_getter_default
  def legends(self):
    """
    Handles the educated-guess of legends to be used.

    >>> ## From multiple trees/params/cuts
    >>> QHist(trees=(tree,tree), params='P').legends
    ('h1_mu', 'h1_mu')
    >>> QHist(trees=tree, params=('P1','P2')).legends
    ('P1', 'P2')
    >>> QHist(trees=tree, params='P', cuts=('C1','C2')).legends
    ('C1', 'C2')

    >>> ## From advance TPC
    >>> for leg in QHist(tpc=tpc).legends:
    ...   print leg
    [0] tree='h1_mu', param='pi_BPVIP', cut='pi_BPVIP > 0'
    [1] tree='h1_mu', param='mu_BPVIP', cut='mu_BPVIP > 0'

    """
    ## Do generically for advance stacking
    if self.is_advance_stack:
      res = ["[%i] tree=%r, param=%r, cut=%r"%(i,t.GetName(),p,c) for i,(t,p,c) in enumerate(self.tpc)]
    else:
      res = None
      ## Simple stacking guesswork.
      lt = len(self.trees)
      lp = len(self.params)
      lc = len(self.cuts)
      # by trees (REMARK: T >= 1)
      if lt>=1 and lp<=1 and lc<=1:
        ## Remove Ganga's prefix. It'll be in debug console later.
        # res = tuple(t.GetTitle().split('::')[-1].split('/')[-1] for t in self.trees)
        # disable backslash in case of genuine usage (GeV/c)
        res = tuple(t.GetTitle().split('::')[-1] for t in self.trees)
      if lt<=1 and lp>1 and lc<=1:  # by params
        res = self.params
      if lt<=1 and lp<=1 and lc>1:  # by cuts
        res = self.cuts
    return res


  @getter_plus_doc(ProtoQHist.option)
  @override_getter_default
  def option(self):
    """
    >>> ## default to empty string like ROOT:TTree
    >>> QHist().option
    ''
    """
    return ''

  #-----------------------------

  @ProtoQHist.xmin.getter
  @override_getter_default
  def xmin(self):
    return self.stats.xmin

  @ProtoQHist.xmax.getter
  @override_getter_default
  def xmax(self):
    return self.stats.xmax

  @ProtoQHist.xbin.getter
  @override_getter_default
  def xbin(self):
    return self.stats.nbin

  @getter_plus_doc(ProtoQHist.xlog)
  @override_getter_default
  def xlog(self):
    """
    1. Use explicit value.
    2. Use from explicit bound.
    3. Use from scanned bound.

    >>> QHist().xlog is None
    True
    >>> QHist(xlog=True).xlog
    True

    """
    val1 = utils.auto_log( self.xmin, self.xmax )
    val2 = self.stats.xlog
    return utils.prefer_first( val1, val2 )

  @getter_plus_doc(ProtoQHist.xlabel)
  @override_getter_default
  def xlabel(self):
    """
    >>> QHist().xlabel
    ''
    >>> QHist(params='P').xlabel  # guess
    'P'
    >>> QHist(params='PX:PY').xlabel  # guess
    'PX'
    >>> QHist(tpc=[(tree, 'P', '')]).xlabel  # guess
    'P'
    >>> QHist(tpc=[(tree, 'P', 'c1'), (tree, 'P', 'c2')]).xlabel # guess
    'P'
    >>> QHist(tpc=tpc).xlabel  # complex, don't guess
    ''

    """
    ## Guess from params if it's simple enough.
    l = list(set(self.params))
    if l and len(l)==1:
      ## make sure to return the first dim.
      return utils.split_dim(l[0])[0]
    ## Prefer blank string than None for easy SetTitle later
    return ''

  @ProtoQHist.ymin.getter
  @override_getter_default
  def ymin(self):
    return self.stats.ymin

  @ProtoQHist.ymax.getter
  @override_getter_default
  def ymax(self):
    return self.stats.ymax

  @ProtoQHist.ybin.getter
  @override_getter_default
  def ybin(self):
    return self.stats.nbin

  @ProtoQHist.ylog.getter
  @override_getter_default
  def ylog(self):
    val1 = utils.auto_log( self.ymin, self.ymax )
    val2 = self.stats.ylog
    return utils.prefer_first( val1, val2 )

  @getter_plus_doc(ProtoQHist.ylabel)
  @override_getter_default
  def ylabel(self):
    """
    Attempt to guess from the params if it's not ambigious

    >>> QHist().ylabel
    ''
    >>> QHist(params='P').ylabel  # not enough dim
    ''
    >>> QHist(params='PX:PY').ylabel  # guess
    'PY'
    >>> QHist(tpc=[(tree, 'P', '')]).ylabel  # not enough dim
    ''
    >>> QHist(tpc=[(tree, 'PX:PY', '')]).ylabel  # guess
    'PY'
    >>> QHist(tpc=tpc).ylabel  # complex, don't guess
    ''

    """
    ## Fast check from global dim
    if self.dim < 2:
      return ''
    ## Guess from params if it's simple enough.
    l = list(set(self.params))
    if l and len(l)==1:
      p = l[0]
      if p and utils.dim(p)>=2:
        ## make sure to return the first dim.
        return utils.split_dim(p)[1]
    ## Prefer blank string than None for easy SetTitle later
    return ''

  @ProtoQHist.zbin.getter
  @override_getter_default
  def zbin(self):
    return self.stats.nbin

  @ProtoQHist.zlog.getter
  @override_getter_default
  def zlog(self):
    return self.stats.zlog

  @getter_plus_doc(ProtoQHist.zlabel)
  @override_getter_default
  def zlabel(self):
    """
    Attempt to guess from the params if it's not ambigious

    >>> QHist().zlabel
    ''
    >>> QHist(params='P').zlabel  # not enough dim
    ''
    >>> QHist(params='PX:PY:PZ').zlabel  # guess
    'PZ'
    >>> QHist(tpc=[(tree, 'P', '')]).zlabel  # not enough dim
    ''
    >>> QHist(tpc=[(tree, 'PX:PY:PZ', '')], option='prof').zlabel  # guess
    'PZ'
    >>> QHist(tpc=tpc).zlabel  # complex, don't guess
    ''

    """
    ## Fast check from global dim
    if self.dim < 3:
      return ''
    ## Guess from params if it's simple enough.
    l = list(set(self.params))
    if l and len(l)==1:
      p = l[0]
      if p and utils.dim(p)>=3:
        ## make sure to return the first dim.
        return utils.split_dim(p)[2]
    ## Prefer blank string than None for easy SetTitle later
    return ''

  #------------------------------------#
  # Overridden setter ~ Pre-validation #
  #------------------------------------#

  @setter_from_return_plus_doc(trees)
  @equiplist_nullcheck_typecheck(ROOT.TTree)
  def trees( self, val ):
    """
    Doctest::

        ## Default is empty list
        >>> QHist().trees
        []

        ## Equip to list
        >>> QHist(trees=tree).trees
        (<ROOT.TTree object ("h1_mu") at ...>,)

        ## Raise error if other stacked
        >>> h = QHist(params=['PX', 'PY'])
        >>> h.trees = tree,tree
        Traceback (most recent call last):
        ...
        AttributeError: Cannot expand `trees`, already expanded elsewhere.

        ## Raise error is already have advance-TPC
        >>> h = QHist(tpc=tpc)
        >>> h.trees = tree
        Traceback (most recent call last):
        ...
        AttributeError: ...

    """
    ## Abort if advance mode already there
    if self.is_advance_stack:
      raise AttributeError('Advance mode is already used. Cannot use simple TPC.')
    ## Raise error if other component has been stacked.
    if len(val) > 1 and (len(self.params) > 1 or len(self.cuts) > 1):
      raise AttributeError('Cannot expand `trees`, already expanded elsewhere.')
    ## Finally
    return val

  @setter_from_return_plus_doc(params)
  @equiplist_nullcheck_typecheck( basestring )
  def params( self, val ):
    """
    Doctest::

        ## Default is empty list
        >>> QHist().params
        []

        ## Equip to list
        >>> QHist(params='PT').params
        ('PT',)

        ## Raise error if other stacked
        >>> h = QHist(cuts=['Q>0', 'Q<0'])
        >>> h.params = 'PT1', 'PT2'
        Traceback (most recent call last):
        ...
        AttributeError: Cannot expand `params`, already expanded elsewhere.

        ## Inconsistent dimensions
        >>> h = QHist(params=('PT','PX:PY')) # inconsistent
        Traceback (most recent call last):
        ...
        AttributeError: ...

        ## Too-large dimensions
        >>> h = QHist(params='PX:PY:PZ')  # 3 is okay
        >>> h = QHist(params='PX:PY:PZ:PE')
        Traceback (most recent call last):
        ...
        AttributeError: ...

        ## Raise error is already have advance-TPC
        >>> h = QHist(tpc=tpc)
        >>> h.params = 'P'
        Traceback (most recent call last):
        ...
        AttributeError: ...

    """
    ## Abort if advance mode already there
    if self.is_advance_stack:
      raise AttributeError('Advance mode is already used. Cannot use simple TPC.')
    ## Raise error if other component has been stacked.
    if len(val) > 1 and (len(self.trees) > 1 or len(self.cuts) > 1):
      raise AttributeError('Cannot expand `params`, already expanded elsewhere.')
    ## Dimensionality check
    dim0 = None
    for x in val:
      dim = utils.dim(x)
      if dim > 3:
        raise AttributeError('QHist cannot do dim>3 histogram.')
      if dim0 is None:
        dim0 = dim
      elif dim0 != dim:
        raise AttributeError('Inconsistent dimension.')
    ## Finally
    return val

  @setter_from_return_plus_doc(cuts)
  @equiplist_typecheck( basestring )
  def cuts( self, val ):
    """

    >>> ## Default is empty list
    >>> QHist().cuts
    []

    >>> ## Equip to list
    >>> QHist(cuts='ISMUON').cuts
    ('ISMUON',)

    >>> ## Allow explicit null string
    >>> QHist(cuts='').cuts
    ('',)

    >>> ## Raise error if other stacked
    >>> h = QHist(params=['PT1','PT2'])
    >>> h.cuts = 'Q>0', 'Q<0'
    Traceback (most recent call last):
    ...
    AttributeError: Cannot expand `cuts`, already expanded elsewhere.

    >>> ## Raise error is already have advance-TPC
    >>> h = QHist(tpc=tpc)
    >>> h.cuts = 'c'
    Traceback (most recent call last):
    ...
    AttributeError: ...

    """
    ## Abort if advance mode already there
    if self.is_advance_stack:
      raise AttributeError('Advance mode is already used. Cannot use simple TPC.')
    ## Raise error if other component has been stacked.
    if len(val) > 1 and (len(self.trees) > 1 or len(self.params) > 1):
      raise AttributeError('Cannot expand `cuts`, already expanded elsewhere.')
    ## Finally
    return val

  @setter_from_return_plus_doc(filters)
  @equiplist_nullcheck_typecheck( basestring, list, tuple )
  def filters( self, val ):
    """
    Doctest::

        >>> QHist().filters
        []
        >>> QHist(filters='cut').filters
        ('cut',)
        >>> QHist(filters=['cut1','cut2']).filters
        ('cut1', 'cut2')
        >>> QHist(filters={'cut1','cut2'}).filters
        set(['cut1', 'cut2'])
        >>> QHist(filters={('cut1A','cut1B'),('cut2A','cut2B')}).filters
        set([('cut1A', 'cut1B'), ('cut2A', 'cut2B')])

        ## Error
        >>> QHist(filters=None)
        Traceback (most recent call last):
        ...
        TypeError: ...

    """
    return val # no further validation, already in decorator.


  @setter_from_return_plus_doc(tpc)
  @equiplist_nullcheck_typecheck( list, tuple )
  def tpc( self, val ):
    """

    The triplet must be well-defined
    --------------------------------

    >>> QHist(tpc=[('param',)])
    Traceback (most recent call last):
    ...
    AttributeError: TPC: Need a triplet.

    >>> QHist(tpc=[('param', 'cuts')])
    Traceback (most recent call last):
    ...
    AttributeError: TPC: Need a triplet.

    >>> QHist(tpc=(tree, 'P', 'C')) # need triplet in a list, not naked.
    Traceback (most recent call last):
    ...
    TypeError: ...


    Correct triplet types
    ---------------------

    >>> QHist(tpc=[('BAD', 'p', 'c')])
    Traceback (most recent call last):
    ...
    AttributeError: ...
    >>> QHist(tpc=[(tree, 5555, 'c' )])
    Traceback (most recent call last):
    ...
    AttributeError: ...
    >>> QHist(tpc=[(tree, 'c', None )])
    Traceback (most recent call last):
    ...
    AttributeError: ...


    Disable advance-TPC setter if simple one is already used.
    ---------------------------------------------------------

    >>> h = QHist(trees=tree)
    >>> h.tpc = tpc
    Traceback (most recent call last):
    ...
    AttributeError: Simple mode is already used. Cannot use advance TPC.

    >>> h = QHist(params='P')
    >>> h.tpc = tpc
    Traceback (most recent call last):
    ...
    AttributeError: Simple mode is already used. Cannot use advance TPC.

    >>> h = QHist(cuts='c')
    >>> h.tpc = tpc
    Traceback (most recent call last):
    ...
    AttributeError: Simple mode is already used. Cannot use advance TPC.


    Need consistent dim
    -------------------

    >>> QHist(tpc=[(tree, 'PT', ''), (tree, 'PX:PY', '')])
    Traceback (most recent call last):
    ...
    AttributeError: TPC: Inconsistent dimension.

    >>> QHist(tpc=[(tree, 'D1:D2:D3:D4', '')])
    Traceback (most recent call last):
    ...
    AttributeError: QHist cannot do dim>3 histogram.

    """
    ## Abort if simple mode already there
    if self.is_simple_stack:
      raise AttributeError('Simple mode is already used. Cannot use advance TPC.')
    dim0 = None
    for triplet in val:
      ## Check for being len 3
      if len(triplet) != 3:
        raise AttributeError('TPC: Need a triplet.')
      ## Check for correct type:
      if not isinstance( triplet[0], ROOT.TTree ):
        raise AttributeError('TPC: Need triplet[0] to be ROOT.TTree')
      if not isinstance( triplet[1], basestring ):
        raise AttributeError('TPC: Need triplet[1] to be basestring')
      if not isinstance( triplet[2], basestring ):
        raise AttributeError('TPC: Need triplet[2] to be basestring')
      ## Check dimension consistency
      dim = utils.dim(triplet[1])
      if dim > 3:
        raise AttributeError('QHist cannot do dim>3 histogram.')
      if dim0 is None:
        dim0 = dim
      elif dim0 != dim:
        raise AttributeError('TPC: Inconsistent dimension.')
    ## Finally
    return val


  #--------------#
  # AXIS setters #
  #--------------#

  @setter_from_return_plus_doc(xmin)
  @setter_isinstance(float, int)
  def xmin( self, val ):
    """
    >>> QHist().xmin is None
    True
    >>> QHist(xmin=10).xmin
    10.0

    >>> QHist(xmax=10).xmin = 20
    Traceback (most recent call last):
    ...
    ValueError: ...

    """
    val = float(val)
    ## Check min < max
    if self.xmax is not None and val >= self.xmax:
      raise ValueError('Cannot have xmin > xmax')
    return val

  @setter_from_return_plus_doc(xmax)
  @setter_isinstance(float, int)
  def xmax( self, val ):
    """
    >>> QHist().xmax is None
    True
    >>> QHist(xmax=10).xmax
    10.0

    >>> QHist(xmin=10).xmax = 5
    Traceback (most recent call last):
    ...
    ValueError: ...

    """
    val = float(val)
    ## Check min < max
    if self.xmin is not None and self.xmin >= val:
      raise ValueError('Cannot have xmin > xmax')
    return val

  @setter_from_return_plus_doc(xbin)
  @setter_isinstance(int)
  def xbin( self, val ):
    """
    >>> QHist(xbin=20).xbin
    20

    >>> ## no zero
    >>> QHist(xbin=0)
    Traceback (most recent call last):
    ...
    ValueError: ...

    >>> ## no negative
    >>> QHist(xbin=-10)
    Traceback (most recent call last):
    ...
    ValueError: ...

    >>> ## no float
    >>> QHist(xbin=10.)
    Traceback (most recent call last):
    ...
    TypeError: ...

    """
    if val <= 0:
      raise ValueError('Cannot have non-positive number of bins')

  @setter_from_return_plus_doc(xlog)
  @setter_isinstance(bool)
  def xlog( self, val ):
    """
    >>> QHist(xlog=True).xlog
    True
    >>> QHist(xlog=False).xlog
    False
    >>> QHist(xlog=None)
    Traceback (most recent call last):
    ...
    TypeError: ...

    """
    pass

  @setter_from_return_plus_doc(xlabel)
  @setter_isinstance(basestring)
  def xlabel( self, val ):
    """
    >>> ## Simple
    >>> QHist(xlabel='mass').xlabel
    'mass'

    """
    pass

  @setter_from_return_plus_doc(ymin)
  @setter_isinstance(float, int)
  def ymin( self, val ):
    """
    >>> QHist().ymin is None
    True
    >>> QHist(ymin=10).ymin
    10.0

    >>> QHist(ymax=10).ymin = 20
    Traceback (most recent call last):
    ...
    ValueError: ...

    """
    val = float(val)
    ## Check min < max
    if self.ymax is not None and val >= self.ymax:
      raise ValueError('Cannot have ymin > ymax')
    return val

  @setter_from_return_plus_doc(ymax)
  @setter_isinstance(float, int)
  def ymax( self, val ):
    """
    >>> QHist().ymax is None
    True
    >>> QHist(ymax=10).ymax
    10.0

    >>> QHist(ymin=10).ymax = 5
    Traceback (most recent call last):
    ...
    ValueError: ...

    """
    val = float(val)
    ## Check min < max
    if self.ymin is not None and self.ymin >= val:
      raise ValueError('Cannot have ymin > ymax')
    return val

  @setter_from_return_plus_doc(ybin)
  @setter_isinstance(int)
  def ybin( self, val ):
    """
    >>> QHist(ybin=-10)
    Traceback (most recent call last):
    ...
    ValueError: ...

    """
    if val <= 0:
      raise ValueError('Cannot have non-positive number of bins')

  @setter_from_return_plus_doc(ylog)
  @setter_isinstance(bool)
  def ylog( self, val ):
    pass

  @setter_from_return_plus_doc(ylabel)
  @setter_isinstance(basestring)
  def ylabel( self, val ):
    """
    >>> QHist(ylabel='count').ylabel
    'count'

    """
    pass

  @setter_from_return_plus_doc(zbin)
  @setter_isinstance(int)
  def zbin( self, val ):
    """
    >>> QHist(zbin=-10)
    Traceback (most recent call last):
    ...
    ValueError: ...

    """
    if val <= 0:
      raise ValueError('Cannot have non-positive number of bins')

  @setter_from_return_plus_doc(zlog)
  @setter_isinstance(bool)
  def zlog( self, val ):
    pass

  @setter_from_return_plus_doc(zlabel)
  @setter_isinstance(basestring)
  def zlabel( self, val ):
    """
    >>> QHist(zlabel='count').zlabel
    'count'

    """
    pass

  #-------------------------

  @setter_from_return_plus_doc(normalize)
  @equiplist_typecheck(bool, int, float, long, type(None), types.FunctionType)
  def normalize( self, val ):
    """
    Doctest::

        ## Equip to tuple of length-1 internally, ready for mult.
        # even though TPC is not available
        >>> QHist(normalize=True)._staticprop_normalize
        (True,)
        >>> QHist(normalize=False)._staticprop_normalize
        (False,)
        >>> QHist(normalize=None)._staticprop_normalize
        (None,)
        >>> QHist(normalize=100)._staticprop_normalize
        (100,)

        ## Error on empty inputs
        >>> QHist(normalize=[])
        Traceback (most recent call last):
        ...
        AttributeError: Require non-empty list ...

    """
    return val # this is now the equipped list


  @setter_from_return_plus_doc(comment)
  def comment(self, val):
    """
    Doctest::

        ## Stringify everything threw into it.
        >>> QHist(comment='Hello world').comment
        u'Hello world'

    """
    return unicode(val)


  @setter_from_return_plus_doc(legends)
  @equiplist_nullcheck_typecheck(basestring)
  def legends( self, val ):
    """

    >>> ## In general, do not allow setting in legends if there's no TPC.
    >>> QHist(legends=['a', 'b'])
    Traceback (most recent call last):
    ...
    ValueError: ...

    >>> ## Disable legends if stacking==1 (too verbose)
    >>> QHist(trees=tree, params='P', legends='text')
    Traceback (most recent call last):
    ...
    AttributeError: Legends is disable without stacking.

    >>> ## Mismatch dim
    >>> QHist(tpc=tpc, legends=['1', '2', '3']) # dim=2
    Traceback (most recent call last):
    ...
    ValueError: Need legends of same length as TPC.

    """
    self._validate()  # Use validation to confirm existence of TPC
    ltpc = len(self.tpc)
    if ltpc==1:
      raise AttributeError('Legends is disable without stacking.')
    if ltpc != len(val):
      raise ValueError('Need legends of same length as TPC.')
    return val

  #----------------#
  # HIDDEN METHODS #
  #----------------#

  def _fullcuts(self, p, c=''):
    """
    Return the ROOT-ready string represent all cuts to be used in TTree::Draw.
    The arguments (p,c) is usually a subset of (params, cuts) found in the
    instance of qhist, sliced to single-stack and single-dim.

    The fullcuts is composed of these components:
      1. Explicit cut: c
      2. Filters
      3. Implicit/Axis cut

    Leverage functionality of utils.join

    Note:
    - Note that p can be 1D/2D/3D

    - ???? If is_prof is True, the cut on y-axis should NOT be added to this
      since it directly affect the result.

    ## Basic
    >>> QHist()._fullcuts('p', '')
    ''
    >>> QHist()._fullcuts('p', 'c<0')
    'c<0'

    ## With filters
    >>> QHist(filters='c<0')._fullcuts('p', '')
    'c<0'
    >>> QHist(filters=['a>1','b>2'])._fullcuts('p', 'c==3')
    '(c==3) & ((a>1) & (b>2))'
    >>> QHist(filters={'a>1','b>2'})._fullcuts('p', 'c==3')
    '(c==3) & ((b>2) | (a>1))'

    ## With axis
    >>> QHist(xmin=123, xmax=234)._fullcuts('p', 'c==0')
    '(c==0) & ((p >= 123.0) & (p <= 234.0))'
    >>> QHist(xmin=80, xmax=100, ymin=0, ymax=3.14)._fullcuts('PY:PX', 'Z02MuMu')
    '(Z02MuMu) & ((PX >= 80.0) & (PX <= 100.0)) & ((PY >= 0.0) & (PY <= 3.14))'

    ## Higher dim
    >>> QHist(xmin=1, xmax=2, ymin=3, ymax=4, zmin=5, zmax=6)._fullcuts('X:Y:Z')
    '((X >= 1.0) & (X <= 2.0)) & ((Y >= 3.0) & (Y <= 4.0)) & ((Z >= 5) & (Z <= 6))'
    
    """
    fullcuts = []

    ## 1. Explicit cuts
    fullcuts.append(c)

    ## 2. filters
    fullcuts.append(self.filters)

    ## 3. Axis cut
    dim = utils.dim(p)  # For less-verbose testing
    if dim==1:
      fullcuts.append(utils.cut_minmax( p, self.xmin, self.xmax ))
    elif dim==2:
      py,px = utils.split_dim(p) # IMPORTANT: Retain the convention from ROOT, x-axis last
      fullcuts.append(utils.cut_minmax( px, self.xmin, self.xmax ))
      fullcuts.append(utils.cut_minmax( py, self.ymin, self.ymax ))
    elif dim==3:
      px,py,pz = utils.split_dim(p)
      fullcuts.append(utils.cut_minmax( px, self.xmin, self.xmax ))
      fullcuts.append(utils.cut_minmax( py, self.ymin, self.ymax ))
      fullcuts.append(utils.cut_minmax( pz, self.zmin, self.zmax ))
    else:
      raise ValueError('Dimension > 3 not supported.')

    ## Finally, use smart join for return
    logger.debug(fullcuts)
    return utils.join(fullcuts)

  @property
  def _tpc_fullcuts(self):
    """
    Based on self.tpc, but now include the effect of _fullcuts.
    This is for the actual lifecycle methods.
    """
    for t,p,c in self.tpc:
      yield t, p, self._fullcuts(p,c)

#===============================================================================

  @report_debug
  def _validate(self):
    """
    Performs all validation before processing further,
    no change in its internal state.

    ## Default is not valid
    >>> QHist()._validate()
    Traceback (most recent call last):
    ...
    ValueError: ...

    ## Incomplete-simple-TPC is not valid
    >>> QHist(trees=tree)._validate()
    Traceback (most recent call last):
    ...
    ValueError: ...

    >>> QHist(params='P')._validate()
    Traceback (most recent call last):
    ...
    ValueError: ...

    ## Complete simple-TPC is valid
    >>> QHist(trees=tree, params='P')._validate()
    True

    ## Complete advance-TPC is valid
    >>> QHist(tpc=tpc)._validate()
    True

    ## Error on mismatch normalize dim
    >>> QHist(tpc=tpc, normalize=[10, 20, 15])._validate()
    Traceback (most recent call last):
    ...
    AttributeError: ...

    ## 1D + profile is impossible
    >>> QHist(tpc=tpc, option='prof')._validate()
    Traceback (most recent call last):
    ...
    ValueError: Profile plot can only be used in 2D/3D plot.

    ## 2D + profile is okay!
    >>> QHist(tpc=[(tree, 'p1:p2', 'c')], option='prof')._validate()
    True

    """
    ## Need TPC ready. Rely on earlier setters logic
    if not self.trees or not self.params:
      raise ValueError('Missing tree/param')

    ## Profile plot can only be used in 2D/3D plot
    if self.is_profile and self.dim not in (2,3):
      raise ValueError('Profile plot can only be used in 2D/3D plot.')

    ## Normalize dim
    if len(self.normalize) != len(self.tpc):
      raise AttributeError('Unmatch normalize dimension.')

    ## For traditional status code
    return True

#===============================================================================
