#!/usr/bin/env python

import ROOT
from array import array

## Const
LHCb_FONT = 132
LHCb_SIZE = 0.06
LHCb_FONT_FIXED = 133
LHCb_SIZE_FIXED = 20

def set_lhcb_style_lite():
  """
  Apply part of the LHCb style, if not already defined.

  >> set_lhcb_style_lite()

  """
  if ROOT.gStyle.name == 'lhcbStyle': # on top of LHCb style, fine tune
    pass
  else: 
    ROOT.gStyle.SetTitleSize( 1.2*LHCb_SIZE, 'x' )
    ROOT.gStyle.SetTitleSize( 1.2*LHCb_SIZE, 'y' )
    ROOT.gStyle.SetLabelSize( LHCb_SIZE    , 'x' )
    ROOT.gStyle.SetLabelSize( LHCb_SIZE    , 'y' )
    ROOT.gStyle.SetTitleFont( LHCb_FONT    , 'x' )
    ROOT.gStyle.SetTitleFont( LHCb_FONT    , 'y' )
    ROOT.gStyle.SetLabelFont( LHCb_FONT    , 'x' )
    ROOT.gStyle.SetLabelFont( LHCb_FONT    , 'y' )
    ROOT.gStyle.padTickX = 1 # tick on another side
    ROOT.gStyle.padTickY = 1

def set_qhist_color_palette():  
  # black, red, blue, ...
  palette = array('i', [1, 2, 4, 28, 6, ROOT.kGreen+3, ROOT.kAzure+7])
  ROOT.gStyle.SetPalette(len(palette), palette)

#===============================================================================

#--------------------#
# Default QHistStyle #
#--------------------#

# # st = GenericQHistStyle('QHist', 'QHistStyle')
# st = ROOT.TStyle('QHist', 'QHistStyle')
# st.ownership = False

# ## Whitening all
# st.SetPadBorderMode(0)
# st.SetPadColor(0)
# st.SetCanvasBorderMode(0)
# st.SetCanvasColor(0)
# st.SetFrameBorderMode(0)
# st.SetFrameFillColor(0)
# st.SetTitleFillColor(0)

# ## Margins
# st.SetPadTopMargin(0.07)
# st.SetPadLeftMargin(0.07) # for ylabel
# st.SetPadRightMargin(0.04)
# st.SetPadBottomMargin(0.08)

# ## Colors
# st.SetPalette(ROOT.kBird)

# ## Fonts
# st.SetTitleFont( LHCb_FONT, 'title' )

# ## Histo
# st.HistLineWidth = int(LHCb_WIDTH)

# # Disable stats box
# st.OptStat = 0

# st.cd()