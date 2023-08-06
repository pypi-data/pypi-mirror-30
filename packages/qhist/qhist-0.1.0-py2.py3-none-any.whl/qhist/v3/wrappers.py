#!/usr/bin/env python
"""

Helper wrapper to handle the customized TObject template to be drawn.

"""

import ROOT
from abc import ABCMeta, abstractmethod
from .. import utils

__all__ = ()

#===============================================================================

def apply_generic_style(qhist, h, index):
  """
  Translate the styling instruction from qhist to apply to given histogram h,
  at the given index.
  """
  ## If COLOR explicitly True/False
  if qhist.st_color is True:
    c = utils.COLORS(index)
    h.markerColor = c
    h.fillColor   = c
    h.lineColor   = c

  ## If FILL explicitly True/False
  if qhist.st_fill is True:
    h.fillStyle = utils.FILLS(index)
  if qhist.st_fill is False:
    h.fillStyle = 0
    h.fillColor = 0 # implicit

  ## If MARKER explicitly True/False
  if qhist.st_marker is True:
    h.markerStyle = utils.MARKERS(index)
  if qhist.st_marker is False:
    h.markerSize = 0

  ## If LINE explicitly True/False
  if qhist.st_line is True:
    h.lineStyle = utils.LINES(index)
  if qhist.st_line is False:
    h.lineStyle = 1 # plain line

#===============================================================================

def Wrapper(qhist):
  """
  Prepare the template instance to be cloned.
  Most of the time, there's no need to worry about style here,
  since it'll not be carried forward to be used in 3rd-pass anyway.  
  """
  dim  = qhist.dim
  prof = qhist.is_profile
  if dim==1:
    return TH1F(qhist)
  elif dim==2:
    if prof:
      return TProfile(qhist)
    else:
      return TH2F(qhist)
  elif dim==3 and prof:
    return TProfile2D(qhist)
  else:
    raise ValueError('Failed to determine the wrapper to be used.')

#===============================================================================

class QHistWrapper(object):
  """
  Abstract base class for making different histograms from same interface.
  """
  __metaclass__ = ABCMeta

  def __init__(self, qhist):
    self.qhist     = qhist # pointer to instructed QHist
    self.counter   = 0     # clone counter
    self._template = self.template()  # Lazy

  def clone(self):
    """Handle cloning, unique naming, ownership, in one go."""
    self.counter += 1
    name = '%s_hc_%02i' % (self.qhist.name, self.counter)
    hc   = self._template.Clone(name)
    hc.ownership = False
    return hc

  @abstractmethod
  def template(_):  # pragma: no cover
    """
    Implement this method to return a new instance of histogram.
    """
    raise NotImplementedError

  @abstractmethod
  def apply_style(wrapper, h, index):  # pragma: no cover
    raise NotImplementedError

  # @abstractproperty
  # def legend_header(_):
  #   raise NotImplementedError

  # @abstractmethod
  # def legend_entry(_, h, index):
  #   raise NotImplementedError

#===============================================================================

class TH1F(QHistWrapper):

  def template(self):
    qh = self.qhist
    return ROOT.TH1F(qh.name+'_wrapper', qh.title, qh.xbin, qh.xarr)

  def apply_style(wrapper, h, index):
    # STYLE#01: Data is 1st entry, showed as marker. The rest is MC, show as lines
    # e.g., Zmumu normalization plot
    code = wrapper.qhist.st_code
    if code==1:
      if index==0:
        # points
        h.markerStyle = ROOT.kFullDotMedium
        return ("E1", "p")
      else:
        # histogram
        h.lineColor  = utils.COLORS(index)
        h.lineStyle  = index
        h.markerSize = 0
        return ("H", "l")

    ## STYLE#02: 1st entry is marker. The rest are stacked & filled.
    elif code==2:
      if index==0:
        h.markerStyle = 20  # LHCb
        h.markerSize  = 1.2
        return ("E1 sames", "p")
      else:
        c = utils.COLORS(index) # skip first color (black)
        h.lineColor = c
        h.fillColor = c
        h.fillStyle = utils.FILLS(index)
        h.markerSize = 0.
        return ("Hist", "l")

    elif code == 0 or code is None:
      # STANDARD style
      if wrapper.qhist.anchors.stack:  # If stack, shift all index by one (let the main is the stack-sum)
        index += 1
      apply_generic_style(wrapper.qhist, h, index)
      return ("p", "p") if wrapper.qhist.st_marker else ("H", "l")
      ## p0 to show empty bin

    else:  # pragma: no cover
      raise NotImplementedError

  # @property 
  # def legend_header(_):
  #   return ('LHCb-Preliminary', 'Entries', 'Integral', 'Min', 'Max', 'Mean', 'RMS')

  # def legend_entry(self, hc, index):
  #   qh = self.qhist
  #   nentries = int(hc.GetEntries())

  #   yield qh.legends[index]
  #   yield nentries
  #   yield utils.pretty_round(float(hc.Integral()))
  #   yield utils.pretty_round(qh.stats[index].xmin)
  #   yield utils.pretty_round(qh.stats[index].xmax)
  #   yield utils.pretty_round(hc.GetMean()) if nentries else '---'
  #   yield utils.pretty_round(hc.GetRMS())  if nentries else '---'

#==============================================================================

class TProfile(QHistWrapper):

  def template(self):
    qh = self.qhist
    return ROOT.TProfile(qh.name+'_wrapper', qh.title, qh.xbin, qh.xarr)

  def apply_style(self, h, index):
    apply_generic_style(self.qhist, h, index)
    return ('ep0', 'p') if self.qhist.st_marker else ('', 'l')

  # @property
  # def legend_header(_):
  #   return ('LHCb-preliminary', 'Entries', 'Y-mean')

  # def legend_entry(self, hc, index):
  #   qh = self.qhist
  #   from array import array
  #   arr = array('d', range(6))
  #   hc.GetStats(arr)
  #   # print arr
  #   ymean = arr[4]/arr[0] if arr[0]!=0 else '9999'
  #   # yrms  = (arr[5]/arr[1])**0.5

  #   yield qh.legends[index]
  #   yield int(hc.GetEntries())
  #   yield utils.pretty_round(ymean)
  #   # yield utils.pretty_round(yrms)

#==============================================================================

class TH2F(QHistWrapper):

  def template(self):
    qh = self.qhist
    return ROOT.TH2F(qh.name+'_wrapper', qh.title, qh.xbin, qh.xarr, qh.ybin, qh.yarr)

  def apply_style(wrapper, h, index):
    apply_generic_style(wrapper.qhist, h, index)
    h.lineStyle = 1
    # h.fillStyle = 10
    return ('','')

  # @property  
  # def legend_header(_):
  #   return ('LHCb-preliminary', 'count', 'x-mean', 'x-RMS', 'y-mean', 'y-RMS' )

  # def legend_entry(self, hc, index):
  #   yield self.qhist.legends[index]
  #   yield int(hc.GetEntries())
  #   yield utils.pretty_round(hc.GetMean(1))
  #   yield utils.pretty_round(hc.GetRMS(1))
  #   yield utils.pretty_round(hc.GetMean(2))
  #   yield utils.pretty_round(hc.GetRMS(2))

#==============================================================================

class TProfile2D(QHistWrapper):

  def template(self):
    qh = self.qhist
    return ROOT.TProfile2D(qh.name+'_wrapper', qh.title, qh.xbin, qh.xarr, qh.ybin, qh.yarr)

#==============================================================================
