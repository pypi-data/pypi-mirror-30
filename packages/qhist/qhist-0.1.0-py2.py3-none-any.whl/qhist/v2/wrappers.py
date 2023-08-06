#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import functools
import ROOT
from abc import ABCMeta, abstractmethod, abstractproperty
from .. import logger, utils


def set_ownership_false(func):
  @functools.wraps(func)
  def wrap(*args, **kwargs):
    obj = func(*args, **kwargs)
    ROOT.SetOwnership(obj, False)
    return obj
  return wrap

#===============================================================================

class QHistWrapper:
  __metaclass__ = ABCMeta

  @abstractmethod
  def new(_, hist, name, title):
    raise NotImplementedError

  @abstractproperty
  def legend_header(_):
    raise NotImplementedError

  @abstractmethod
  def style(_, qhist, h, index):
    """
    Customize the style of TTree depends on style_code & index j. 
    return opt_tree, opt_legend to be used in one TTree::Draw instance.
    """
    raise NotImplementedError

  @abstractmethod
  def precycle_process(wrapper, qhist):
    raise NotImplementedError

  @abstractmethod
  def midcycle_legend_entry(_, qhist, h, index):
    raise NotImplementedError

  @abstractmethod
  def midcycle_postprocess(wrapper, qhist, h, index):
    raise NotImplementedError

  @abstractmethod
  def endcycle_preprocess(_, qhist, h):
    raise NotImplementedError


#===============================================================================

class Styler(object):
  @staticmethod
  def style(wrapper, qhist, h, index):
    # pass
    ## Disabled 151023 in favor of lhcbStyle.C 
    if qhist.st_line: 
      h.lineStyle = utils.LINES(index)

    if qhist.st_marker: 
      h.markerStyle = utils.MARKERS(index)
    else: # explicitly null
      h.markerStyle = 0
      h.markerSize  = 0

    if qhist.st_color:
      c = utils.COLORS(index)
      h.markerColor = c
      h.lineColor = c
      if qhist.st_fill:
        h.fillColor = c

    if qhist.st_fill:
      h.fillStyle = utils.FILLS(index)

#======================================================================

class CommonTH1(object):
  """Utils, for now, common behavior between TH1F, TProfile."""

  @staticmethod
  def precycle_process(wrapper, qhist):
    # Collector for ymin/ymax axis
    wrapper.collect_ymin  = []
    wrapper.collect_ymax  = []

  @staticmethod
  def midcycle_postprocess(wrapper, qhist, h, index):
    # Collect yaxis-info. This is UNAFFECTED by axis range (min/max). 
    # These will be important for Mother Histogram later on.
    # Note: This is only possible after 1st-pass, where _xmin,_xmax are known
    wrapper.collect_ymin.append(h.GetMinimum())
    wrapper.collect_ymax.append(h.GetMaximum())  # Can only this after normalization

    ## Transfer the subhisto title
    h.SetTitle(qhist.legends[index])

  @staticmethod
  def endcycle_preprocess(wrapper, qhist, hfin):
    # Effectice _ymin, _ymax is now obtainable after all plot is known
    qhist._ybin = None  # not used, but instantiated here.
    qhist._ymin = utils.prefer_first(qhist.ymin, min(wrapper.collect_ymin)*1.0)
    qhist._ymax = utils.prefer_first(qhist.ymax, max(wrapper.collect_ymax)*1.1)
    # Correct _ymin==0 if y-axis is log scale
    if qhist.ylog and qhist._ymin==0: 
      logger.debug("Auto correct ymin=0 in ylog scale to 1E-3.")
      qhist._ymin=1E-3
    # Enforce again
    ROOT.gPad.SetLogy(int(qhist.ylog))
    hfin.SetMinimum(qhist._ymin)
    hfin.SetMaximum(qhist._ymax)
    # Finally, report
    logger.debug("1D _ymin: " + str(qhist._ymin))
    logger.debug("1D _ymax: " + str(qhist._ymax))


#======================================================================

