"""

Stats classes.

"""

from collections import namedtuple
from .. import utils

#==============================================================================

ProtoSingleStats = namedtuple('ProtoSingleStats', 'entries xmin xmax ymin ymax zmin zmax dim nbin')

def repr_stat(self):
  """
  Same representation.


  """
  ## Minimise the dimension
  fmt = 'X=[{0.xmin:.4}, {0.xmax:.4}]'
  if self.dim>=2:
    fmt += ' Y=[{0.ymin:.4}, {0.ymax:.4}]'
  if self.dim==3:
    fmt += ' Z=[{0.zmin:.4}, {0.zmax:.4}]'
  return fmt.format(self)

#-------------------------------------------------------------------------------

class SingleStats(ProtoSingleStats):
  """
  Proxy class that contains stats of single histogram of any dimension.
  Greatly relies on utils on 1-dim calculation.

  Specialized form of ProtoSingleStats by constructor made from TPC.
  
  Note: Per ROOT.TTree convention, 1D=X, 2D=Y:X, 3D=X:Y:Z

  Doctest::

      ## Constructor from TPC
      >>> SingleStats(tree, 'pi_BPVIP')
      N=303/20, X=[0.001842, 1.804]

      ## Null plot
      >>> SingleStats(tree, 'pi_BPVIP', 'pi_BPVIP < -10')
      N=0/20, X=[None, None]

      ## 2-dimensional
      >>> SingleStats(tree, 'pi_BPVIP: nPVs')
      N=303/20, X=[1.0, 1.0] Y=[0.001842, 1.804]

      ## 3D
      >>> SingleStats(tree, 'pi_BPVIP : nPVs : M/1e3')
      N=303/20, X=[0.001842, 1.804] Y=[1.0, 1.0] Z=[15.31, 86.44]
      
      ## 4D not supported
      >>> SingleStats(tree, 'pi_BPVIP:mu_BPVIP:1/pi_BPVIP:1/mu_BPVIP')
      Traceback (most recent call last):
      ...
      ValueError: Not support for dim > 3.

  """
  __slots__ = ()

  def __new__(cls, t, p, c=''):
    """
    Use `__new__` instead of `__init__` because of immutability
    """
    ## shortcut
    get = lambda p: utils.get_stats_single(t, p, c)
    ## Note: p can be 2 dimensions here
    dim = utils.dim(p)
    ymin = ymax = zmin = zmax = None
    if dim==1:
      entries, xmin, xmax = get(p)
    elif dim==2:
      py,px = utils.split_dim(p)
      xcount, xmin, xmax = get(px)
      ycount, ymin, ymax = get(py)
      assert xcount==ycount, "WTF!?"
      entries = xcount
    elif dim==3:
      px,py,pz = utils.split_dim(p)
      xcount, xmin, xmax = get(px)
      ycount, ymin, ymax = get(py)
      zcount, zmin, zmax = get(pz)
      assert xcount==ycount==zcount, "WTF!?"
      entries = xcount
    else:
      raise ValueError('Not support for dim > 3.')
    ## Estimate total number of bins
    nbin = utils.auto_bin_size(entries)
    ## Finally
    return super(SingleStats, cls).__new__(cls, entries, xmin, xmax, ymin, ymax, zmin, zmax, dim, nbin)

  def __repr__(self):
    """
    Minimise the dimension
    """
    fmt = 'N={0.entries}/{0.nbin}, '
    return fmt.format(self) + repr_stat(self)

#==============================================================================

