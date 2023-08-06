#!/usr/bin/env python

import itertools
import types
import ROOT
from array import array
from math import log10
from . import logger

#--------#
# SCHEME #
#--------#

def COLORS(i):
  """
  Repeating palette of colors, modulo around.
  Change to obey the active palette, allowing local change of color.

  >>> COLORS(0)
  1
  >>> COLORS(3)  # qhist's
  28

  """
  n = ROOT.TColor.GetNumberOfColors()
  return ROOT.TColor.GetColorPalette(i%n)
  # return (1, 2, 4, 28, 6, ROOT.kGreen+3, ROOT.kAzure+7 )[i%7]
  # return ( 1,2,8,4,6,7,9 )[i%7]
  # return ROOT.gStyle.GetColorPalette( i*100 )
  # return (0,5,7,3,6,2,4,1)[i%8] ## From LHCb.style

def MARKERS(i):
  """
  Repeating choices of marker.

  >>> MARKERS(0) == ROOT.kMultiply
  True
  >>> MARKERS(2) == ROOT.kPlus
  True

  """
  return [ROOT.kMultiply, ROOT.kCircle, ROOT.kPlus, ROOT.kOpenDiamond, ROOT.kOpenTriangleUp][i%5]

def LINES(i):
  """
  Choice of line style.

  >>> LINES(0)
  1

  """
  return i+1

def FILLS(i):
  """
  Repeating choice of fill style, modulo 7.
  
  >>> FILLS(0)
  3001

  """
  return (3001, 3254, 3245, 3305, 3395, 3012, 3016)[i%7]
  # return (3003,3004,3005,3006,3007,3012,3016)[i%7]

#-------------#
# COMPUTATION #
#-------------#

def auto_bin_size(nevt):
  """
  Given the list of event size (counts), return appropriate num of bins,
  which is calculated from sqrt of smallest event size, rounded in 5.
  min of 20, max of 100.

  >>> auto_bin_size(100)
  20
  >>> auto_bin_size(5000)
  70
  >>> auto_bin_size(1E6)
  100
  >>> auto_bin_size(0)  # Even null plot, return minimum number of bins
  20

  """
  minv = 20
  maxv = 100
  val  = int(round(1./5*(nevt**0.5))*5)
  return minv if val < minv else maxv if val > maxv else val

#-------------------------------------------------------------------------------

def auto_log(vmin, vmax):
  """
  Deduce whether the log scale should be used or not, judging from given range.

  >>> auto_log(0, 10)  # has zero, don't.
  False
  >>> auto_log(0.0, 1.0)  # has zero, don't.
  False
  >>> auto_log(-1.0, 1.0)  # has negative, don't.
  False
  >>> auto_log(1E-4, 1E1)  # positive & wide, do it.
  True
  >>> auto_log(10, 50)  # arbitary, don't
  False

  >>> ## If both are not initialize (e.g., null-stats), return None 
  >>> ## in order to have same default as QHist.xlog
  >>> auto_log( 10, None ) is None
  True
  >>> auto_log( None, 100 ) is None
  True
  >>> auto_log( None, None ) is None
  True

  """
  ## Uninitialize case
  if vmin is None or vmax is None:
    return None
  ## If bound within [0,1], don't
  if vmin==0. and vmax==1.:
    return False 
  ## Crossing zero. No log
  if vmin <= 0:
    return False 
  ## Large magnitude
  if vmax / vmin >= 1E2:
    return True 
  ## Don't do log, by default
  return False

#-------------------------------------------------------------------------------

def auto_morelog(axis):
  """
  Wrapper around TAxis.SetMoreLogLabels 
  Configure automatically whether this axis should have detail label or not.
  Perferable do so in small scale.

  >>> axis = ROOT.TAxis(20, 1, 1000)
  >>> axis.moreLogLabels
  False
  >>> auto_morelog(axis)
  >>> axis.moreLogLabels
  True

  """
  valmin = axis.xmin
  valmax = axis.xmax
  if valmin and valmax/valmin < 1E4: # Non zero, and not-too-wide scale
    axis.moreLogLabels = True

#-------------------------------------------------------------------------------

