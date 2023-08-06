#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Further implementation of QHistV3, providing the stateful instance methods 
that finally lead to the drawing of specified parameters.

Drawing Lifecycle
-----------------

0. Attribute assignment to QHist instance, before calling `h.draw()`.
   The assertion inside setters performs a check.

1. VALIDATE: With all fields prepared, perform the validation based on the overall inputs.

2. PREPARE: instantiate all ROOT.TObject need for the drawing, attach them onto
   the anchors.

3. SCAN-STATS: take all entries and calculate the statistical info need before 
   draw, such as min/max/entries.

4. DRAW-COMPONENTS: loop over each entries, draw each of them into separate 
   histogram individually.

5. MAKESTACK: take the histograms and stack them together according to style_code.

6. LEGEND: deduce the legend entries and draw them.

7. POST-PROCESSING: perform user-defined post-processing on the histogram.

8. FINALIZE: save the output pdf/root files into target destination.


>>> getfixture('freeze_time')
>>> print(QHist())  # doctest: +ELLIPSIS
-------------------...
        KEY       |   VALUE  ( * differs from default )
anchors           | * -------------------...
                  |           KEY       |   VALUE  ( * differs from default )
                  |   canvas            |   None
                  |   debug             |   None
                  |   debugpad          |   None
                  |   legend            |   None
                  |   legendpad         |   None
                  |   mainpad           |   None
                  |   stack             |   None
                  |   ----------------------------------------------------...
auto_name         |   None
batch             |   None
comment           |   ''
cuts              |   []
debug_messages    | * <generator object debug_messages at ...
dim               |   0
filename          |   py...
filters           |   []
guessname         |   None
has_name          |   False
height_debug_conso|   60
height_legend_cons|   15
is_advance_stack  |   False
is_profile        |   False
is_simple_stack   |   False
legends           |   None
name              |   temp_20200101_000000000000
normalize         |   ()
option            |   ''
params            |   []
postproc          |   None
prefix            |   None
st_code           |   None
st_color          |   None
st_fill           |   None
st_line           |   None
st_marker         |   None
stats             |   <Stats> len=0 nbin=None X=[None, None]
suffix            |   None
timestamp         |   20200101_000000000000
title             |   temp_20200101_000000000000
tpc               |   []
trees             |   []
wrapper           |   EXCEPTION
xarr              |   None
xbin              |   None
xlabel            |   ''
xlog              |   None
xmax              |   None
xmin              |   None
yarr              |   None
ybin              |   None
ylabel            |   ''
ylog              |   None
ymax              |   None
ymin              |   None
zbin              |   None
zlabel            |   ''
zlog              |   None
zmax              |   None
zmin              |   None
--------------------------------------------------------------------------------
<BLANKLINE>

