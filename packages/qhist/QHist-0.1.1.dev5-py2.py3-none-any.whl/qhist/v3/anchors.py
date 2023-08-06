#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ROOT
from ..functools import static_struct

__all__ = ('Anchors',)

## Define the possible anchors
ProtoAnchors = static_struct('ProtoAnchors', 
  canvas    = 'DOC',
  stack     = 'DOC',
  mainpad   = 'DOC',
  legend    = 'DOC',
  legendpad = 'DOC',
  debug     = 'DOC',
  debugpad  = 'DOC',
)

class Anchors(ProtoAnchors):
  """
  This helper class with take ownership the attached TObject.

  Usage::

      ## Init & attach
      >>> a = Anchors()
      >>> a.canvas = ROOT.TCanvas('name', 'title')

  """

  def __setattr__(self, key, obj):
    """
    Two possibilities:

    If obj is False/None, this will explicitly disable this anchor and thus the
    respective object will not be shown.

    If it's ROOT.TObject, then bind it normally.

    """
    assert isinstance(obj, ROOT.TObject)
    if not key.startswith('_staticprop_'):
      ## Keep alive
      ROOT.SetOwnership(obj, False)
      ## Pad needs to be drawn not, and everything else doesn't.
      if isinstance(obj, ROOT.TPad):
        obj.Draw()
    return super(Anchors, self).__setattr__(key,obj)

  def update(self):
    """
    Recursively call `Update` of all its contents.
  
    >>> a = Anchors()
    >>> a.canvas  = ROOT.TCanvas('c2', 'title')
    >>> a.legend  = ROOT.TLegend()
    >>> a.mainpad = ROOT.TPad('pad', 'pad', 0, 0, 1, 1)
    >>> a.update()

    """
    ## Drill down on existing pads.
    for key in self.keys():
      if key != 'canvas':
        val = getattr(self, key)
        if val and isinstance(val, ROOT.TPad):
          val.Modified()
          val.Update()
    ## Usually needed
    self.mainpad.RedrawAxis()
    ## last object
    if self.canvas:
      self.canvas.Modified()
      self.canvas.Update()

  def save(self, *args):
    """
    Delegation from canvas.SaveAs
    """
    self.update()
    return self.canvas.SaveAs(*args)

  # def __str__(self):
  #   ## Print list of objects in self
  #   msg = ""
  #   tmp = '{:10} {}\n'.format
  #   msg += tmp('NAME', 'INSTANCE')
  #   for name in dir(self):
  #     if not name.startswith('_'):
  #       obj = getattr(self, name)
  #       if not hasattr(obj, 'im_self'):
  #         msg += tmp(name, obj)
  #   return msg
