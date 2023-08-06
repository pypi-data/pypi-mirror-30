# plot_seq_tools.py

from auxiliary import cm2inch
from datetime import datetime
import os, numpy as np, pandas as pd, sys, re, math
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.ticker import MaxNLocator
from extract_pcr import getwavelength
from find_tools import findfolders_abspath, findfiles_abspath



class Base():
  def __init__(self, nb, angle_range = None, minute_range = None, printsize = "two_in_docx"):
    self.df = nb.datdf
    self.outpath = nb.outpath
    self.system = nb.exp_name
    self.printsize = printsize
    self.path = os.getcwd()
    self.minute_range = minute_range
    """ checking if dataframe is empty """
    if self.df.empty:
      print("--no data frames have been found!")
      return -1

    self.angles = self.df.index.values
    if type(angle_range) == type(tuple()):
      start,end = angle_range
      mymask1 = self.angles > start
      mymask2 = self.angles < end
      mymask = mymask1 == mymask2
      self.df = self.df.iloc[mymask]


    self.defining_sizes()


  def celcius2latex(self, mystring = ""):
    """ returns a latexified string to be used in plt.
    e.g. 500oC --> 500$^o$C """
    return re.sub("(\d)oC","\g<1>°C",mystring)

  def setting_qspace(self):
    for self.myfolder in findfolders_abspath():
      pcrs = findfiles_abspath(".pcr", path = self.myfolder)
      if len(pcrs) > 0:
        self.wavelength = getwavelength(pcrs[0])
        break
    vfunc = np.vectorize(math.sin)
    self.df.index = math.pi * 4 / self.wavelength * ( vfunc( math.pi / 180 / 2 * self.df.index.values) )
    os.chdir(self.path)
    """ this is mask for Q-space """
    mymask1 = self.df.index.values > 3.2
    mymask2 = self.df.index.values < 1.9
    mymask = mymask1 == mymask2
    self.df = self.df.iloc[mymask]
    self.angles = self.df.index.values


  def meshgrid(self):
    """prepare meshgrids and plotting parameters"""
    self.angle_mesh,self.time_mesh = np.meshgrid(self.angles, self.minutes)
    self.signals = self.df.values.T


  def plot1(self):
    """ doing the actual plotting """
    fig = plt.figure(figsize=self.figsize)

    """higher number for nbin yields higher level of detail in plot"""
    self.nbins = [100] # 10 does not show the weak features... no difference between 100 and 200
    nbin = self.nbins[0]
    if len(self.signals) == 0: # the specified range for plotting includes no values.
      return -1
    levels = MaxNLocator(nbins=nbin).tick_values(self.signals.min(), self.signals.max())
    style = self.styles[0]
    plt_cmap = plt.get_cmap(style)
    CS = plt.contourf(self.angle_mesh, self.time_mesh, self.signals,
                      cmap=plt_cmap,
                      levels = levels
                      )

    """ getting the axis object """
    self.baseax = plt.gca()

    """ adding colorbar """
    import matplotlib
    matplotlib.rcParams.update({'font.size': self.textsize})
    mybar = plt.colorbar()

    """ setting up xlabel and ylabel """
    plt.xlabel(r'Q-space [$\AA^{-1}$]', size = self.xlabelsize)
    ylabel = plt.ylabel('time [min]', size = self.ylabelsize)

    """ changing the size of x ticks"""
    for tick in self.baseax.xaxis.get_major_ticks():
      tick.label.set_fontsize(self.xticksize)

    for tick in self.baseax.yaxis.get_major_ticks():
      tick.label.set_fontsize(self.yticksize)

    """ set padding of first y-axis minute ticks and change length """
    self.baseax.get_yaxis().set_tick_params(pad=1, length = 2)

    """ set padding of x-axis angle ticks and change length"""
    self.baseax.get_xaxis().set_tick_params(pad=1, length = 2)


  def rotating_ylabels(self, printsize = "two_in_docx"):
    """ rotating and repositioning the ylabels """
    if self.printsize == "thirdpage":
      self.baseax.yaxis.set_label_coords(0,1.05)
      ylabel.set_rotation(0)




  def defining_sizes(self, printsize = "two_in_docx"):
    """ pypot uses inches... """
    inch2cm = 1.0 / 2.54
    """ horizontal length of graph """
    dimension = {"onepage": 17 * inch2cm, "two_in_docx": 8 * inch2cm, "thirdpage": 5.0 * inch2cm}

    choosen_dimension = dimension[printsize]
    """ sizes of figure, ticks, labels and legends """
    # height_factor = 1.0 if dwarf else 1.5
    height_factor = 1.4
    if choosen_dimension == dimension["two_in_docx"]:
      self.figsize = (choosen_dimension,choosen_dimension * height_factor)
      self.textsize = 8
      self.titlesize = self.textsize + 1
      self.xlabelsize = self.textsize
      self.ylabelsize = self.textsize
      self.xticksize = self.textsize
      self.yticksize = self.textsize -1
      self.ylabelpos = (-0.12, 0.5)
    elif choosen_dimension == dimension["thirdpage"]:
      self.figsize = (choosen_dimension,choosen_dimension * height_factor)
      self.textsize = 6
      self.titlesize = self.textsize
      self.xlabelsize = self.textsize
      self.ylabelsize = self.textsize
      self.xticksize = self.textsize
      self.yticksize = self.textsize

  def title(self):
    """ setting title """
    title_ypos = 1.0 # percent of canvas.
    plt.title( self.celcius2latex(self.system), size = self.titlesize, y = title_ypos)

  def tight_layout(self):
    self.myyticks = self.baseax.get_yticks()
    plt.yticks(self.myyticks, ["100" for ytick in self.myyticks])
    """ enable tight layout """
    plt.tight_layout()  # do not use with altered ylabels.
    replacement = [int(y) for y in self.myyticks]
    replacement[replacement.index(0)] = ""
    plt.yticks(self.myyticks, replacement)
    plt.ylim(min(self.minutes),max(self.minutes))
    self.myxticks = self.baseax.get_xticks()
    plt.xticks(np.arange(2.1,3.2,0.2))
    """ setting xlim """
    plt.xlim(2.05,3.2)
    self.baseax.yaxis.set_label_coords(*self.ylabelpos)



  def savefig(self):
    """ saving plot , outfolder has already been created """
    figname = self.system + ".png"
    plt.savefig( os.path.join(self.outpath,figname), dpi = 250 )
    plt.close() # save pc from crashing!



