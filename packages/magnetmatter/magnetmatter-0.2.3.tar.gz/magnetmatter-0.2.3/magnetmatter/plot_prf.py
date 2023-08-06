# plot_prf.py

import os, numpy as np, pandas as pd, sys, re, math
import matplotlib.pyplot as plt

""" importing private modules """
from auxiliary import cm2inch
from wrappers import TraceCalls
from find_tools import findfile, findfiles, findfolders_abspath
from prf_plot_tools import extract_out_file, calculate_size, excluded_regions
from prf_plot_tools import prepare_refinement_result, get_spacegroups
from read_prf import read_prf
from extract_pcr import getwavelength
from myObject import AbstractPrf
from make_video import Video


def plot_prf(path = "", printsize = "two_in_docx", video = False, xlim = (2.8,3.6), dpi = 250):
  # plot_prf_enhanced(path=path, printsize=printsize, minmax2theta = minmax2theta)
  # plot_prf_plain(path=path, printsize=printsize, minmax2theta = minmax2theta)
  plain = PlainPrf(printsize = printsize, path = path, verbose = False, dpi = dpi)
  enhanced = EnhancedPrf(printsize = printsize, path = path, verbose = True, dpi = dpi)


  enhanced( xlim = xlim )
  plain( xlim = None )
  xlimrange = True
  if video:
    xlim = (0.0,16.0)
    range1 = [round(x,1) for x in np.arange(*xlim,0.1)]
    range2 = [round(x+0.4,1) for x in np.arange(*xlim,0.1)]
    print("")
    mymax = max(range2)
    mymin = max(range1)
    for low, high in zip(range1, range2):
      # import pdb; pdb.set_trace();
      sys.stdout.write("\rplotting q-range = ({},{})  ... continues to ({},{})         ".format(low,high,mymin,mymax))
      plain( xlim = (low, high))
    print("")
    Video(plain.outfolder)
  else:
    plain( xlim = xlim )



class PlainPrf(AbstractPrf):
  def __init__(self, printsize = "two_in_docx", path = "", verbose = False, dpi = 100):
    super().__init__(path = path, verbose = verbose, dpi = dpi)
    if printsize == "two_in_docx":
      self.graph_width = 8.45 # cm
      self.graph_height = self.graph_width*3/4 # cm
      self.medium_text = 8 # still quite big
      self.smaller_text = 6 # better
      self.micro_text = 4 # 4 good for refinement info.
      self.dotsize = 1 #
      self.linewidth = 0.7
      self.ylabelpos_pre = (0.01,1.05)
      self.ylabelpos_post = (-0.058,0.50)
      self.xlabelpos_pre = (1.05,0.15)
      self.xlabelpos_post = (0.50,-0.10)
      self.ticklabelpadding = 3
      self.yticklabel_placeholder = "10000"
    elif printsize == "one_in_docx":
      self.graph_width = 17 # cm
      self.graph_height = self.graph_width*3/4 # cm
      self.medium_text = 12 # still quite big
      self.smaller_text = 10 # better
      self.micro_text = 8 # 4 good for refinement info.
      self.dotsize = 2
      self.linewidth = 2
      self.ylabelpos_pre = (-0.007,1.05)
      self.ylabelpos_post = (-0.07,0.50)
      self.xlabelpos_pre = (1.05,-0.043)
      self.xlabelpos_post = (0.50,-0.07)
      self.ticklabelpadding = 5
      self.yticklabel_placeholder = "100"
    elif printsize == "one_in_ppt":
      self.graph_width = 32 # cm
      self.graph_height = self.graph_width*2/5 # cm
      self.medium_text = 18 # still quite big
      self.smaller_text = 16 # better
      self.micro_text = 10 # 4 good for refinement info.
      self.dotsize = 3
      self.linewidth = 2
      self.ylabelpos_pre = (-0.009,1.07)
      self.ylabelpos_post = (-0.045,0.55)
      self.xlabelpos_pre = (1.05,-0.063)
      self.xlabelpos_post = (0.50,-0.10)
      self.ticklabelpadding = 9
      self.yticklabel_placeholder = "1000000"
    elif printsize == "one_in_ppt":
      self.graph_width = 32 # cm
      self.graph_height = self.graph_width*2/5 # cm
      self.medium_text = 18 # still quite big
      self.smaller_text = 16 # better
      self.micro_text = 10 # 4 good for refinement info.
      self.dotsize = 3
      self.linewidth = 2
      self.ylabelpos_pre = (-0.009,1.07)
      self.ylabelpos_post = (-0.045,0.55)
      self.xlabelpos_pre = (1.05,-0.063)
      self.xlabelpos_post = (0.50,-0.10)
      self.ticklabelpadding = 9
      self.yticklabel_placeholder = "1000000"



    plt.style.use("seaborn-white")

  def update_outpath(self):
    self.suffix = "_plain"
    self.outfolder = os.path.join(self.basepath, self.suffix)
    if not os.path.exists(self.outfolder): os.makedirs(self.outfolder)
    out = os.path.join(self.outfolder, os.path.basename(self.basefolder))
    if self.xlim != None:
      xlim = tuple(str(round(x,1)) for x in self.xlim)
      self.suffix += xlim[0]+"to"+xlim[1]+".png"
    else:
      out = os.path.join(self.basepath, os.path.basename(self.basefolder))
      self.suffix += ".png"
    self.figname = out + self.suffix

  def update_legends(self):
    super(PlainPrf, self).update_legends()
    self.legend.set_visible(False)