def make_bins(valmin, valmax, nbins, is_log=False, margin=0.0):
  """
  Important method to provide the binnings for given spec.
  The cue is to have pretty-log axis.
  http://root.cern.ch/root/roottalk/roottalk06/1213.html

  Usage::

      ## Simple
      >>> make_bins(0, 100, 20)
      array('d', [0.0, 5.0, 10.0, ...

      ## Restrict the extreme one
      >>> make_bins(-1e12, 1, nbins=1)
      array('d', [-1000000.0, 1.0])
      >>> make_bins(1, 1e12, nbins=1)
      array('d', [1.0, 1000000.0])

      ## Grace allowance
      >>> make_bins(10, 10, nbins=1)
      array('d', [9.9, 10.1])
      >>> make_bins(0, 0, nbins=1)
      array('d', [-0.1, 0.1])

      ## Ignore log on negative
      >>> make_bins(-1, 10, nbins=1, is_log=True)
      array('d', [-1.0, 10.0])

      ## absurd
      >>> make_bins(-1e12, -1e12, 100)
      Traceback (most recent call last):
      ...
      ValueError: Data range seems absurd. The script will halt.

  """
  ### Validate and abort if it seems very suspicious
  if valmin < -1E6 and valmax < -1E6:
    logger.warning(locals())
    raise ValueError('Data range seems absurd. The script will halt.')

  ### Some fine adjustment of data
  ## If it's too extreme, restrict the domain
  if valmin < -1E6:
    logger.debug('valmin too small. Restrict back to -1E6.')
    valmin = -1E6
  if valmax > 1E6:
    logger.debug('valmax too large. Restrict back to 1E6.')
    valmax = 1E6

  ## If the min==max, do the grace allowance (+-1% each side)
  if valmin == valmax:
    if valmin==0:  # Worst case: Complete-0s
      dval = 0.1
    else:
      dval = abs(valmin*0.01)
    valmin -= dval
    valmax += dval
    logger.debug('Grace adjust when min==max: dx={}'.format(dval))

  ## If x is logarithm, disable if math domain conflict
  if is_log and valmin <= 0:
    logger.warning('Found non-positive valmin in log-axis. Recommending disable log-axis, or put `xmin=1E-6` or `cuts>0`)')
    is_log = False

  logger.debug('## QHistUtils.make_bins summary (post-adjustment)')
  logger.debug("valmin : " + str(valmin))
  logger.debug("valmax : " + str(valmax))
  logger.debug("nbins  : " + str(nbins))
  logger.debug("is_log : " + str(is_log))

  ## Finally, make a array out of it.
  valmin *= ( 1.-margin if valmin>0 else 1.+margin )
  valmax *= ( 1.+margin if valmax>0 else 1.-margin )
  if is_log:
    width = 1.0*(log10(valmax)-log10(valmin))/(nbins)
    arr   = [ 10**(log10(valmin) + i*width) for i in range(nbins+1) ]
  else:
    width = 1.0*(valmax-valmin)/(nbins)
    arr   = [ valmin + i*width for i in range(nbins+1) ]
  return array('d', arr)

#-------------------------------------------------------------------------------

def get_stats_single(t, p, c):
  """
  Return the axis-min/max of the given TPC tuple.

  Note: TTree::GetMinimum is NOT what we want because cannot use cut c
  Note: Y-min/max is more complicate because of ybin, normalization
  Note: For SetEstimate hack, see TTree::Draw documantation
  Note: To ensure, use the vanilla TTree (not rootpy Tree), force mother call.

  """
  logger.debug('Stats: t: '+t.title)
  logger.debug('Stats: p: %r'%p)
  logger.debug('Stats: c: %r'%c)
  t.estimate = t.entries+1 # bug with (-1)
  # n = ROOT.TTree.Draw(t, p, c, "goff")
  # n = t.Draw(p, c, "goff")
  cw = c.replace('&&','*').replace('&','*')
  n  = t.Draw(p, cw, "goff") # make sure it counts the weight
  if n <=0 :
    logger.warning("Null-histogram. Please know what you're doing...")
    logger.warning('Tree : %s %r'%(t.title, t))
    logger.warning('Param: %s'%p)
    logger.warning('Cut  : %s'%c)
    return 0, None, None
    # raise ValueError('Null plots!! Please recheck the TPC settings.')
  g1,g2 = itertools.tee(t.GetV1()[i] for i in xrange(n)) # Use generator for speed
  return n, min(g1), max(g2)
  # axis = ROOT.gROOT.FindObject('htemp').GetXaxis()
  # return n, axis.GetXmin(), axis.GetXmax()

#-------------------------------------------------------------------------------

