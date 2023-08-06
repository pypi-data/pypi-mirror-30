
import os, pandas as pd, sys, math, re
import matplotlib.pyplot as plt

""" importing private modules """
from find_tools import findfile, findfolders_abspath
from read_prf import read_prf
from extract_pcr import getwavelength, getphases
from auxiliary import cm2inch, natural_keys
from read_bragg_reflections_from_out import BraggContainer
import numpy as np





class AbstractPrf():
  """ we will collect the many lose variables...

  this is designed to be a abstract class. I have not yet figured out the benefits
  of using the abc module to do this. for now I use built-in inheritate for PlainPrf and EnhancedPrf. """
  def __init__(self, path = "", dpi = 100, verbose = False):

    self.dpi = dpi
    """ path bookkeeping """
    self.basepath = path if path != "" else os.getcwd()
    os.chdir(self.basepath)
    self.verbose = verbose
    self.basefolders = findfolders_abspath()
    if self.verbose:
      for f in self.basefolders: print("found folder {}".format(f))
      print("")
      """ TODO:
      read in all data and metadata to keep (save reading in files over and over).
      Through away folders in basefolders that cannot be plotted. """
    # self.basefolders = iter( self.basefolders ) # no longer needed.

  def update(self):

    # verbose = verbose if verbose != "" else self.verbose

    if self.verbose: print("\nworking on", self.basefolder)

    os.chdir(self.basefolder)

    def helper_findfile(extension):
      myfile = findfile(extension)
      if not os.path.exists(myfile):
        if self.verbose: print("!-!-!-! skipping \"" + self.basefolder + "\" + --> no " + extension + " was found");
        return -1
      if extension == ".prf":
        self.baseprf = myfile;
      if extension == ".pcr":
        self.basepcr = myfile;
      if extension == ".out":
        self.baseout = myfile;
      return 0

    if helper_findfile(".prf") == -1: return -1
    if helper_findfile(".pcr") == -1: return -1
    if helper_findfile(".out") == -1: return -1

    """ reading DMC/HRPT or Xray/Dioptas prf file """
    (prf_type, self.df) = read_prf(self.baseprf)
    if self.verbose: print("found {}-prf.".format(prf_type))
    should_I_break = [x for x in ["dmc", "xray"] if x == prf_type]
    if len(should_I_break) == 0:
      return -1

    """ check if model data are actual values! otherwise skip datafolder """
    if self.df.empty:
      if self.verbose: sys.stdout.write("!-!-!-! skipping folder \"" + self.basefolder + "\". DataFrame is empty (values in prf might be NaNs)\n");
      return -1

    self.wavelength = getwavelength(self.basepcr)
    self.df["Yobs-Ycal"] = self.df["Yobs"]-self.df["Ycal"]
    """ formular for converting from 2Theta to Q-space:
    |q| = (4 * pi) / wavelength * sin(2Theta[radians] / 2)
    source: https://www.staff.tugraz.at/manfred.kriechbaum/xitami/java/qtheta.html """
    self.df["q-space"] = math.pi * 4 / self.wavelength * ( (math.pi / 180 / 2 * self.df["2Theta"]).apply(math.sin) )

    return 0

  def baseplotting(self):
    plt.close("all")
    self.basefig, self.baseax = plt.subplots(figsize = cm2inch(self.graph_width, self.graph_height) )

    if self.xlim != None:
      df = self.df[self.df["q-space"] > self.xlim[0]]
      df = df[df["q-space"] < self.xlim[1]]
    else:
      df = self.df

    if df.empty: return -1

    y = "Yobs"
    self.baseax = df.plot(
      "q-space",
      y,
      kind="scatter",
      s = self.dotsize,
      ax = self.baseax,
      fontsize = self.smaller_text,  # xtick and ytick labels
      label = y, # for legend
      c = "r",
      alpha=0.5,
      )
    df.plot(
      "q-space",
      "Ycal",
      linewidth = self.linewidth,
      ax = self.baseax,
      alpha=0.8,
      )
    df.plot(
      "q-space",
      "Yobs-Ycal",
      linewidth = self.linewidth,
      ax = self.baseax,
      alpha=0.3,
      )

    return 0

  def update_legends(self):
    """ changing the position of the legends to make Yobs appear at the top """
    handles,labels = self.baseax.get_legend_handles_labels()
    handles = [handles[2], handles[0], handles[1]]
    labels = [labels[2], labels[0], labels[1]]

    """ setting legend to best position """
    self.legend = plt.legend(handles,labels, loc="best", prop = {"size": self.micro_text})

  def update_xylabels_tightlauoyt(self):
    """ setting dummy y- and xlabel names. These are changed later
    self is done due to the effect of using plt.tight_layout()
    in combination with rotation and shifting of the text object"""
    ylabel = plt.ylabel("Counts", size = self.smaller_text)
    plt.xlabel(r"2$\theta$", size = self.smaller_text)

    """ repositioning and rotation the ylabel """
    self.baseax.yaxis.set_label_coords(*self.ylabelpos_pre)
    ylabel.set_rotation(0)

    """ Xlabel must be here otherwise plt.tight_layout is not given the
    additional white space for the ref_info text """
    self.baseax.xaxis.set_label_coords(*self.xlabelpos_pre)

    """ set all yticks to 100 to tweak the right space for final ytick labels """
    self.myyticks = self.baseax.get_yticks()
    self.mynewyticks = [self.yticklabel_placeholder for x in self.myyticks]
    plt.yticks(self.myyticks, self.mynewyticks)

    """ ensure nothing is left outside the plot
    many elements are moved the following code to optimize the space """
    plt.tight_layout()
    """ everything from here is tweaking already existing plt objects! """

    """ setting padding of x and y tick labels """
    self.baseax.tick_params(pad=self.ticklabelpadding)

    """ repositioning and renaming xlabel and ylabel
    _after_ the use of plt.tight_layout()"""
    ylabel.set_rotation(90)
    self.baseax.yaxis.set_label_coords(*self.ylabelpos_post)
    self.baseax.xaxis.set_label_coords(*self.xlabelpos_post)
    # plt.xlabel(r"scattering angle 2$\theta$ [$^o$]", size = smaller_text)
    plt.xlabel(r"4$\pi$/$\lambda\cdot$sin($\theta$) = Q [$\AA^{-1}$]", size = self.smaller_text)
    ylabel = plt.ylabel("signal count [a.u.]", size = self.smaller_text)

  def update_title(self):
    def _label_text(mystring):
      """ returns a latexified string to be used in plt.
      e.g. 500oC --> 500$^o$C """
      return re.sub("(\d)oC","\g<1>°C",mystring)
    self.basetitle = _label_text(os.path.basename(self.basefolder))
    plt.title(self.basetitle, size = self.medium_text)

  def update_xylim(self, xlim):
    """ making the diffraction data as wide as possible """
    # xmin = min(self.df["q-space"])
    # xmax = max(self.df["q-space"])
    # self.df = self.df[self.df["Yobs"] > 2.8]
    # self.df = self.df[self.df["Yobs"] < 3.6]

    """ this is not really necessary with plt.xlim?? """
    df = self.df[self.df["q-space"] > xlim[0]]
    df = df[df["q-space"] < xlim[1]]
    ylim = (df[["Yobs","Ycal","Yobs-Ycal"]].min().min(), df[["Yobs","Ycal","Yobs-Ycal"]].max().max())
    self.baseax.set_ylim( *ylim )
    self.baseax.set_xlim( *xlim )
    """ this is not really necessary with plt.xlim?? """


    # ymin = min([min(self.df["Yobs"]), min(self.df["Ycal"])])
    # ymax = max([max(self.df["Yobs"]), max(self.df["Ycal"])])
    # # plt.xlim(1,3.5)
    # """ reducing empty space in data plot """
    # min_y = min(self.baseax.get_yaxis().major.locator.locs)
    # max_y = max(self.baseax.get_yaxis().major.locator.locs)
    # plt.ylim(min_y,max_y)
    # plt.ylim(ymin,ymax)
    # plt.xlim(2.8,3.6)


  def update_xyticks(self):
    """ showing only first and last ytick label """
    self.mynewyticks = ["" for x in self.myyticks]
    self.mynewyticks[-1] = "{:.1e}".format(self.myyticks[-1])
    self.mynewyticks[0] = "{:.1e}".format(self.myyticks[0])
    plt.yticks(self.myyticks, self.mynewyticks)

    myxticks = self.baseax.get_xticks()
    mynewxticks = []
    for x in myxticks:
      mynewxticks.append(round(x,1))
    mynewxticks[-1] = ""
    mynewxticks[0] = ""
    plt.xticks(myxticks, mynewxticks)

  def update_grid(self):
    self.baseax.grid()


  def savefigure(self):
    """ saving the figure in high resolution """
    """ path and name of output file """

    plt.savefig(self.figname, dpi=self.dpi, format = "png")

    """ avoid memory leak """
    plt.close()

  def add_bragg_peaks(self):
    bc = BraggContainer(self.baseout, self.wavelength).dfs

    df2 = self.df
    if self.xlim != None:
      df2 = df2[df2["q-space"] > self.xlim[0]]
      df2 = df2[df2["q-space"] < self.xlim[1]]
      if df2.empty: return -1

    mininum = min( self.baseax.get_ylim() )
    maximum = df2["Yobs"].min()

    myrange = iter(np.linspace(0, mininum, 10)+maximum)
    next(myrange)
    phases = getphases(self.basepcr)
    for phase in sorted( phases , key = natural_keys):
      minmax = (next(myrange), next(myrange))
      df = bc[phase]

      if self.xlim != None:
        df = df[df["q-space"] > self.xlim[0]]
        df = df[df["q-space"] < self.xlim[1]]

      if df.empty: continue

      # reflections = df["2theta"].unique()
      reflections = df["q-space"].unique()
      for refl in reflections:
        # print(phase, refl, *minmax)
        self.baseax.plot([refl, refl],[*minmax],"--r", linewidth = 0.5, alpha = 1, zorder=1)







  def add_bragg_peaks_obsolete_remove_soon(self):
    """ uPDaTe:
    we might be able to extract bragg peaks
    from the FP .outfile
    """

    """ inserting bragg peak positions.

    NOTE: the 2theta values can be found in the .out file!!!!!!!!!

    No.  Code     H   K   L  Mult     Hw         2theta      Icalc       Iobs      Sigma      HwG     HwL       ETA       d-hkl        CORR

    NOTE: implementation is not correct! see discussion below
    """
    type_of_diffraction_data = ""
    if type_of_diffraction_data == "more complicated than as such to implement":
      import bragg_peak_indications as bpi

      mycs = bpi.Crystals().crystals
      mypositions = [0.02, 0.04]
      mycolours = ["r","b","g"]*2
      for myc in mycs:
        mycolour = mycolours.pop(0)
        myc = myc.unique
        mymax = max(df["2Theta"])
        mymin = min(df["2Theta"])
        myc = myc[myc > mymin]
        myc = myc[myc < mymax]
        for val in myc:

          setmin = mypositions[0] * (abs(min_y) + max_y) + min_y
          setmax = mypositions[1] * (abs(min_y) + max_y) + min_y
          plt.plot([val,val],[setmin, setmax], c = mycolour, lw = 0.5)
        mypositions = [0.03 + mypos for mypos in mypositions]
    """
    above code is not correct - magnetic structures are inherently complicated
    and even for x-ray diffraction patterns the zero shift (if not more...) has to be taken into account.
    Also I tried to color coordinate the phasename with the reflections, but changing color in a block of
    text by means of LaTeX-based code has proven to be non-trivial.
    """
