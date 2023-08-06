#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..functools import static_struct

## These are grouped in the same way as README
ProtoQHist = static_struct('ProtoQHist', 

  ## CORE REQUIRED FIELDS
  trees   = '[TTree] ROOT::TTree instance(s) to perform Drawing',
  params  = '[str] String represent TBranch name to plot. For 2D, use X:Y convention (opposite to ROOT)',
  tpc     = '[...] Manually provide the list of TPC triplet.',

  ## COMPUTATION
  cuts      = '[str] List of, or one string for drawing cuts',
  filters   = '[str] List of, or one string, for cuts to be applied throughout its lifecycle.', # Concept from Gaudi's DaVinci
  normalize = """
    [bool/float/callable] Specify the normalization scheme. 
    
    - True  : All plots will be normalized to 1.
    - False : No normalization. All histograms retain their counts.
    - float : Each histogram will be normalize to float given. 
    If list is given, the size of list MUST corresponds to TPC size.
    - callable: accept one float arg (current hist integral), return new integral.
  """, 
  option   = '(str) Additional option flag to add to TTree::Draw.',
  postproc = '(callable) Optional post-processing, before saving.',

  ## AXIS CONTROL 
  xmin    = '(float) Adjust min value of X-axis.',
  xmax    = '(float) Adjust max value of X-axis.',
  xbin    = '(int)   Adjust number of bins of X-axis',
  xlog    = '(bool)  Use log-scale on X-axis or not.',
  xlabel  = '(str)   String label for X-axis',
  ymin    = '(float) Adjust min value of Y-axis.',
  ymax    = '(float) Adjust max value of Y-axis.',
  ybin    = '(int)   Adjust number of bins of Y-axis',
  ylog    = '(bool)  Use log-scale on Y-axis or not.',
  ylabel  = '(str)   String label for Y-axis',
  zmin    = '(float) Adjust min value of Z-axis.',
  zmax    = '(float) Adjust max value of Z-axis.',
  zbin    = '(int)   Adjust number of bins of Z-axis (i.e., contours in 2D plot)',
  zlog    = '(bool)  Use log-scale on Z-axis or not (i.e., contours in 2D plot).',
  zlabel  = '(str)   String label for Z-axis',

  ## NAMING & OUTPUTS
  name    = '(str)  Name of the output file.',
  title   = '(str)  Optional title of histogram, taken from `name` if null.',
  prefix  = '(str)  Prefix to consistently prepend to the name/title.',
  suffix  = '(str)  Suffix to consistently append to the name/title.',
  comment = '(...)  Arbitary comment to write on canvas note.',
  batch   = '(bool) True to wrap with gROOT.SetBatch, False is explicitly intr, None is to leave to existing value.',
  auto_name = """
    (bool) If True, QHist will try to guess the name by itself. 
    Consequently, the guessed name will be used for saving PDF result.
  """,

  ### COSMETICS + STYLE (experimental)
  legends   = '[str] List of strings to be used as legends. Must have same dim as TPC',
  st_code   = '(int) Style-code',
  st_color  = '(bool) use color',
  st_line   = '(bool) use different line style',
  st_marker = '(bool) use marker',
  st_fill   = '(bool) use filling',
)