class Dioptas(Base):
  def __init__(self, nb, angle_range = None, minute_range = None, printsize = "two_in_docx"):
    args = (nb, angle_range, minute_range, printsize)
    super(Dioptas, self).__init__(*args)


    index = "angle"
    """ index was already set... """
    # df = df.set_index(index)
    """ prepare minutes array"""
    duration_frame = 5 # seconds, blindly hardcoded...
    nb_of_frames = len(self.df.columns.values)

    """ converts the frames, e.g. frame18, frame19, .. frameN to integer list [18, 19, .., N] """
    myframes = [int(index.strip("frame")) for index in self.df.columns]

    """ blindly defines the first frame e.g. frame193 to be zero point in time """
    myframes = [integ - myframes[0] for integ in myframes]
    minutes = [frame * (duration_frame / 60.0) for frame in myframes]
    self.minutes = np.array(minutes)

    """ truncate DataFrame if user asks for it
    truncation is done by indicating what (x1,x2) minutes to include"""
    if type(self.minute_range) is type(tuple()):
      """ this is to cut the time, NOT the angles!! """
      lower_bound, higher_bound = self.minute_range
      con1 = minutes > lower_bound
      self.df = self.df.iloc[:,con1]
      minutes = minutes[con1]
      con2 = minutes < higher_bound
      self.df = self.df.iloc[:,con2]
      self.minutes = minutes[con2]

      """check if any values are left"""
      if len(self.minutes) == 0:
        print("no values to plot for",self.minute_range, "in", path)
        return 1


    """ these are styles that have better contrast:
    choosen_cmaps = "gnuplot gnuplot2 jet ocean viridis Paired Oranges PuBu " +\
        "PuBuGn PuRd Reds YlGn YlGrBu YlOrRd cool"
    """
    self.styles = [style for style in 'jet'.split()]

  def setting_minutes(self):
    """ changing yticks and their size"""
    self.minutes_simplified = [int(i) for i in self.minutes]
    plt.yticks(self.minutes_simplified)


  def tick_spacing(self):
    """ showing only time-yticklabel every tick_spacing """
    limit = max(self.minutes) - min(self.minutes)
    if limit <= 20:
      tick_spacing = 1 # min
    if limit <= 60:
      tick_spacing = 5 # min
    else:
      tick_spacing = 10 # min


    self.baseax.yaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
    # """ this is important when the 2theta view is truncated... """
    # self.baseax.xaxis.set_major_locator(ticker.MultipleLocator(0.5))


