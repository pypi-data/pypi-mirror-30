# plot_seq_tools.py

from auxiliary import cm2inch
import os, numpy as np, pandas as pd, sys, re, math
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.ticker import MultipleLocator
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

    self.xvalues = self.df.index.values
    if type(angle_range) == type(tuple()):
      start,end = angle_range
      mymask1 = self.xvalues > start
      mymask2 = self.xvalues < end
      mymask = mymask1 == mymask2
      self.df = self.df.iloc[mymask]
    self.xvalues = self.df.index.values


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
    """ this is mask for Q-space

    EDIT: use xlim instead! """
    self.xlow = 2.8
    self.xhigh = 3.2
    mymask1 = self.df.index.values > self.xlow
    mymask2 = self.df.index.values < self.xhigh
    mymask = mymask1 == mymask2
    self.df = self.df.iloc[mymask]
    self.xvalues = self.df.index.values


  def meshgrid(self):
    """prepare meshgrids and plotting parameters"""
    self.angle_mesh,self.time_mesh = np.meshgrid(self.xvalues, self.yvalues)
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
    matplotlib.rcParams.update({'font.size': self.textsize})
    self.mybar = plt.colorbar(ticks = [])
    # self._mybarvalues = self.mybar._tick_data_values
    # self.mybar._tick_data_values = [1000000 for x in self._mybarvalues]

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




  def defining_sizes(self):
    """ pypot uses inches... """
    inch2cm = 1.0 / 2.54
    """ horizontal length of graph """
    dimension = {"onepage": 17 * inch2cm, "two_in_docx": 8 * inch2cm, "thirdpage": 5.0 * inch2cm, "four_in_docx": 4.2 * inch2cm}
    choosen_dimension = dimension[self.printsize]

    """ sizes of figure, ticks, labels and legends """
    height_factor = 1.3
    if self.printsize == "two_in_docx":
      self.figsize = (choosen_dimension,choosen_dimension * height_factor)
      self.textsize = 8
      self.titlesize = self.textsize + 1
      self.xlabelsize = self.textsize
      self.ylabelsize = self.textsize
      self.xticksize = self.textsize
      self.yticksize = self.textsize -1
      self.linewidth = 0.8
      self.ylabelpos_pre = (0.5, 0.5)
      self.ylabelpos = (-0.12, 0.5)
      self.ytick_placeholder = "1000"
    elif self.printsize == "thirdpage":
      self.figsize = (choosen_dimension,choosen_dimension * height_factor)
      self.textsize = 6
      self.titlesize = self.textsize
      self.xlabelsize = self.textsize
      self.ylabelsize = self.textsize
      self.xticksize = self.textsize
      self.yticksize = self.textsize
    elif self.printsize == "four_in_docx":
      self.figsize = (choosen_dimension,choosen_dimension * height_factor)
      self.textsize = 5
      self.titlesize = self.textsize + 1
      self.xlabelsize = self.textsize
      self.ylabelsize = self.textsize
      self.xticksize = self.textsize
      self.yticksize = self.textsize
      self.ylabelpos_pre = (0.5, 0.5)
      self.ylabelpos = (-0.2, 0.5)
      self.linewidth = 0.4
      self.ytick_placeholder = "10000"

  def title(self):
    """ setting title """
    # title_ypos = 1.0 # percent of canvas.
    plt.title( self.celcius2latex(self.system), size = self.titlesize)#, y = title_ypos)

  def tight_layout(self):
    self.myyticks = self.baseax.get_yticks()
    plt.yticks(self.myyticks, [self.ytick_placeholder for ytick in self.myyticks])
    self.baseax.yaxis.set_label_coords(*self.ylabelpos_pre)
    """ enable tight layout """
    plt.tight_layout()  # do not use with altered ylabels.
    replacement = [int(y) for y in self.myyticks]
    replacement[replacement.index(0)] = ""
    plt.yticks(self.myyticks, replacement)
    plt.ylim(min(self.yvalues),max(self.yvalues))
    self.myxticks = self.baseax.get_xticks()
    plt.xticks(np.arange(self.xlow,self.xhigh,0.2))
    """ setting xlim """
    plt.xlim(self.xlow, self.xhigh)
    self.baseax.yaxis.set_label_coords(*self.ylabelpos)
    """ resetting colorbar tick values """
    # self.mybar._tick_data_values = self._mybarvalues

    plt.tick_params(
    axis='y',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    left='off',      # ticks along the bottom edge are off
    right='off',         # ticks along the top edge are off
    # labelbottom='off'
    ) # labels along the bottom edge are off

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
    self.yvalues = [frame * (duration_frame / 60.0) for frame in myframes]
    self.yvalues = np.array(self.yvalues)

    """ truncate DataFrame if user asks for it
    truncation is done by indicating what (x1,x2) minutes to include"""
    if type(self.minute_range) is type(tuple()):
      """ this is to cut the time, NOT the angles!! """
      lower_bound, higher_bound = self.minute_range
      con1 = self.yvalues > lower_bound
      self.df = self.df.iloc[:,con1]
      self.yvalues = self.yvalues[con1]
      con2 = self.yvalues < higher_bound
      self.df = self.df.iloc[:,con2]
      self.yvalues = self.yvalues[con2]

      """check if any values are left"""
      if len(self.yvalues) == 0:
        print("no values to plot for",self.minute_range, "in", path)
        return 1


    """ these are styles that have better contrast:
    choosen_cmaps = "gnuplot gnuplot2 jet ocean viridis Paired Oranges PuBu " +\
        "PuBuGn PuRd Reds YlGn YlGrBu YlOrRd cool"
    """
    self.styles = [style for style in 'jet'.split()]

  def setting_minutes(self):
    """ changing yticks and their size"""
    self.minutes_simplified = [int(i) for i in self.yvalues]
    plt.yticks(self.minutes_simplified)


  def tick_spacing(self):
    """ showing only time-yticklabel every tick_spacing """
    limit = max(self.yvalues) - min(self.yvalues)
    if limit <= 20:
      tick_spacing = 1 # min
    if limit <= 60:
      tick_spacing = 5 # min
    else:
      tick_spacing = 10 # min

    self.baseax.yaxis.set_major_locator(MultipleLocator(tick_spacing))
    # """ this is important when the 2theta view is truncated... """
    # self.baseax.xaxis.set_major_locator(MultipleLocator(0.5))

  def run(self):

    self.setting_qspace()

    self.meshgrid()

    if self.plot1() == -1:
      return -1

    self.setting_minutes()

    self.tick_spacing()

    self.rotating_ylabels()

    self.title()

    self.tight_layout()

    self.savefig()

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
    self.yvalues = self.df.columns.values
    self.minutes_simplified = [int(float(i)) for i in self.yvalues]

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
      new_yvalues = [t for i,t in enumerate(self.yvalues) if i%2==0]
    else:
      new_yvalues = self.yvalues

    plt.yticks(new_yvalues, self.minutes_simplified)


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
    for y in self.yvalues: # dotted lines
      plt.plot([min(self.xvalues), max(self.xvalues)], [y, y], "--r", linewidth = self.linewidth, alpha = 0.6) # dotted lines

  def run(self):

    """ unique for Dmc """
    self.remove_sapphire_peak()

    self.setting_qspace()

    self.meshgrid()

    if self.plot1() == -1:
      return -1

    self.setting_minutes()

    """ unique for Dmc """
    self.dotted_lines()

    self.rotating_ylabels()

    self.title()

    self.tight_layout()

    self.savefig()

    return 0














# end