def prefer_first(*vals):
  """
  This idiom is used so often...
  Pick fist value unles it's None.

  Usage::
  
      >>> prefer_first( True, 42 )
      True
      >>> prefer_first( None, 42 )
      42

      ## Still pick 1st one if it's not None
      >>> prefer_first( False, 42 )
      False

      >>> prefer_first( 1, 2, 3 )
      1
      >>> prefer_first( None, 2, 3 )
      2
      >>> prefer_first( None, None, 3 )
      3
      >>> prefer_first( None, None, None ) is None
      True

  """
  for val in vals:
    if val is not None:
      return val 
  return val # last value in loop

#--------#
# STRING #
#--------#

def cut_minmax(p, valmin, valmax):
  """
  Simply parse 3 strings together in form of 'valmin < p && p < valmax'.
  Skip if val is None. Return empty string if both null.

  >>> cut_minmax( 'X', 10, 20 )
  '(X >= 10) & (X <= 20)'

  >>> cut_minmax( 'X', 12.3, None )
  'X >= 12.3'

  >>> cut_minmax( 'X', None, None )
  ''

  """
  queue = []
  if valmin is not None: queue.append(p+' >= '+str(valmin))
  if valmax is not None: queue.append(p+' <= '+str(valmax))
  return join(queue)

#-------------------------------------------------------------------------------

def pretty_array(arr):
  """
  Pretty-print an array('d') to not be too long, for logging.

  >>> from array import array
  >>> arr = array('d', [10*x**-2 for x in xrange(5,10)])
  >>> arr
  array('d', [0.4, 0.2777777777777778, 0.2040816326530612, 0.15625, 0.12345679012345678])
  >>> print(pretty_array(arr))
  array(0.40, 0.28, 0.20, 0.16, 0.12)

  """
  l = [ '%.2f'%d for d in arr ]
  s = str(l).replace("'",'').replace('[','').replace(']','')
  s = s[:75] + (s[75:] and '..')
  return "array(%s)" % s

#-------------------------------------------------------------------------------

def pretty_round(val):
  """
  Return string used in mean/RMS, with my custom format.

  >>> pretty_round(None)      # Nice null
  '---'
  >>> pretty_round(1234567)   # Too large
  '> 1E6'
  >>> pretty_round(-1234567)  # Too large
  '< -1E6'
  >>> pretty_round(2E-7)      # Tiny than 1E-6
  '< 1E-6'
  >>> pretty_round(3E-5)      # Small
  '3.00E-05'
  >>> pretty_round(12345)     # Large 
  '1.23E+04'
  >>> pretty_round(1.4142)    # Natural scale
  '1.41'

  """
  if val is None:
    return '---'
  if val > 1E6:  # So largely positive
    return '> 1E6'
  if val < -1E6: # So largely negative
    return '< -1E6'
  if 0 < val < 1E-6:  # So tiny near zero
    return '< 1E-6'
  if 0 < val < 1E-2:  # semi-small value
    return '{:.2E}'.format(val)
  if 1E4 < val < 1E9:  # semi-large value
    return '{:.2E}'.format(val)
  return "{:.2f}".format(val) # Human-friendly format

#-------------------------------------------------------------------------------

def concat(*tokens, **kwargs):
  """
  Custom method to concatenate list of string together, such that
  null is ignore ( being basestring or not ).
  Provide flag `delim` to change delimiter

  Use primarily on logic of QHist's naming

  >>> concat('prefix', 'root', 'suffix')
  'prefix_root_suffix'

  >>> concat(None, 'root', 'suffix', delim='/')
  'root/suffix'

  """
  delim = kwargs.get('delim', '_')
  return delim.join([ str(token).strip(delim) for token in tokens if token ])

#-------------------------------------------------------------------------------