class Stats(tuple):
  """
  Provide collective interpretation of SingleStats, handling null-plot along the way.
  Relies on utils.get_stats_single for the null-plot default values.

  Note:
  
  - Don't do entries, its interpretation is vague.
  - The default of empty-stats case should be the same defaults as QHist no-TPC case.

  Doctest::

      ## Empty instance (placeholder for empty QHist)
      >>> Stats()
      <Stats> len=0 nbin=None X=[None, None]

      ## Check collections
      >>> s1 = SingleStats(tree, 'pi_BPVIP', '')
      >>> s2 = SingleStats(tree, 'mu_BPVIP', '')
      >>> s3 = SingleStats(tree, 'pi_BPVIP:nPVs', '')
      >>> s0 = SingleStats(tree, 'pi_BPVIP', 'pi_BPVIP<-10')

      >>> Stats([s1]) # single
      <Stats> len=1 nbin=20 X=[0.001842, 1.804]
      
      >>> Stats([s1,s2]) # stacked
      <Stats> len=2 nbin=20 X=[0.0005247, 1.804]
      
      >>> Stats([s3]) # 2dim
      <Stats> len=1 nbin=20 X=[1.0, 1.0] Y=[0.001842, 1.804]

      >>> Stats([s2, s0]) # with null
      <Stats> len=2 nbin=20 X=[0.0005247, 0.9826]

      ## Invalid type for constructor
      >>> Stats(['string', 123])
      Traceback (most recent call last):
      ...
      TypeError: Need a collection of <ProtoSingleStats>.

      ## Invalid dim for constructor
      >>> Stats([s1, s3])
      Traceback (most recent call last):
      ...
      ValueError: Inconsistent dimension: [1, 2]

  """

  def __new__(cls, *args):
    """
    Default constructor made from list of ProtoSingleStats
    Same signature as regular-tuple.
    """
    ## Non-empty list is given, validate it.
    assert len(args) <= 1
    if len(args)==1:
      list_single_stats = args[0]
      if not all(isinstance(obj, ProtoSingleStats) for obj in list_single_stats):
        raise TypeError('Need a collection of <ProtoSingleStats>.')
      if not len({obj.dim for obj in list_single_stats})==1:
        dims = [obj.dim for obj in list_single_stats]
        raise ValueError('Inconsistent dimension: %s'%dims)
    ## finally
    return super(Stats, cls).__new__(cls, *args)

  @classmethod
  def from_list_TPC(cls, list_tpc):
    """
    Specialized constructor from list of TPC
    """
    return cls([SingleStats(*tpc) for tpc in list_tpc])

  def __repr__(self):
    return '<Stats> len=%i nbin=%s '%(len(self),self.nbin) + repr_stat(self)

  @property
  def nbin(self):
    """ 
    Return the estimated appropriate total number of bins (all dims).
    """
    # if not self: return None  # Prefer to return None on nbin, to be like others
    l = [ s.nbin for s in self if s.nbin is not None ]
    return min(l) if l else None 

    # l = [ s.entries for s in self if s.entries > 0 ]
    # entries = min(l) if l else 0 # Make binning from smallest entries
    # # Leave auto_bin_size to deal with all-null stats
    # # Unlike the above case where there're no stats at all, 
    # # this is where there're stats but they are null
    # return utils.auto_bin_size(entries)
  
  @property
  def dim(self):
    """Consistent dim across all stats."""
    return 0 if not self else self[0].dim

  @property
  def xmin(self):
    l = [ s.xmin for s in self if s.xmin is not None ]
    return min(l) if l else None 
  @property
  def xmax(self):
    l = [ s.xmax for s in self if s.xmax is not None ]
    return max(l) if l else None 
  @property
  def xlog(self):
    return utils.auto_log( self.xmin, self.xmax )
  @property
  def ymin(self):
    l = [ s.ymin for s in self if s.ymin is not None ]
    return min(l) if l else None 
  @property
  def ymax(self):
    l = [ s.ymax for s in self if s.ymax is not None ]
    return max(l) if l else None 
  @property
  def ylog(self):
    return utils.auto_log( self.ymin, self.ymax )
  @property
  def zmin(self):
    l = [ s.zmin for s in self if s.zmin is not None ]
    return min(l) if l else None 
  @property
  def zmax(self):
    l = [ s.zmax for s in self if s.zmax is not None ]
    return max(l) if l else None 
  @property
  def zlog(self):
    return utils.auto_log( self.zmin, self.zmax )
  
#==============================================================================