# @TraceCalls()
  def __call__(self, xlim = ""):
      """
      ?searches all folders for given path for .prf, .out, .pcr files to plot with refined informations?

      ?Args?:
          path: script will be executed at this path
          printsize: options are "two_in_docx", two_in_ppt", "one_in_docx", "one_in_ppt".
          minmax2theta: tuple of min and max 2theta values to be ignored

      ?Compatibility?:
          Script has been tested with refined data from DMC, HRPT (SINQ:PSI)
          and refined data from X-ray sources.
          The FullProf .pcr format is the new format (_not_ classical).

      ?Side effect?:
          Saves plots of "Yobs", "Ycal" and "Ycal-Yobs" for .prf, .out and .pcr files
          found in child folderns. The script is verbose and will tell what it is currently
          doing, if the process was successful and what mistakes occured.

      ?Common mistake?:
          If you change your .pcr, remember to run FullProf to see the effect of the updated
          parameters or added phases. This script stupidly reads in the .out and .prf files.
          Any changes to especially phase names will certainly result in unchanged phase names found
          in plot.
          Therefore always run the .pcr file to update the FullProf output files.
      """

      self.xlim = xlim

      for self.basefolder in self.basefolders:

        # if not os.path.exists(self.basefolder): continue # not sure if this is necessary

        if 0 != self.update(): continue

        # """ shortening the view of the diffractogram
        #   if user has provided a tuple of min-max values """
        # if type(xlim) == type(tuple()) and len(xlim) == 2:
        #   self.df = self.df[self.df["2Theta"] > minmax2theta[0]]
        #   self.df = self.df[self.df["2Theta"] < minmax2theta[1]]


        """ plotting Yobs, Ycal, and Yobs-Ycal data. """
        if self.baseplotting() == -1: continue
        """ above should be continue... if diffraction data from different sources are used. """

        self.update_legends()

        self.update_title()

        self.add_bragg_peaks()


        self.update_xylabels_tightlauoyt()

        self.update_xyticks()

        if self.xlim != None:
          self.baseax.set_xlim( *self.xlim )
        else:
          self.baseax.set_xlim( self.df["q-space"].min(), self.df["q-space"].max() )


        """ THIS DOESN'T work. ups capslock... """
        plt.tick_params(
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom='on',      # ticks along the bottom edge are off
        top='off',         # ticks along the top edge are off
        # labelbottom='off'
        ) # labels along the bottom edge are off


        # self.update_grid()
        # if type(xlim) == type(tuple()): self.update_xylim( xlim )



        self.update_outpath()

        self.savefigure()










