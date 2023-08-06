"""

Wrapper class around ROOT::TTree::Draw method to plot histograms. 
Simple things should be simple to use...


Note on auto-legend logic (work-in-progress)

Target:
- xlabel, ylabel
- legend (console)

1. If expansion == 1: Simple 

2. elif {params} == 1: (Predict)

.
.
.

"""

import os
import inspect
import types
import math
import __main__ # For current script name
import ROOT
from datetime import datetime

## Local package
from .. import logger, utils
from ..functools import prop
from . import wrappers

## 3rd-party
from PythonCK.decorators import lazy_property

## Invoke default style at global level
## TODO: disabled it until first-use, in favor of having lazy-import ROOT
# from . import styles
# ROOT.gROOT.SetStyle('QHist')


__all__ = (
  'QHist', 
)

#==============================================================================


class metaQHist(type):

  def __new__(cls, name, parents, dct):
    # print cls      # metaQHist
    # print name     # QHist
    # print parents  # 'object'
    # print dct      
    qhist = super(metaQHist, cls).__new__(cls, name, parents, dct)
    qhist._initial_state = dct 
    return qhist

  def __setattr__( self, key, val ):
    # print 'metaQHist', key, val
    super(metaQHist, self).__setattr__(key, val)


class QHist(list):
  """
  The ultimate wrapper around TTree.Draw for better analysis!

  ## Core features

  - Simplified interface, most often-used options are brought in instance's property 

  - Pythonic approach to make superimposing histograms as quick as possible

  - Drawing over large collection is simple with flag sharing

  - Axis control & binning are automatically cover for best ranges.

  - Handle auto saving *.pdf file, and *.root file after plot.

  - Support protocol for `TH1D`, `TH2D`, `TProfile`

  - Auto bind the lifecycle of TObject instance upon `setattr` via `ROOT::SetOwnership`

  - Itself is a subclass of list, containing all histogram used in the superpositioning.


  !!  Leveraging concurrency when superimposing plots. --> NOPE, TTree is NOT THREAD_SAFE!

  """
  __metaclass__ = metaQHist

  ## CORE: REQUIRED FIELDS
  trees       = prop(None   , "List of, or one instance of ROOT::TTree")
  params      = prop(None   , "List of, or one string represent TBranch's name to plot. For 2D, use X:Y convention")
  expansion   = prop([]     , "(For advance usage) Manual expansion of t-p-c. This will override trees/params/cuts.")

  ## IMPORTANT OPTIONAL
  cuts        = prop(""     , "List of, or one string for param cuts")
  filters     = prop(""     , "List of cuts which will be applied at all time. Apply AND-boolean on all given.")
  legends     = prop(None   , "List of, or one string to show as legends")

  ## NAMING / OUTPUTS
  name        = prop(None   , "Name of the output file. Default=temp_timestamp.")
  title       = prop(None   , "Title of the histogram, equal to self.name unless specified.")
  # output_path = prop('fig/' , "Default output location")  ## Determined automatically instead
  prefix      = prop(''     , "Prefix to append to the name/title. For advance usage.") 
  suffix      = prop(''     , "Suffix to append to the name/title. For advance usage.") 
  comment     = prop(None   , "Extra comments to write on canvas")
  auto_name   = prop(False  , 'If True, this turns on auto-naming feature (figure out frmo input args). Implies autosave too.')

  ## AXIS CONTROL
  xmin    = prop(None , "Min of x-axis. Implies implicit-cut on given params.")
  xmax    = prop(None , "Max of x-axis. Implies implicit-cut on given params.")
  xbin    = prop(None , "Number of bins on x-axis")
  xlog    = prop(None , "Use axis in logarithm scale? If None, QHist will try to guess for you.") 
  xlabel  = prop(''   , "String to display the x-axis label")
  ymin    = prop(None)
  ymax    = prop(None)
  ybin    = prop(None)
  ylog    = prop(None)
  ylabel  = prop('')
  zbin    = prop(10 , "(TH2F only) Number of contour level.")
  zlog    = prop(None)
  veto    = prop(tuple(), "EXPERIMENTAL: Kill certain value for better auto-plotting, e.g., [ -1E16 ]")

  ## CANVAS
  options    = prop(""   , "Additional options flag to add to TTree::Draw stage.")
  stack      = prop(False, "If True, the histogram will stack on top of each other (Using THStack)")
  normalize  = prop(True , """
    Specify the normalization scheme. 
    - True  : All plots will be normalized to 1.
    - False : No normalization. All histograms retain their counts.
    - [int] : Each histogram will be normalize to int given. The size of list MUST corresponds to expansion.
  """)
  batch      = prop(None, 'True to wrap with gROOT.SetBatch, False is explicitly intr, None is to leave to existing value.')

  # STYLES - AESTHETICS
  st_line   = prop(True , "Uses lines' auto-style? (straight, dash, ...)")
  st_color  = prop(True , "Uses lines' auto-color?")
  st_marker = prop(False, "Uses marker style?")
  st_fill   = prop(False, "Fill?")
  st_grid   = prop(True , "True/False to show the grid.")
  st_code   = prop(None , "Experimental: Style-code")

  def __init__(self):
    super(QHist, self).__init__()
    for key in dir(self):
      if key not in ('height_console', 'dim', 'expansion'):
        val = getattr(self,key)
        if isinstance(val, list):  # Fixing mutable attr from class
          logger.debug('Patching mutable: %s: %r'%(key,val))
          setattr(self, key, list(val))

  def __setattr__(self, key, value):

    # print key, hasattr(self,key), type(getattr(self.__class__,key,None)), isinstance(getattr(self.__class__,key,None), property)

    # ## Raise if this attr is unknown
    # if not key.startswith('_') and not isinstance(getattr(self.__class__,key,None), property):
    #   raise AttributeError('Unknown attribute: %r'%key)


    ## Set it
    super(QHist, self).__setattr__(key, value)
    
    ## Bind the lifetime of TObject to this QHist instance
    if isinstance(value, ROOT.TObject):
      logger.debug('Binding lifecycle: %s'%str(value))
      ROOT.SetOwnership(value, False)

  @classmethod
  def reset(cls):
    """ Upon call, reset its attributes to original value """
    logger.debug("QHist::reset")
    for key, val in cls._initial_state.iteritems():
      if isinstance(val, property):
        setattr(cls, key, val) 

  @property # don't use lazy
  def is_prof(self):
    """True if the option for `profile` plot is flagged."""
    return 'prof' in self.options

  # @lazy_property
  # def is_complex_normalize(self):
  #   # Identify complex normalization (nmz over given range)
  #   return isinstance(self.normalize,(tuple,list))

  @lazy_property
  def dim(self):
    """
    Return dimensionality of the params. Expected to be called after expanded.
    """
    # Also, verify dimension-homogeneity of params (i.e., don't mix 1D,2D plot)
    # if not self.expansion:  # For default-value report.
    #   return None
    l = { utils.dim(p) for _,p,_ in self.expansion } # Loop over container of p
    if len(l) != 1:
      raise ValueError("Dimension of self.params is not balanced... Abort: \n%r"%self.expansion)
    dim = l.pop()
    return dim

  @property
  def height_console(self):
    """Absolute height of debug console, depends on number on lines."""
    return len(list(self.gen_debug_msg())) * 15

    # lines = 3  # By default: axis, script, timestamp
    # # Number of trees
    # if self.expansion:
    #   lines += len(set(t.GetName() for t,_,_ in self.expansion))  
    # else:
    #   ## Equip to list if needed. 
    #   if isinstance(self.trees, ROOT.TTree):
    #     trees = [ self.trees ] # Don't use list(TChain), it explodes.
    #   elif isinstance(self.trees, (list,tuple)):
    #     trees = self.trees
    #   else:
    #     trees = []  # None
    #   lines += len(trees) # Need equip list because QHist cls 
    # if self.comment:
    #   lines += 1 
    # lines += len(list(self.filters))
    # return 15*lines

  @property
  def height_legend(self):
    """Careful, get me only after I have expansion"""
    return 15*(len(self.expansion)+1) if self.expansion is not None else 0

  @lazy_property
  def str_now(self):
    """
    Can be lazy. It's called at debug-console timestamp, but can also be
    called earlier at null-name plot.
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S%f")

  @property
  def filename(self):
    """Return the current filename (without path, nor extension)"""
    return os.path.splitext(os.path.split(__main__.__file__)[-1])[0]

  @property 
  def output_path(self):
    """
    Return destination directory, by default, made of script filename.
    It'll also try to make sure that the path is relative to the 
    script's path, not caller's path.
    """
    basedir = os.path.split(__main__.__file__)[0]
    return os.path.join( basedir, self.filename )

  @property
  def fullpath_safe(self):
    """
    Extension of above, returning target filename+path of safename ready to be
    saved as PDF.
    """
    filename      = "%s.pdf" % self.name
    filename_safe = utils.safename(filename)
    return os.path.join(self.output_path, filename_safe)

  def get_complete_cuts(hist, p, c):
    """
    Return the root-string represent the efffective cut.

    The complete cut is composed of these components:
      1. Explicit cut: c 
      2. Implicit/Axis cut
      3. Master cut
      4. Veto: p != val

    Input: Note that p can be 1D/2D

    Note: If is_prof is True, the cut on y-axis should NOT be 
    added to this since it directly affect the result.
    """
    complete_cuts = []

    def add_if_nonnull(val):
      """Helper method to collect complete_cuts"""
      if val:
        if isinstance(val, basestring):
          complete_cuts.append(val)
        elif isinstance(val, (list,tuple)):
          complete_cuts.extend(val)
        else:
          raise NotImplementedError

    add_if_nonnull(c)
    add_if_nonnull(hist.filters)
    if hist.dim==1: 
      add_if_nonnull(utils.cut_minmax(p, hist.xmin, hist.xmax))
    elif hist.dim==2:
      py,px = utils.split_dim(p)
      add_if_nonnull(utils.cut_minmax(px, hist.xmin, hist.xmax))
      if not hist.is_prof:
        add_if_nonnull(utils.cut_minmax(py, hist.ymin, hist.ymax))
    elif hist.dim == 3 and hist.is_prof:
      pz,py,px = utils.split_dim(p)
      add_if_nonnull(utils.cut_minmax(px, hist.xmin, hist.xmax))
      add_if_nonnull(utils.cut_minmax(py, hist.ymin, hist.ymax))

    for val in hist.veto:
      add_if_nonnull( '(%s != %f)'%(p,val) )
    result = utils.join(complete_cuts)
    # Small aesthetics: Trim all multiple-whitespace to single one
    return ' '.join(result.split())

  def gen_debug_msg(self):
    """
    Generate the entries for debug console.
    """
    ## Mastercut
    for cut in self.filters:
      if cut: 
        yield 'MasterCUT', cut

    ## Trees
    used_names = set()
    for t,_,_ in self.expansion:
      tname = t.title
      if tname not in used_names:
        used_names.add(tname)
        yield 'TTree', '{} [{}]'.format(tname, t.entries)

    ## Implicit cut & Xaxis
    xmin = utils.prefer_first(self.xmin, "Auto=%.2E" % self._xmin)
    xmax = utils.prefer_first(self.xmax, "Auto=%.2E" % self._xmax)
    xbin = utils.prefer_first(self.xbin, "Auto=%i"   % self._xbin)
    ymin = utils.prefer_first(self.ymin, '---' if not self._ymin else "Auto=%.2E" % self._ymin) # Another guard for early self.height_console
    ymax = utils.prefer_first(self.ymax, '---' if not self._ymax else "Auto=%.2E" % self._ymax)
    ybin = '' if (self.dim==1 or self.is_prof) else '/%s'%utils.prefer_first(self.ybin, "Auto=%i" % self._ybin)
    # ybin = 'TODO' # conflict with new Wrapper
    yield "Axis", "x=[%s, %s]/%s, y=[%s, %s]%s" % (xmin, xmax, xbin, ymin, ymax, ybin)

    ## Veto
    if self.veto: 
      yield 'Veto', str(self.veto)
    ## Notes
    if self.comment: 
      yield "Comment", self.comment
    ## Timestamp
    yield 'Timestamp', self.str_now
    ## Script 
    yield 'Script', os.path.abspath(getattr(__main__, '__file__', '(interactive)'))

  def __determine_style_code(self):
    """ EXPERIMENTAL! Guess the style-code current config belongs to."""
    if self.st_code is not None:
      return self.st_code
    if self.legends is None:
      return 0
    else:  
      # 1. Styling for 1xREAL + NxMC
      if 'MC' not in self.legends[0] and all(['MC' in name for name in self.legends[1:]]):
        return 1

  #---------------------------------------
  def _initial_validation_auto_exp(self):
  #---------------------------------------

    # Verify TREES/PARAMS
    assert bool(self.trees), "Missing input trees"
    assert bool(self.params), "Missing input params"

    # Equip CUTS, PARAMS, LEGENDS
    if isinstance(self.trees, ROOT.TTree):  # careful, TTree itself is also iterable
      self.trees   = [ self.trees ]
    if isinstance(self.params, str):
      self.params  = [ self.params ]
    if isinstance(self.cuts, str):
      self.cuts    = [ self.cuts ]

    # Verify the contents
    assert None not in self.trees, "Found bad entry in self.trees: %r" % self.trees 

    ## EXPANSION is a core item. This is a list of (t,p,c) tuple to be plotted.
    self.expansion = [(t,p,ct) for t in self.trees for p in self.params for ct in self.cuts]


  #-----------------------------------------
  def _initial_validation_manual_exp(self):
  #-----------------------------------------

    ## Assert that this is a list/tuple
    exp = self.expansion
    assert isinstance(exp, (list, tuple)), "Invalid type of self.expansion"

    ## Assert each memner has 3 submembers, of (TTree, str, str)
    for member in exp:
      assert len(member) == 3, "Invalid TPC triplet member."
      assert isinstance(member[0], ROOT.TTree), "Invalid T-member (expected ROOT.TTree)"
      assert isinstance(member[1], basestring), "Invalid P-member (expected basestring)"
      assert isinstance(member[2], basestring), "Invalid C-member (expected basestring)"


  def _validate(self):

    # assert self.dim in (1,2), "Bad self.dim: %r" % self.params
    assert isinstance(self.veto, (float, tuple, list))
    assert isinstance(self.normalize, ( bool, tuple, list ))
    if isinstance(self.normalize, (tuple,list)):
      assert len(self.normalize) == len(self.expansion)
      assert all( isinstance(val, (int,long,float,bool)) or callable(val) for val in self.normalize )

    ## If prof is used, required dim==2,3
    if self.is_prof:
      assert self.dim in (2,3), 'Requred dim==2/3 with `prof` flag'
      # assert self.ylog is not True, "Bug in y-log in TProfile. Fixed in v3"
    else:
      assert self.dim in (1,2), 'Requred dim==1/2'


  #--------------------------------------------------------------------

  def _loop_first_pass(self):
    """
    Given expansion, do the 1st-pass to collect info on (xy)min/max in order 
    to know the true coverage across all expansion members.
    """

    ## Skip loop-first-pass if all axis limit is given

    if self.is_prof and self.dim==3:
      queues = self.xmin, self.xmax, self.xbin, self.ymin, self.ymax, self.ybin
      if all( val is not None for val in queues):
        logger.debug('Sufficient info to skip loop-first-pass')
        self._xmin = self.xmin
        self._xmax = self.xmax
        self._xbin = self.xbin
        self._ymin = self.ymin
        self._ymax = self.ymax
        self._ybin = self.ybin
        return

    if (self.dim == 1) or (self.dim==2 and self.is_prof):
      queues = self.xmin, self.xmax, self.xbin 
      if all( val is not None for val in queues):
        logger.debug('Sufficient info to skip loop-first-pass')
        self._xmin = self.xmin
        self._xmax = self.xmax
        self._xbin = self.xbin
      # optional
      self._ybin = None
      self._ymin = utils.prefer_first( self.ymin, 0. )
      self._ymax = utils.prefer_first( self.ymax, 0. )
      return      

    # ----

    if self.dim == 1:
      list_tpc    = ((t,p,self.get_complete_cuts(p,c))   for t,p,c in self.expansion )
      ## TODO: _stats is too monkeyish.
      self._stats = [ utils.get_stats_single(t,p,c) for t,p,c in list_tpc ] # count/min/max
      lcount, lmin, lmax = zip(*self._stats)
      ## Remove None
      lcount = [ x for x in lcount if x is not None ]
      lmin   = [ x for x in lmin   if x is not None ]
      lmax   = [ x for x in lmax   if x is not None ]
      xcount, xmin, xmax = int(min(lcount)), min(lmin), max(lmax)

    elif self.dim == 2:
      list_tpcX = []
      list_tpcY = []
      for t,p,c in self.expansion:
        py,px = utils.split_dim(p)
        cc    = self.get_complete_cuts(p,c)
        list_tpcX.append([t, px, cc])
        list_tpcY.append([t, py, cc])
      xcount, xmin, xmax = utils.get_stats(list_tpcX) 
      ycount, ymin, ymax = utils.get_stats(list_tpcY) 

    else:
      raise NotImplementedError;

    ## Slight bin enlargement by ~1%
    xmax *= 1.01

    # Select the final effective value
    self._xmin = utils.prefer_first(self.xmin, xmin)
    self._xmax = utils.prefer_first(self.xmax, xmax)
    self._xbin = utils.prefer_first(self.xbin, utils.auto_bin_size(xcount))
    if self.dim==2:
      self._ymin = utils.prefer_first(self.ymin, ymin)
      self._ymax = utils.prefer_first(self.ymax, ymax)
      self._ybin = utils.prefer_first(self.ybin, utils.auto_bin_size(ycount))
    else:
      self._ymin = self._ymax = self._ybin = None

  def _summary_loop_first_pass(self):
    logger.debug('### Summary: _loop_first_pass')
    logger.debug("_xmin : " + str(self._xmin))
    logger.debug("_xmax : " + str(self._xmax))
    logger.debug("_xbin : " + str(self._xbin))
    logger.debug("_ymin : " + str(self._ymin))
    logger.debug("_ymax : " + str(self._ymax))
    logger.debug("_ybin : " + str(self._ybin))


  #--------------------------------------------------------------------

  def _prepare_drawing_base(self):
    """
    This will make all preparation on all vars, directories, canvas, etc.
    """

    #------------------------#
    # Equip correct datatype #
    #------------------------#

    if isinstance(self.filters, str):
      self.filters = [ self.filters ]  # Homogenize with other. AND-all
    if isinstance(self.legends, str):
      self.legends = [ self.legends ]
    if isinstance( self.veto, float ):
      self.veto = [ self.veto ]

    if isinstance( self.normalize, bool ):
      self.normalize = [ self.normalize ] * len(self.expansion)

    #-------------------#
    # Setting up the IO #
    #-------------------#

    ## Make output path
    if not os.path.exists(self.output_path):
      os.makedirs(self.output_path) 
      logger.debug('Created output_path: ' + self.output_path)
    # if not os.path.exists(self.output_path + '/temp'):
    #   os.makedirs(self.output_path + '/temp')

    #--------------------------------#
    # Name / Title / Prefix / Suffix #
    #--------------------------------#

    ## Figure-out the name, 
    if not self.name:
      if self.auto_name:  # Hmm, figure out a good name...
        ## 1. single param
        if len(self.params)==1:
          name = self.params[0]
        else:
          raise ValueError('Unconfigured auto-save naming scheme.')
        ## 2. Use safe name
        name = utils.safename(name)
        ## Finally, log it down
        self.name = name
        logger.debug('Autoname: %r' % name)
      else:
        self.name = 'temp_'+self.str_now


    ## If name is None, do the standard timestamp
    # self.str_now = datetime.now().strftime("%Y%m%d_%H%M%S")
    # if not self.name:

    ## Set title default to self.name, unless given
    if not self.title:
      self.title = self.name

    ## Optional '_' on prefix/suffix
    if self.prefix and not self.prefix.endswith('_'):
      self.prefix = self.prefix+'_'
    if self.suffix and not self.suffix.startswith('_'):
      self.suffix = '_'+self.suffix

    ## Apply prefix/suffix if needs, to both name/title
    if not self.name.startswith('temp_'): # exclude the temp mode
      if not self.name.startswith(self.prefix):
        self.name   = self.prefix + self.name
      if not self.name.endswith(self.suffix):
        self.name  += self.suffix

    ## For title, add regardless the temp
    if not self.title.startswith(self.prefix):
      self.title  = self.prefix + self.title
    if not self.title.endswith(self.suffix):
      self.title += self.suffix

    ## Finally, clean name (can be very weird name disturbing the namespace).
    self.name = utils.safename(self.name)

    #--------------------#
    # Instantiate CANVAS #
    #--------------------#

    ### NEW STYLING
    # qhistStyle.apply()

    ## Determine the dimension of the canvas (a priori, not including legend+console)
    width, height = 800,450  # Fixed default. If you need something else, modified from drew QHist in ROOT file.
    height += self.height_console
    height += self.height_legend

    ## TODO: If legend & console is disabled, lower the height

    # INIT: Canvas
    self.c = ROOT.TCanvas(self.name, self.title, width, height)

    ## INIT: Debug console & its pad (we start from bottom-most pad first)
    rheight_console = 1./height * self.height_console
    self.dpad = ROOT.TPad('debugPad', 'debugPad', .01, .01, .99, rheight_console)
    self.dpad.Draw()

    # INIT: Legend & its pad
    rheight_legend = 1./height * self.height_legend
    self.l    = ROOT.TLegend(0., 0., 1., 1., "", "NDC")  # Whatever 
    self.lpad = ROOT.TPad('legendPad', 'legendPad', .01, rheight_console, .99, rheight_console+rheight_legend)
    self.lpad.Draw()

    # Setup the upperPad
    self.upperPad = ROOT.TPad("upperPad", "upperPad", .005, rheight_console+rheight_legend, .995, .995)
    self.upperPad.Draw()   
    self.upperPad.cd()

    ## AXIS control: Only after bin/min/max determination is completed
    if self.xlog is None: # Guess! 
      # Some bound within [0,1], don't do log
      if self._xmin > 0. and self._xmax < 1.: 
        self.xlog  = False
      # Some bound within [0,2pi], don't do log
      if self._xmin > 0. and self._xmax < math.pi*2: 
        self.xlog  = False
      # Diff is more than 2 magnitude, do log
      elif self._xmin and self._xmax/self._xmin >= 1E3:
        self.xlog = True 
      else:
        self.xlog = False
      logger.debug('Guessing xlog: None --> %r' % self.xlog)
    if self.ylog is None:
      self.ylog = False # Guesswork not support yet. Conflict between 1D/2D
    if self.zlog is None:
      self.zlog = False
      
    ROOT.gPad.SetLogx(int(self.xlog)) # ++ method for var bin size
    ROOT.gPad.SetLogy(int(self.ylog))
    ROOT.gPad.SetLogz(int(self.zlog))

    #-----------------------#
    # Auto LEGENDS / LABELS #
    #-----------------------#

    ## Extra work on auto legends
    if not self.legends:
      # Default to most generic solution first
      self.legends = [ "[%i] tree=%s, param=%s, cut=%s"%(i,t.name,p,c) for i,(t,p,c) in enumerate(self.expansion) ]

      # More sophistication if needed
      if (self.trees is not None) and (self.params is not None): # auto-exp
        if len(self.trees)>=1 and len(self.params)==1 and len(self.cuts)==1:  # by trees (REMARK: T >= 1)
          self.legends = [ t.GetTitle().split('::')[-1].split('/')[-1] for t in self.trees ] # Remove Ganga's prefix. It'll be in debug console later.
        elif len(self.trees)==1 and len(self.params)>1 and len(self.cuts)==1:  # by params
          self.legends = [ p for p in self.params ]
        elif len(self.trees)==1 and len(self.params)==1 and len(self.cuts)>1:  # by cuts
          self.legends = [ c for c in self.cuts ]

    ## Auto-guess xlabel
    if not self.xlabel:
      params = list({ p for _,p,_ in self.expansion })
      if len(params)==1: # Single-param case
        if self.dim == 1:
          self.xlabel = params[0]
        elif self.dim == 2:
          py,px = utils.split_dim(params[0])
          self.xlabel = px
          self.ylabel = py
        elif self.dim == 3:
          pz,py,px = utils.split_dim(params[0])
          self.xlabel = px
          self.ylabel = py

    ## Finally, latexize the label after determination
    # func = utils.lhcb_latexize
    # self.xlabel   = func(self.xlabel)
    # self.ylabel   = func(self.ylabel)
    # self.legends  = [ func(s) for s in self.legends ]

    #--------#
    # Others #
    #--------#

    ## EXPERIMENTAL: Setting styles (Need to do thise before building auto-legend)
    self.style_code = self.__determine_style_code()


  # #----------------------------------------------------------------
  # def _loop_complex_normalize(self):
  #   """Extra-pass: Get the integral for custom normalization"""
  # #----------------------------------------------------------------

  #   logger.debug("---------- Custom normalization ----------")
  #   nmin, nmax = self.normalize
  #   nbin = int((nmax-nmin) / ((self._xmax-self._xmin)/self._xbin))
  #   spec = "(%i,%f,%f)" % (nbin,nmin,nmax)

  #   self.collect_intg = []
  #   for i,t,p,c in enumerate(expansion):
  #     # xmin = self.xmin if self.xmin is not None else self.exp_xmin[i] 
  #     # xmax = self.xmax if self.xmax is not None else self.exp_xmax[i]
      
  #     hname = "htemp_1stpass_%i" % i
  #     tree.Draw(param + " >> " + hname + spec, cut, "goff")
  #     hc    = eval(hname)
  #     xaxis = hc.GetXaxis()
  #     bmin  = xaxis.FindBin(nmin)
  #     bmax  = xaxis.FindBin(nmax)
  #     intg  = hc.Integral(bmin, bmax)
  #     logger.debug("| hname : " + hname + spec +" ---------------")
  #     logger.debug("| xaxis.FindBin(nmin): %i" % bmin)
  #     logger.debug("| xaxis.FindBin(nmax): %i" % bmax)
  #     logger.debug("| intg (before corr) : %f" % intg)
  #     intg -= hc.GetBinContent(bmin)*(nmin-xaxis.GetBinLowEdge(bmin))/ \
  #                 xaxis.GetBinWidth(bmin)
  #     intg -= hc.GetBinContent(bmax)*(xaxis.GetBinUpEdge(bmax)-nmax)/ \
  #                 xaxis.GetBinWidth(bmax)
  #     logger.debug("| intg (after corr)  : %f" % intg)
  #     self.collect_intg.append(intg)
  #   logger.debug("------------------------------------------")


  #------------------------------------------------------------------
  def _report_stats(self):
    """Report all stats for this QHist before doing the drawing"""
  #------------------------------------------------------------------

    def msg(key, defval, strval):
      star = '*' if defval!=strval else ' '
      if defval=='':
        defval = "''"
      key  = key[:18]  # Cutoff width
      return '{key:18}| {star} {strval}'.format(**locals())

    def is_good_keyval(key, val):
      if inspect.ismethod(val):  # method
        return False
      if isinstance(val, types.BuiltinFunctionType):
        return False
      if key.startswith('_'): # Internal
        return False
      if len(key)==1:  # singleton TObject
        return False 
      if key.lower().endswith('pad'):  # internal pads
        return False
      if key[0].isupper(): 
        return False
      if key.startswith('var'):
        return False
      if key in ('expansion', 'height_console', 'dim'): # Skip me
        return False
      return True

    # Default instance to check for default value
    default_instance = QHist()

    logger.debug("-"*100)
    logger.debug("QHist::" + self.name)
    logger.debug('        KEY       |  VALUE  ( * differs from default )')
    for key in dir(self):
      val = getattr(self, key)
      if is_good_keyval(key, val):
        defval = str(getattr(default_instance, key, None))
        strval = str(val)
        # Break into several lines instead if it's a long list
        if len(strval)>60 and isinstance(val, (list,tuple)):
          for i,subval in enumerate(val):
            if i==0:
              line = msg(key, defval, str(subval))
            else:  # Omit the key+defval
              line = msg('',None,str(subval))
            logger.debug(line)
        else:
          logger.debug(msg(key,defval,strval))
    logger.debug("-"*100)

  #--------------------------------------------------------------------

  def _draw_wrapped_single(self, wrapper, i, tree, param, cut):
      ## Prelim
      hname = "%s_hc_%02i" % (self.name,i)
      htemp = wrapper.new(self, hname, hname)
      c     = self.get_complete_cuts(param, cut)  # Need pre-reverse param

      ## HACK TO ALLOW WEIGHT, need a float cut instead of boolean
      c = c.replace('&','*')

      ## Apply aesthetics
      opt_tree, opt_legend = wrapper.style(self, htemp, i)
      opt_user = self.options

      ## Final report before draw
      logger.debug("----- DRAW %s: %02i"%(wrapper.__class__, i))
      logger.debug("hname      : " + hname)
      logger.debug("tree       : " + tree.title)
      logger.debug("param      : " + param)
      logger.debug("cut        : " + c)
      logger.debug("opt_tree   : " + opt_tree)
      logger.debug("opt_user   : " + opt_user)
      logger.debug("opt_legend : " + opt_legend)

      #------------------------------------------------------------------------#
      # Note: Enforce vanilla TTree
      tree.Draw(\
        param + " >> " + hname, \
        c, \
        "goff " + opt_tree + ' ' + opt_user
      )
      # logger.debug('DRAW::nCountVisible --> '+str(nCountVisible))
      #------------------------------------------------------------------------#

      # Save pointer to (cloned) individual histogram into self, using eval()
      # Note: Eval trick works only with "from ROOT import *"
      htemp.option = "sames "+opt_tree+' '+opt_user
      self.append(htemp)

      ## Final optional post-processor
      wrapper.midcycle_postprocess(self, htemp, i)

      ## Supply manual legend, extra touch on first col.
      for icol, val in enumerate(wrapper.midcycle_legend_entry(self, htemp, i)):
        self.l.AddEntry(htemp, str(val), '' if icol else 'lpf')


  def _draw_wrapped(self, wrapper):
    """
    Core method of drawing. Do all the generic task of drawing here until
    the deletation to the respective wrapper.
    """

    logger.debug("##### Arrive at new upperPad #####")
    wrapper.precycle_process(self)

    ## Prepare array (with, or without 1-st pass)
    self._xarr = utils.make_bins(self._xmin, self._xmax, self._xbin, self.xlog)

    ## Prepare the legends header
    header = wrapper.legend_header
    self.l.SetNColumns(len(header))
    for val in header:
      self.l.AddEntry('', val, '')  # Last flag is to disable markers

    ## Loop over each expansion
    for i, (tree, param, cut) in enumerate(self.expansion):
      self._draw_wrapped_single( wrapper, i, tree, param, cut)

    ## End of pad. Combine.
    logger.debug("### Arrive at EndPad ###")

    ## 
    if self.st_code == 2: ## Experimental partial stacking
      ## Draw a stack behind
      self._stack = ROOT.THStack(self.name, self.title) # Attaching lifecycle
      for i,h in enumerate(self):
        if i>0:
          opt = h.option.strip()
          h.markerSize = 0.
          self._stack.Add(h, opt)
          logger.debug('Loop stack: '+ h.name + ', opt:' + opt)
      self._stack.Draw()
      
      ## Draw data later to be on top
      h0 = self[0]
      h0.markerStyle     = 20  # LHCb
      h0.markerSize      = 0.8
      if not (self.normalize[0] is True): # raw number, not nor
        h0.binErrorOption  = ROOT.TH1.kPoisson
      h0.Draw('E1 sames')

      ## TODO: This should be supercede by explicit setting of qhist.ymax
      # self._ymin = min([ self._stack.minimum, h0.minimum ])
      if self.ymax:
        self._ymax = self.ymax 
      else:
        y1 = self._stack.maximum
        y2 = h0.maximum
        if y2 > 1: y2 += y2**0.5  # with Poisson err, if unnormalized
        self._ymax = max([y1, y2]) 
      self._stack.minimum = self._ymin
      self._stack.maximum = self._ymax
      self._stack.histogram.XTitle = self.xlabel
      self._stack.histogram.YTitle = self.ylabel

    else:
      self.hfin = hfin = wrapper.new(self, self.name, self.title) 
      wrapper.endcycle_preprocess(self, hfin)
      hfin.Draw()
      for h in self: 
        opt = h.option.strip() # Need strip, because whitespace in "sames " harms
        logger.debug('Loop draw: '+ h.name + '.Draw("' + opt + '")')
        h.Draw(opt) 

      ## Another pass to draw component through the filling
      ## http://svnweb.cern.ch/world/wsvn/lhcb/Urania/trunk/RootTools/LHCbStyle/src/myPlot.py
      # for h in self:
      #   h.SetFillStyle(0)
      #   # h.SetFillColorAlpha(0, 0.0)
      #   h.DrawCopy('SAMES')
      #   h.SetFillStyle(1001)  # Restore


    ## Finally, update canvas
    self.upperPad.Modified()
    self.upperPad.Update()


  #-------------------------#
  def _draw_legends(self):
  #-------------------------#
    logger.debug('Begin drawing legends console')
    self.lpad.cd()

    ## Adjust legends
    self.l.SetBorderSize(1)
    self.l.SetColumnSeparation(0)
    self.l.SetEntrySeparation(0)
    self.l.SetName('legend')
    self.l.SetTextSize(13)
    self.l.SetTextFont(103)
    # self.l.SetTextAlign(32) #
    self.l.SetX1(0.)
    self.l.SetY1(0.)
    self.l.SetX2(1.)
    self.l.SetY2(1.)
    self.l.Draw()

  #------------------------------------
  def _draw_debug_console(self):
  #------------------------------------

    # Cut into smaller chunks if it's too long 
    # For the trees, params, cuts, filters
    ## DISABLE: Conflict with auto/manual expansion
    # for i,x in enumerate(self.trees):
    #   pt.AddText("Tree[%i]  : %s" % (i,x.GetTitle()))
    # for i,x in enumerate(self.params):
    #   pt.AddText("Params[%i]: %s" % (i,x))
    # if not (len(self.cuts)==1 and self.cuts[0] == ""):
    #   for i,x in enumerate(self.cuts):
    #     pt.AddText("Cuts[%i]  : %s" % (i,x))

    logger.debug('Begin drawing debug console')
    self.dpad.cd()

    ## Create an instance
    pt = self.console = ROOT.TPaveText(0., 0., 1., 1., "NDC")
    pt.SetBorderSize(1)
    pt.SetFillColor(0)
    pt.SetTextSize(12)
    pt.SetTextFont(103)
    pt.SetTextAlign(12)
    pt.SetMargin(0.01)

    ## Flush msg, and determine dynamic height
    all_msg   = list(self.gen_debug_msg())
    lenfield  = max(len(x[0]) for x in all_msg)  # Dynamic field length
    template  = '{:<'+str(lenfield)+'}: {}'
    for field,msg in all_msg:
      pt.AddText(template.format(field, msg))

    ## Finally
    pt.Draw()

  #-----------------------------------------------------------------------------

  def save(self):
    """
    Save the contents that this QHist instance is holding into PDF and ROOT file.
    
    This method is actually public, and aims to allow the user to keep editing 
    on the canvas for a little more, ( for example, adding text, polyline, etc.) 
    and calling `save` when they are done.
    """
    fpath = self.fullpath_safe
    logger.debug('fullpath_safe: '+fpath)

    # Save the full debug canvas
    self.c.SaveAs(fpath)

    ## Save to ROOT file (using script name), delete existing first
    fname = os.path.join(self.output_path, self.filename+".root")
    fout  = ROOT.TFile( fname, 'UPDATE' )
    # fout.Delete(self.c.name+";*")  # Delete keys & cycles
    # fout.Delete(self.c.name) # Delete object
    # self.c.Write()
    self.c.Write('', ROOT.TObject.kOverwrite)
    fout.Close()


  #-----------------------------------------------------------------------------
  def _finalize(self):
    """Misc things."""

    ## Redirect the pointer to null-pad. Necessary for multiple drawing.
    # Required because the next drawing will call _loop_first_pass, 
    # which in turn calls TTree::Draw to calculate stats.
    self.nullPad = ROOT.TPad("nullPad", "nullPad", 0.1, 0.1, 0.2, 0.2 )
    self.nullPad.cd()


  #-------------------------------------
  def draw(self, **kwargs):
    """Main method to do the drawing."""
  #-------------------------------------

    postpc = kwargs.pop('postpc') if 'postpc' in kwargs else None

    ## Compact form: final say from kwargs
    for key, val in kwargs.iteritems():
      setattr(self, key, val)

    ## retrieve existing value
    _batch = ROOT.gROOT.IsBatch()
    if self.batch is not None: # some explicit value
      ROOT.gROOT.SetBatch(bool(self.batch))

    logger.debug('Init draw()')
    try:
      if self.expansion:
        self._initial_validation_manual_exp()
      else:
        self._initial_validation_auto_exp()
      self._validate()
      self._loop_first_pass()
      self._summary_loop_first_pass()
      self._prepare_drawing_base()
      # if self.is_complex_normalize and self.dim==1:
      #   self._loop_complex_normalize()      
      self._report_stats()
      if self.dim==1:
        wrapper = wrappers.TH1F()
      elif self.dim==2:
        if self.is_prof:
          wrapper = wrappers.TProfile()
        else:
          wrapper = wrappers.TH2F()
      elif self.dim==3 and self.is_prof:
        wrapper = wrappers.TProfile2D()
      else:
        raise NotImplementedError
      self._draw_wrapped(wrapper)        
      self._draw_legends()
      self._draw_debug_console()

      ## postprocessor
      if postpc:
        postpc(self)

      self.c.Update()  ## Final pre-save TCanvas update
      if 'temp_' not in self.name:  # Save only when I have some name, not having temp.
        self.save()
      self._finalize()  
      return self.c
    except Exception as e:
      logger.exception(e)
      logger.error('Failed to draw: '+ str(self.name))

    ## restore original value
    ROOT.gROOT.SetBatch(_batch)


  # #---------------------------------------
  # def update(self):
  #   """Poke inner TCanvas to update, by looping over stored self.htemp. EXPERIMENTAL!"""
  #   for h in self: h.Draw("sames")
  #   self.upperPad.Modified()
  #   self.upperPad.Update()  # Need Modified+Update to work!
  #   self.save()

  # #---------------------------------------


#==============================================================================
