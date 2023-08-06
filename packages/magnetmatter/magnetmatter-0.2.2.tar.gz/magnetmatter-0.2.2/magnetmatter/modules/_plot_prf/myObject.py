
import os, pandas as pd, sys, math
import matplotlib.pyplot as plt

""" importing private modules """
from find_tools import findfile, findfolders_abspath
from read_prf import read_prf
from extract_pcr import getwavelength
from auxiliary import cm2inch



class AbstractPrf():
  """ we will collect the many lose variables...

  this is designed to be a abstract class. I have not yet figured out the benefits
  of using the abc module to do this. for now I use inheritate for PlanPrf and EnhancedPrf. """
  def __init__(self, path = os.getcwd(), verbose = False):

    """ path bookkeeping """
    self.basepath = path
    os.chdir(self.basepath)
    self.verbose = verbose
    self.basefolders = findfolders_abspath()
    if self.verbose:
      for f in self.basefolders: print("found folder {}".format(f))
      print("")
    # self.basefolders = iter( self.basefolders ) # no longer needed.

  def update(self, verbose = ""):

    verbose = verbose if verbose != "" else self.verbose

    if verbose: print("\nworking on", self.basefolder)

    os.chdir(self.basefolder)

    self.baseprf = findfile(".prf");
    if not os.path.exists(self.baseprf):
      if verbose: print("!-!-!-! skipping \"" + self.basefolder + "\" + --> no .prf was found");
      return -1

    self.basepcr = findfile(".pcr");
    if not os.path.exists(self.basepcr):
      if verbose: print("!-!-!-! skipping \"" + self.basefolder + "\" + --> no .pcr was found");
      return -1

    self.baseout = findfile(".out");
    if not os.path.exists(self.baseout):
      if verbose: print("!-!-!-! skipping \"" + self.basefolder + "\" + --> no .out was found");
      return -1

    """ reading DMC/HRPT or Xray/Dioptas prf file """
    (prf_type, self.df) = read_prf(self.baseprf)
    if verbose: print("found {}-prf.".format(prf_type))

    """ check if model data are actual values! otherwise skip datafolder """
    if self.df.empty:
      if verbose: sys.stdout.write("!-!-!-! skipping folder \"" + self.basefolder + "\". DataFrame is empty (values in prf might be NaNs)\n");
      return -1

    self.wavelength = getwavelength(self.basepcr)
    self.df["Yobs-Ycal"] = self.df["Yobs"]-self.df["Ycal"]
    """ formular for converting from 2Theta to Q-space:
    |q| = (4 * pi) / wavelength * sin(2Theta[radians] / 2)
    source: https://www.staff.tugraz.at/manfred.kriechbaum/xitami/java/qtheta.html """
    self.df["q-space"] = math.pi * 4 / self.wavelength * ( (math.pi / 180 / 2 * self.df["2Theta"]).apply(math.sin) )

    return 0

  def baseplotting(self):
    self.basefig, self.baseax = plt.subplots(figsize = cm2inch(self.graph_width, self.graph_height) )

    y = "Yobs"
    self.baseax = self.df.plot(
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
    self.df.plot(
      "q-space",
      "Ycal",
      linewidth = self.linewidth,
      ax = self.baseax,
      alpha=0.8,
      )
    self.df.plot(
      "q-space",
      "Yobs-Ycal",
      linewidth = self.linewidth,
      ax = self.baseax,
      alpha=0.3,
      )

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
    self.basetitle = os.path.basename(self.basefolder)
    plt.title(self.basetitle, size = self.medium_text)


  def update_xyticks(self):
    """ showing only first and last ytick label """
    self.mynewyticks = ["" for x in self.myyticks]
    self.mynewyticks[-1] = "{:.1e}".format(self.myyticks[-1])
    self.mynewyticks[0] = "{:.1e}".format(self.myyticks[0])
    plt.yticks(self.myyticks, self.mynewyticks)

    myxticks = self.baseax.get_xticks()
    mynewxticks = [x for x in myxticks]
    mynewxticks[-1] = ""
    mynewxticks[0] = ""
    plt.xticks(myxticks, mynewxticks)

  def update_grid(self):
    self.baseax.grid()


  def savefigure(self):
    """ saving the figure in high resolution """
    """ path and name of output file """

    plt.savefig(self.figname, dpi=250, format = "png")

    """ avoid memory leak """
    plt.close()

  def add_bragg_peaks(self):
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