class TH1F(QHistWrapper):

  @set_ownership_false
  def new(_, hist, name, title):
    arr = hist._xarr
    h   = ROOT.TH1F(name, title, len(arr)-1, arr)
    h.SetTitle(title)
    h.SetXTitle(hist.xlabel)
    h.SetYTitle(hist.ylabel)
    ## If log-range < 1E4, show more label
    if hist.xlog:
      utils.auto_morelog(h.GetXaxis())
    return h

  @property 
  def legend_header(_):
    return ('LHCb preliminary', 'Entries', 'Integral', 'Min', 'Max', 'Mean', 'RMS') # 'Count (input)',

  def style(wrapper, qhist, h, index):
    # return ('', '') ## For migration to LHCb-style

    # STYLE#01: Data is 1st entry, showed as marker. The rest is MC, show as lines
    if qhist.st_code==1:
      if index==0:
        h.SetMarkerStyle(ROOT.kFullDotMedium)
        # return ("p", "p")
        return ("E1", "p")
      else:
        h.SetLineColor(utils.COLORS(index))
        h.SetLineStyle(index)
        return ("H", "l")

    ## STYLE#02: 1st entry is marker. The rest are stacked & filled
    elif qhist.st_code == 2:
      if index==0:
        h.SetMarkerStyle(ROOT.kFullDotMedium)
        return ("E1", "p")

      else:
        c = utils.COLORS(index)
        h.SetLineColor(c)
        h.SetFillColor(c)
        h.SetFillStyle(utils.FILLS(index))
        return ("Hist", "l")

    else:
      # STANDARD style
      if qhist.stack:  # If stack, shift all index by one (let the main is the stack-sum)
        index += 1
      Styler.style(wrapper, qhist, h, index)
      return ("p", "p") if qhist.st_marker else ("H", "l")
      ## p0 to show empty bin

  #--------------------------------------------

  def precycle_process(wrapper, qhist):
    CommonTH1.precycle_process(wrapper, qhist)

  def midcycle_legend_entry(_, qhist, hc, index):
    # nmz       = qhist.normalize[index]
    intg      = hc.Integral()
    nentries  = int(hc.entries)
    yield qhist.legends[index]
    yield nentries
    yield utils.pretty_round(intg)
    yield utils.pretty_round(qhist._stats[index][1]) if hasattr(qhist,'_stats') else '---'  ## TODO: unsafe _stats
    yield utils.pretty_round(qhist._stats[index][2]) if hasattr(qhist,'_stats') else '---'
    yield utils.pretty_round(hc.mean) if nentries else '     ---'
    yield utils.pretty_round(hc.RMS)  if nentries else '     ---'

  def midcycle_postprocess(wrapper, qhist, hc, index):
    ## Normalize the histogram
    nmz   = qhist.normalize[index]
    intg  = hc.Integral()
    if intg==0:
      scale = 1.
    elif callable(nmz):
      scale = 1./intg*nmz(hc.entries)
    elif nmz is True:
      scale = 1. / intg
    elif nmz is False:
      scale = 1.0
    else:  # user's value
      scale = float(nmz) / intg
    logger.debug("Integral   : %.2f" % intg)

    ## Proper treatment of error
    # need to guard against warning, in case of dirty tree (e.g., lepton misid)
    if not hc.sumw2N:
      hc.Sumw2()
    hc.Scale(scale)

    ## After scaling
    CommonTH1.midcycle_postprocess(wrapper, qhist, hc, index)

  def endcycle_preprocess(wrapper, *args):
    CommonTH1.endcycle_preprocess(wrapper, *args)

#==============================================================================

class TProfile(QHistWrapper):

  @set_ownership_false
  def new(wrapper, qhist, name, title):
    arr = qhist._xarr
    h   = ROOT.TProfile(name, title, len(arr)-1, arr)
    h.SetTitle(title)
    h.SetXTitle(qhist.xlabel)
    h.SetYTitle(qhist.ylabel)
    h.GetXaxis().SetMoreLogLabels(True)
    return h

  @property
  def legend_header(_):
    return ('LHCb preliminary', 'Entries', 'Y-mean')

  def style(wrapper, qhist, h, index):
    Styler.style(wrapper, qhist, h, index)

    # STYLE#01: Data is 1st entry, showed as BAND. The rest is MC, show as lines
    if qhist.st_code==1:
      if index==0:  
        h.SetFillColor(1)
        h.SetFillStyle(3001)
        return 'E3','l'
      else:
        return 'ep0','p'
    else:
      return ('ep0', 'p') if qhist.st_marker else ('', 'l')

  def precycle_process(wrapper, qhist):
    CommonTH1.precycle_process(wrapper, qhist)
    # qhist.upperPad.SetLeftMargin(0.08)  # To have space for ylabel ## Disable, leave to Style.

  def midcycle_legend_entry(_, self, hc, index):
    from array import array
    arr = array('d', range(6))
    hc.GetStats(arr)
    # print arr
    ymean = arr[4]/arr[0]
    # yrms  = (arr[5]/arr[1])**0.5

    yield self.legends[index]
    yield int(hc.entries)
    yield utils.pretty_round(ymean)
    # yield utils.pretty_round(yrms)

  def midcycle_postprocess(wrapper, qhist, hc, index):
    CommonTH1.midcycle_postprocess(wrapper, qhist, hc, index)

  def endcycle_preprocess(wrapper, qhist, hfin):
    hfin.xaxis.SetTitleOffset( 1.1 ) ## Space of text label and h 
    hfin.yaxis.SetTitleOffset( 0.9 ) ## Space of text label and h 
    hfin.SetLabelOffset( 0., 'X' ) ## This is space between numeric value and h
    CommonTH1.endcycle_preprocess(wrapper, qhist, hfin)