class EnhancedPrf(AbstractPrf):
  def __init__(self, printsize = "two_in_docx", path = "", verbose = False, dpi = 100):
    super().__init__(path = path, verbose = verbose, dpi = dpi)
    if printsize == "two_in_docx":
      self.graph_width = 8.45 # cm
      self.graph_height = self.graph_width*3/4 # cm
      self.medium_text = 8 # still quite big
      self.smaller_text = 6 # better
      self.micro_text = 4 # 4 good for refinement info.
      self.refsize_text = 5
      self.dotsize = 1 #
      self.linewidth = 0.7
      self.subplot_right_space = 8.1#6.8
      self.refinfo_pos_long_text = (1.02,-0.2)#(1.02,-0.07)
      self.refinfo_pos_short_text = (1.02,-0.07)
      self.ylabelpos_pre = (0.01,1.05)
      self.ylabelpos_post = (-0.11,0.50)
      self.xlabelpos_pre = (1.05,0.15)
      self.xlabelpos_post = (0.50,-0.09)
      self.ticklabelpadding = 3
      self.yticklabel_placeholder = "1000"
    if printsize == "two_in_ppt":
      self.graph_width = 15 # cm
      self.graph_height = self.graph_width*3/4 # cm
      self.medium_text = 12 # still quite big
      self.smaller_text = 10 # better
      self.micro_text = 8 # 4 good for refinement info.
      self.refsize_text = 8
      self.dotsize = 2
      self.linewidth = 2
      self.subplot_right_space = 7.7
      self.refinfo_pos_long_text = (1.03,-0.14)
      self.refinfo_pos_short_text = (1.03,-0.06)
      self.ylabelpos_pre = (-0.008,1.05)
      self.ylabelpos_post = (-0.10,0.50)
      self.xlabelpos_pre = (1.05,-0.043)
      self.xlabelpos_post = (0.50,-0.08)
      self.ticklabelpadding = 6
      self.yticklabel_placeholder = "100"
    elif printsize == "one_in_docx":
      self.graph_width = 17 # cm
      self.graph_height = self.graph_width*3/4 # cm
      self.medium_text = 12 # still quite big
      self.smaller_text = 10 # better
      self.micro_text = 8 # 4 good for refinement info.
      self.refsize_text = 8
      self.dotsize = 2
      self.linewidth = 2
      self.subplot_right_space = 6.8
      self.refinfo_pos_long_text = (1.015,-0.13)
      self.refinfo_pos_short_text = (1.015,-0.055)
      self.ylabelpos_pre = (-0.007,1.05)
      self.ylabelpos_post = (-0.07,0.50)
      self.xlabelpos_pre = (1.05,-0.043)
      self.xlabelpos_post = (0.50,-0.07)
      self.ticklabelpadding = 5
      self.yticklabel_placeholder = "100"
    elif printsize == "one_in_ppt":
      self.graph_width = 32 # cm
      self.graph_height = self.graph_width*2/5 # cm
      self.medium_text = 18 # still quite big
      self.smaller_text = 16 # better
      self.micro_text = 10 # 4 good for refinement info.
      self.refsize_text = 10
      self.dotsize = 3
      self.linewidth = 2
      self.subplot_right_space = 4.6
      self.refinfo_pos_long_text = (1.01,-0.2)
      self.refinfo_pos_short_text = (1.01,-0.075)
      self.ylabelpos_pre = (-0.009,1.07)
      self.ylabelpos_post = (-0.045,0.55)
      self.xlabelpos_pre = (1.05,-0.063)
      self.xlabelpos_post = (0.50,-0.10)
      self.ticklabelpadding = 9
      self.yticklabel_placeholder = "1000000"

    plt.style.use("seaborn-white")

  def update_outpath(self):
    out = os.path.join(self.basepath, os.path.basename(self.basefolder) )
    suffix = ""
    if self.xlim != None:
      xlim = tuple(str(round(x,1)) for x in self.xlim)
      suffix += xlim[0]+"to"+xlim[1]
    self.figname = out + ".png"

  def plotting_info_text(self):
    plt.subplots_adjust(right=self.subplot_right_space)
    """ extraction of:
    phase names (dict)
    phase fractions (dict)
    wavelength (float)
    refined parameter value and error (dict) """
    self.wavelength, self.frac_info, self.phases, self.refined_par = extract_out_file()
    """ can we split this method up or something else? """

    """ calculates:
    ab and c-sizes (dict of dicts) """
    self.size_info = calculate_size(
        wavelength = self.wavelength,
        phases = self.phases,
        refined_par = self.refined_par,
        )

    """ extracting spacegroups from PCR file """
    self.spacegroups = get_spacegroups()

    """ preparing information such as refined parameters, phases, phase fractions
    crystallite sizes and so to be printed on canvas. """
    self.combined_text = prepare_refinement_result(
        phases = self.phases,
        refined_par = self.refined_par,
        size_info = self.size_info,
        frac_info = self.frac_info,
        spacegroups = self.spacegroups,
        wavelength = self.wavelength,
        )

    """ if not long refinement info text, aling text with bottom of graph """
    self.refinfo_pos = self.refinfo_pos_short_text if self.combined_text.count("\n") < 24 else self.refinfo_pos_long_text

    """ plotting refinement info on canvas"""
    ttt = self.baseax.text(
        self.refinfo_pos[0],
        self.refinfo_pos[1],
        self.combined_text,
        size=self.refsize_text,
        fontname = "monospace",
        picker=True,
        transform = self.baseax.transAxes,
        # zorder = 0,
        )

    """ making the refinement info have a semitransparent white background """
    # ttt.set_bbox(dict(facecolor='white', alpha=0.5, edgecolor='white'))



  # @TraceCalls()
  def __call__(self,xlim = ""):
      """
      searches all folders for given path for .prf, .out, .pcr files to plot with refined informations

      Args:
          path: script will be executed at this path
          printsize: options are "two_in_docx", two_in_ppt", "one_in_docx", "one_in_ppt".
          minmax2theta: tuple of min and max 2theta values to be ignored

      Compatibility:
          Script has been tested with refined data from DMC, HRPT (SINQ:PSI)
          and refined data from X-ray sources.
          The FullProf .pcr format is the new format (_not_ classical).

      Side effect:
          Saves plots of "Yobs", "Ycal" and "Ycal-Yobs" for .prf, .out and .pcr files
          found in child folderns. The script is verbose and will tell what it is currently
          doing, if the process was successful and what mistakes occured.

      Common mistake:
          If you change your .pcr, remember to run FullProf to see the effect of the updated
          parameters or added phases. This script stupidly reads in the .out and .prf files.
          Any changes to especially phase names will certainly result in unchanged phase names found
          in plot.
          Therefore always run the .pcr file to update the FullProf output files.

      """

      # printsize = "two_in_ppt" # graphs are 17 cm wide, perfect for two in .ppt
      # printsize = "one_in_docx" # graphs are 17 cm wide, perfect for one in word
      # printsize = "one_in_ppt" # single grpah in .ppt
      # printsize = "two_in_docx" # graphs are 8 cm wide, perfect for two in word

      self.xlim = xlim

      for self.basefolder in self.basefolders:

          if 0 != self.update(): continue

          # """ below code is obsolete """
          # if not df[df["2Theta"] > 30.00].empty:
          #   """ if-check is necessary when treating synchrotron data,
          #   where angles are less than 20 degrees! """
          #   # df = df[df["2Theta"] > 20.00]
          #   # df = df[df["2Theta"] < 92.900]

          # """ shortening the view of the diffractogram
          # if user has provided a tuple of min-max values """
          # if type(minmax2theta) == type(tuple()) and len(minmax2theta) == 2:
          #   df = df[df["2Theta"] > minmax2theta[0]]
          #   df = df[df["2Theta"] < minmax2theta[1]]

          if self.baseplotting() == -1: continue

          self.plotting_info_text()

          self.update_legends()

          self.update_title()

          self.add_bragg_peaks()

          self.update_xylabels_tightlauoyt()

          # """ reducing empty space in data plot """
          # min_y = min(self.baseax.get_yaxis().major.locator.locs)
          # max_y = max(self.baseax.get_yaxis().major.locator.locs)
          # plt.ylim(min_y,max_y)

          # if type(xlim) == type(tuple()): self.update_xylim( xlim )

          self.update_xyticks()

          if self.xlim != None:
            self.baseax.set_xlim( *self.xlim )


          self.update_grid()

          self.update_outpath()

          self.savefigure()

      # """ normalizing the path """
      # os.chdir(path)









# print("\n\nEND_OF_SCRIPT")
# print(sys.version_info)
# print(sys.executable)