def join(*cuts):
  """
  Given list of string (cuts), join them and parenthesis guard 
  (guard only the inner element, not the full outer, to avoid verbose double-guard)
  If the iterable is LIST/TUPLE/GEN, join with AND 
  If the iterable is SET           , join with OR 
  Designed for recursive usage.

  Note:
  - No using double-op '&&' to be LoKi-compatible.
  - The root argument, *args, by python's design, is intrinsically a tuple.
    So that's why one can pass arguments instead of list-of-string as arg.

  Args:
    cuts (iterable): Iterable (tuple/list/set) of string to join.

  Usage::

      ## Test basics
      >>> join([ 'a', 'b' ]) == join('a','b')
      True
      >>> join( 'a', 'b' )
      '(a) & (b)'
      >>> join({'a', 'b'})
      '(a) | (b)'

      ## Handle effective null
      >>> join()
      ''
      >>> join([])
      ''
      >>> join([''])
      ''
      >>> join([None])
      ''
      >>> join({''})  # List of null-cuts
      ''
      >>> join([('',),{''}])  # Super null!
      ''
      >>> join(['c > 0', ('',), ''])
      'c > 0'

      ## Simplify idempotent nesting
      >>> join([[( 'a > 3' )]])
      'a > 3'
      >>> join([ {'b1','b2'} ])
      '(b1) | (b2)'

      ## Handle nested
      >>> join( 'a', {'b1','b2'}, 'c' )
      '(a) & ((b1) | (b2)) & (c)'

      ## Trim whitespace 
      >>> join( 'a     > 5', 'b <    10' )
      '(a > 5) & (b < 10)'

  """

  ## Early kill the null-value on any case, string or not:
  if not cuts:
    return ''
  ## De-equip if it's single-tuple
  if isinstance( cuts, tuple ) and len(cuts)==1:
    cuts = cuts[0]
  ## Early deal with recursive: String is the atomic unit 
  if isinstance( cuts, basestring ):
    ## Simple aesthetic on string: Trim all multiple-whitespace to single one
    return ' '.join(cuts.split())

  ## Given now an iterable, determine the operator 
  #  (need this info before the cleansing).
  if isinstance( cuts, (list,tuple,types.GeneratorType) ):
    op = ' & '
  elif isinstance( cuts, set ):
    op = ' | '
  else: # pragma: no cover
    raise ValueError('Invalid iterable type: %r' % type(cuts))

  ## Apply recursion here, kill bad one before passing.
  cuts = [ join(c) for c in cuts if c ]
  ## Kill bad ones after recursion is applied
  cuts = [ c for c in cuts if c ]
  ## Empty list is discarded at this point
  if not cuts:  
    return ''
  ## Early deal with collection with one item: Extract it.
  if len(cuts) == 1:
    return cuts[0]
  ## Finally join with current op. Wrap inner item here, and only here
  return op.join([ '(%s)'%c for c in cuts])

#-------------------------------------------------------------------------------

def safename(s):
  """
  Return safename for ROOT.TFile creation

  >>> safename('Hello(world)')  # ROOT use bracket for something else
  'Hello{world}'

  >>> safename('PT/P')  # Bad for sys
  'PT_over_P'

  >>> safename('TMath::Log10(PT)')
  'Log10{PT}'

  >>> safename('P/1e3')
  'P'
  """
  ## remove const
  blacklist = ' ', '/1000', '/1e3', '/1E3', '*1000', '*1e3', '*1E3', '*1e6', '*1E6'
  for x in blacklist:
    s = s.replace(x, '')
  ## replace bad ones
  s = s.replace('(', '{').replace(')','}')  # Danger for root
  s = s.replace('/','_over_')
  s = s.replace('TMath::', '')  # Nicer name
  s = s.replace(':', '__') # APT:M --> APT__M
  s = s.replace('.', '_').replace('_pdf','.pdf').replace('_png','.png')
  return s

#-------------------------------------------------------------------------------

def shorten(s, width=78):
  """
  Helper method to shorten string (to 78 chars, terminal width) 
  for pretty-printing.

  >>> print(shorten('abcdefghijklmnopqrstuvwxyz'))  # not 78
  abcdefghijklmnopqrstuvwxyz
  
  >>> print(shorten('abcdefghijklmnopqrstuvwxyz'*10))
  abcdefghijklmnopqrstuvwxyzabcdefghijkl...pqrstuvwxyzabcdefghijklmnopqrstuvwxyz
  
  """
  s = str(s)
  return s if len(s)<width else (s[0:width/2-1]+'...'+s[len(s)-width/2+2:])

#-------------------------------------------------------------------------------

def split_dim(p):
  """
  Safe method to split multi-dim params string.
  Do not change any order

  >>> split_dim('MM:PT')
  ['MM', 'PT']
  >>> split_dim('TMath::Log10(MM): PT')
  ['TMath::Log10(MM)', 'PT']

  """
  l = p.replace("::","@").split(":")
  return [ x.replace("@","::").strip() for x in l ]

#-------------------------------------------------------------------------------

def dim(p):
  """
  Short-cut method of above: Return integer dimension of given string.
  Note that in this case, it can detect dim-0

  >>> dim('PT')
  1
  >>> dim('PT:PZ')
  2
  >>> dim('')
  0
  >>> dim( 'TMath::Log10(PT)' )
  1
  >>> dim( 'TMath::Log10(PT):PZ' )
  2
  """
  return len(split_dim(p)) if p else 0

#===============================================================================