#==============================================================================

class TH2F(QHistWrapper):

  @set_ownership_false
  def new(wrapper, qhist, name, title):
    xarr = qhist._xarr
    yarr = wrapper.yarr
    h    = ROOT.TH2F(name, title, len(xarr)-1, xarr, len(yarr)-1, yarr)
    h.title   = title
    h.XTitle  = qhist.xlabel
    h.YTitle  = qhist.ylabel
    if qhist.xlog:
      utils.auto_morelog(h.xaxis)
    return h

  @property  
  def legend_header(_):
    return ('LHCb preliminary', 'count', 'x-mean', 'x-RMS', 'y-mean', 'y-RMS' )

  def style(wrapper, qhist, h, index):
    Styler.style(wrapper, qhist, h, index)
    return ('','')

  def precycle_process(wrapper, qhist):
    # Manual Y-axis
    wrapper.yarr = utils.make_bins(qhist._ymin, qhist._ymax, qhist._ybin, qhist.ylog)
    # To have space for ylabel  ## No need, leave it to lhcbStyle
    qhist.upperPad.SetRightMargin(0.12)  # For z-axis gradient

  def midcycle_legend_entry(wrapper, qhist, hc, index):
    yield qhist.legends[index]
    yield int(hc.GetEntries())
    yield utils.pretty_round(hc.GetMean(1))
    yield utils.pretty_round(hc.GetRMS(1))
    yield utils.pretty_round(hc.GetMean(2))
    yield utils.pretty_round(hc.GetRMS(2))

  def midcycle_postprocess(wrapper, qhist, h, index):
    h.contour = qhist.zbin  # Change number of coutour. It works only here
    h.title   = qhist.legends[index] ## Transfer the subhisto title

  def endcycle_preprocess(wrapper, qhist, hfin):
    hfin.yaxis.titleOffset = 0.7  ## Space of text label and h 
    hfin.SetLabelOffset( 0., 'X' ) ## This is space between numeric value and h


class TProfile2D(QHistWrapper):

  @set_ownership_false
  def new(wrapper, qhist, name, title):
    xarr = qhist._xarr
    yarr = wrapper.yarr
    h    = ROOT.TProfile2D(name, title, len(xarr)-1, xarr, len(yarr)-1, yarr)
    h.title   = title
    h.XTitle  = qhist.xlabel
    h.YTitle  = qhist.ylabel
    if qhist.xlog:
      utils.auto_morelog(h.xaxis)
    if qhist.ylog:
      utils.auto_morelog(h.yaxis)
    return h

  @property  
  def legend_header(_):
    return ('LHCb preliminary', 'count', 'x-mean', 'x-RMS', 'y-mean', 'y-RMS' )

  def style(wrapper, qhist, h, index):
    Styler.style(wrapper, qhist, h, index)
    return ('','')

  def precycle_process(wrapper, qhist):
    # Manual Y-axis
    wrapper.yarr = utils.make_bins(qhist._ymin, qhist._ymax, qhist._ybin, qhist.ylog)

  def midcycle_legend_entry(wrapper, qhist, hc, index):
    yield qhist.legends[index]
    yield int(hc.GetEntries())
    yield utils.pretty_round(hc.GetMean(1))
    yield utils.pretty_round(hc.GetRMS(1))
    yield utils.pretty_round(hc.GetMean(2))
    yield utils.pretty_round(hc.GetRMS(2))

  def midcycle_postprocess(wrapper, qhist, h, index):
    h.title   = qhist.legends[index] ## Transfer the subhisto title

  def endcycle_preprocess(wrapper, qhist, hfin):
    hfin.yaxis.titleOffset = 0.7  ## Space of text label and h 
    hfin.SetLabelOffset( 0., 'X' ) ## This is space between numeric value and h