"""

import os
import ROOT
from .. import logger, utils
from .stats import Stats
from PythonCK.decorators import report_debug

from .core import QHist as QHist0
from . import __doc__ as doc

#===============================================================================

class QHist(QHist0):

  __slots__ = QHist0.__slots__  # no change
  __doc__ = doc   # take from module init

  def __init__(self, *args, **kwargs):
    """
    Simply pass to the underlying class.
    """
    super(QHist, self).__init__(*args, **kwargs)

#===============================================================================

  # @report_debug
  def _prepare(self):
    """
    Lifecycle step that instantiate ROOT's TObjects needed for drawing.

    ## Test anchor is read-only

    """
    # ## CANVAS & PAD
    # ## increase from current style for the extra consoles
    # width   = ROOT.gStyle.CanvasDefW
    # height  = ROOT.gStyle.CanvasDefH
    # hlegend = self.height_legend_console
    # hdebug  = self.height_debug_console
    # height += hlegend + hdebug
    # y1 = 1. / height *  hdebug 
    # y2 = 1. / height * (hdebug+hlegend)

    # ## Make sure the name is unique
    # self.anchors.canvas    = ROOT.TCanvas( self.name+'_canvas'   , self.title, width, height )
    # self.anchors.debugpad  = ROOT.TPad   ( self.name+'_debugpad' , 'debugpad'  , .01 , .01 , .99 , y1 )
    # self.anchors.legendpad = ROOT.TPad   ( self.name+'_legendpad', 'legendpad' , .01 , y1 , .99 , y2 )
    # self.anchors.mainpad   = ROOT.TPad   ( self.name+'_mainpad'  , 'mainpad'   , .005, y2, .995, .995  )
    # self.anchors.stack     = ROOT.THStack( self.name+'_stack'    , self.title )

    ## Simple
    width  = ROOT.gStyle.CanvasDefW
    height = ROOT.gStyle.CanvasDefH

    ## Make sure the name is unique
    self.anchors.canvas  = ROOT.TCanvas(self.name+'_canvas' , self.title, width, height)
    self.anchors.mainpad = ROOT.TPad   (self.name+'_mainpad', 'mainpad' , .005, .005, .995, .995)
    self.anchors.stack   = ROOT.THStack(self.name+'_stack'  , self.title)

    ## Some default to style code if not provided.
    # Note: this is applied to all wrapper type... may be too non-sense.
    if not self.st_code:
      ## simple no-stacking comparison
      if self.st_line   is None: self.st_line   = True
      if self.st_color  is None: self.st_color  = True
      if self.st_fill   is None: self.st_fill   = False
      if self.st_marker is None: self.st_marker = False

    ## Depends on the style code, override the subflags
    if self.st_code == 2:
      if self.st_color is None:
        self.st_color = True

#===============================================================================

  @report_debug 
  def _scan_stats(self):
    """
    Lifecycle step that scan the stats & coverage of given inputs.

    ## Test with some data
    >>> h = QHist(tpc=tpc)
    >>> h._validate()
    True
    >>> h._scan_stats()
    <Stats> len=2 nbin=20 X=[0.0005247, 1.804]

    ## It prefers explicit value from user, even after _scan_stats.
    >>> h = QHist(xmin=11, xmax=22, xbin=33, ymin=44, ymax=55, ybin=66, zbin=77)
    >>> h._stats = getfixture('stats')  # mimick finished scan.
    >>> h.xmin, h.xmax, h.xbin, h.ymin, h.ymax, h.ybin, h.zbin
    (11.0, 22.0, 33, 44.0, 55.0, 66, 77)


    TODO: Mock Stats.xlog
    >> h = QHist(tpc=tpc)
    >> h._scan()
    >> 

    ## TODO
    # ## After scan stats, the debug info should contain correct binning choice.
    # >>> h._scan_stats()
    # >>> print tabulate.tabulate(h.debug_messages)
    # ---------  ------------------------------------------------------
    # Filters    (pi_BPVIP<0.1) | (mu_BPVIP<0.1)
    # Tree       DitauCandTupleWriter/h1_mu (['res/ditau.root']) [#303]
    # Param[0]   mu_PT: DPHI
    # Axis       X=[ 1.0, 100.0 ]/Auto=20, Y=[ 0.0, 3.14 ]/20
    # Timestamp  20200101_000000000000
    # Script     /mainfile
    # ---------  ------------------------------------------------------


    """
    self._stats = Stats.from_list_TPC(self._tpc_fullcuts) 
    logger.debug(self.stats)
    return self._stats

#===============================================================================

  @report_debug
  def _draw_components(self):
    """
    Lifecycle step that loop draw the cloned histograms into collection.
    """
    for i,(t,p,c) in enumerate(self._tpc_fullcuts):
      ## Make a new clone of empty histogram of appropriate type
      h = self.wrapper.clone()
      self._histos.append(h)

      ## Apply styling & get option
      opt_tree, opt_leg = self.wrapper.apply_style(h,i)
      logger.debug('opt_tree: %s'%opt_tree)
      logger.debug('opt_leg : %s'%opt_leg)

      ## CORE METHOD: Make projection from TTree to histogram
      opt = self.option + opt_tree
      ROOT.TTree.Project(t, h.name, p, c, opt)

      ## Attach metadata
      h.option  = opt # carry forward
      h.title   = self.legends[i]
      h.contour = self.zbin  # 2D only
      if not self.is_profile:
        h.normalize(self.normalize[i])

#===============================================================================

  @report_debug
  def _makestack(self):
    """
    Lifecycle step that uses collected histo and Draw them on Canvas. 
    Different post-processing style (stacking, MC-vs-Data, ratio-plot) specified 
    will be handled here.
    """
    self.anchors.mainpad.cd()
    stk = self.anchors.stack

    ## CODE==2: Stacked except first (e.g., data vs. bkg-sum)
    if self.st_code == 2:
      for i,h in enumerate(self):
        if i>0:
          stk.Add(h, h.option)
      stk.Draw()
      h0 = self[0]
      h0.Draw(h0.option)
      ## fine-tune ymax
      ymax = self.ymax
      if ymax is None:
        y1 = stk.maximum
        y2 = h0.maximum
        if y2 > 1: y2 += y2**0.5  # with Poisson err, if unnormalized
        ymax = max([y1, y2])
      stk.maximum = ymax

    ## Both CODE==0, CODE==1
    else:
      ## 0. Default, no stack
      for h in self:
        stk.Add(h, h.option)
      stk.Draw('nostack'+self.option)

      ## fine-tune ymin/ymax is explicitly given
      if self.ymin is not None:
        stk.minimum = self.ymin
      if self.ymax is not None:
        stk.maximum = self.ymax

    ## Final label
    h = stk.histogram
    h.XTitle = self.xlabel
    h.YTitle = self.ylabel

    ## Adjust the log scale
    if self.xlog:
      self.anchors.mainpad.logx = True
      utils.auto_morelog(stk.xaxis)
    if self.ylog:
      self.anchors.mainpad.logy = True
      utils.auto_morelog(stk.yaxis)
    if self.zlog:
      self.anchors.mainpad.logz = True

#===============================================================================

  def _draw_legend_simple(self):
    ## Skip drawing for n=1
    if len(self.tpc)==1:
      logger.debug('Single entry, skip drawing legend.')
      return

    ## Simple draw
    leg = self.anchors.legend = self.anchors.mainpad.BuildLegend()
    leg.ConvertNDCtoPad()
    leg.fillStyle = 0
    leg.Draw()
    ## Reorder for CODE==2
    if self.st_code==2:
      leg.primitives.AddAt(leg.primitives[-1], 0)
      leg.primitives.RemoveLast() # just pop out, don't delete as the above also disappear

#===============================================================================

  # @report_debug
  # def _draw_legend_advance(self):
  #   ## Init
  #   self.anchors.legendpad.cd()
  #   l = self.anchors.legend = ROOT.TLegend(0., 0., 1., 1., '', 'NDC')  # Whatever 

  #   ## Prepare the legends header
  #   header = self.wrapper.legend_header
  #   l.NColumns = len(header)
  #   for val in header:
  #     l.AddEntry('', val, '')  # Last flag is to disable markers
  #   ## Supply manual legend, extra touch on first col.
  #   for i,h in enumerate(self):
  #     for j,val in enumerate(self.wrapper.legend_entry( h, i )):
  #       l.AddEntry( h, str(val), '' if j else 'lpf' )

  #   ## Styling
  #   l.BorderSize       = 1
  #   l.ColumnSeparation = 0
  #   l.EntrySeparation  = 0
  #   l.Name      = 'legend'
  #   l.TextSize  = 13
  #   l.TextFont  = 103
  #   l.X1  = 0.
  #   l.Y1  = 0.
  #   l.X2  = 1.
  #   l.Y2  = 1.
  #   l.Draw()

#===============================================================================

  # def _draw_debug(self):
  #   self.anchors.debugpad.cd()

  #   ## Create an instance
  #   pt = self.anchors.debug = ROOT.TPaveText(0., 0., 1., 1., 'NDC')
  #   pt.BorderSize = 1
  #   pt.FillColor  = 0
  #   pt.TextSize   = 12
  #   pt.TextFont   = 103
  #   pt.TextAlign  = 12
  #   pt.Margin     = 0.01

  #   ## Flush msg, and determine dynamic height
  #   all_msg   = list(self.debug_messages)
  #   lenfield  = max(len(x) for x,_ in all_msg)  # Dynamic field length
  #   template  = '{:<'+str(lenfield)+'}: {}'
  #   for field,msg in all_msg:
  #     pt.AddText(template.format(field, msg))

#===============================================================================

  @report_debug
  def _finalize(self):
    ## Redirect the pointer to null-pad. Necessary for multiple drawing.
    # Required because the next drawing will call _loop_first_pass, 
    # which in turn calls TTree::Draw to calculate stats.
    # p = ROOT.TPad("nullPad", "nullPad", .1, .1, .2, .2 ).Draw().cd()
    ## TODO: Should be responsibility of Stats

    ## Saving protocol
    if not self.name.startswith('temp_'):
      ## Make output path
      if not os.path.exists(self.filename): # Use filename as outputpath
        os.makedirs(self.filename) 
        logger.debug('Created output_path: ' + self.filename)
      ## Save PDF
      fname = utils.safename(self.name + ".pdf")
      fpath = os.path.join(self.filename, fname)
      self.anchors.canvas.SaveAs(fpath)
      ## Save ROOT
      fpath = os.path.join(self.filename, self.filename+".root")
      fout  = ROOT.TFile( fpath, 'UPDATE' )
      cname = self.anchors.canvas.name
      fout.Delete(cname+";*")  # Delete keys & cycles
      fout.Delete(cname) # Delete object
      self.anchors.canvas.Write()
      fout.Close()

#===============================================================================

  # @report_debug
  def draw(self):

    ## retrieve existing value
    _batch = ROOT.gROOT.IsBatch()
    if self.batch is not None: # some explicit value
      ROOT.gROOT.SetBatch(bool(self.batch))

    try:
      self._validate()
      logger.debug(self)
      self._prepare()
      self._scan_stats()
      self._draw_components()
      self._makestack()

      ## disable for now
      # self._draw_legend_advance()
      # self._draw_debug()
      # self.anchors.update()
      self._draw_legend_simple()

      ## Post-processing and finalize
      if self.postproc is not None:
        self.postproc(self)
      self._finalize()

    ## Catch any exception and log as error.
    except Exception as e:
      logger.exception(e)
      logger.error('Failed to draw: %s'%self.name)
      raise e

    ## restore original value
    ROOT.gROOT.SetBatch(_batch)

#===============================================================================