def plotting_PETRApredata(nb, minute_range = "tuple_of_low_high", angle_range = "tuple_of_low_high", printsize = "two_in_docx"):

  """plotting of saved pd.DataFrame as .csv prepared from dioptas .dat"""

  d = Dioptas(nb, angle_range, minute_range, printsize)

  d.setting_qspace()

  d.meshgrid()

  if d.plot1() == -1:
    return -1

  d.setting_minutes()

  d.tick_spacing()

  d.rotating_ylabels()

  d.title()

  d.tight_layout()

  d.savefig()

  return 0




class Dmc(Base):
  def __init__(self, nb, angle_range = None, minute_range = None, printsize = "two_in_docx"):
    args = (nb, angle_range, minute_range, printsize)
    super(Dmc, self).__init__(*args)

    """ limiting dataframe to first x minutes """
    if type(minute_range) == type(tuple()):
      xmin,xmax = minute_range
      self.df = self.df.loc[:, self.df.columns <= xmax]
      self.df = self.df.loc[:, self.df.columns >= xmin]
    if type(minute_range) == type(int):
      index_to_last = minute_range
      self.df = self.df.iloc[:,minute_range:]

    """ changing yticks and their size"""
    self.minutes = self.df.columns.values
    self.minutes_simplified = [int(float(i)) for i in self.minutes]

    self.styles = [style for style in 'gnuplot'.split()]
    """ these are styles with better contrast:
    choosen_cmaps = "gnuplot gnuplot2 jet ocean viridis Paired Oranges PuBu " +\
        "PuBuGn PuRd Reds YlGn YlGrBu YlOrRd cool"
    """

  def setting_minutes(self):
    """ alternating yticks, skipping every other ytick """
    if 1:
      # temp_simplified = [int(t) for i,t in enumerate(temperatures) if i%2==0]
      self.minutes_simplified = [int(t) for i,t in enumerate(self.minutes_simplified) if i%2==0]
      new_minutes = [t for i,t in enumerate(self.minutes) if i%2==0]
    else:
      new_minutes = self.minutes

    plt.yticks(new_minutes, self.minutes_simplified)


  def remove_sapphire_peak(self):
    """ this is to remove the single crystal sapphire peak... """
    ab = self.df.index < 61.6
    ba = self.df.index > 62.5
    mymask = ab == ba
    """ pandas gives warning about possible bad use
    of setting values of a slice-view. I don't know how to silence it... """
    self.df[mymask] = 0
    """ this command gives no warnings. but it might be deprecented in future version?
    https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.set_value.html
    the below is being deprecated. I will continue using the above with warning.
    """
    # df.set_value(mymask,df.columns,0)

  def dotted_lines(self):
    """ adding visual clue for each frame """
    for y in self.minutes: # dotted lines
      plt.plot([min(self.angles), max(self.angles)], [y, y], "--r", linewidth=1, alpha = 0.5) # dotted lines



def plotting_DMCpredata(nb, minute_range = 'tuple_input', angle_range = (45,80), printsize = "two_in_docx"):

  d = Dmc(nb, angle_range, minute_range, printsize)

  d.remove_sapphire_peak()

  d.setting_qspace()

  d.meshgrid()

  if d.plot1() == -1:
    return -1

  d.setting_minutes()

  d.dotted_lines()

  # self.baseax.xaxis.set_major_locator(ticker.MultipleLocator(0.5))


  d.rotating_ylabels()

  d.title()

  d.tight_layout()

  d.savefig()

  return 0














# end
