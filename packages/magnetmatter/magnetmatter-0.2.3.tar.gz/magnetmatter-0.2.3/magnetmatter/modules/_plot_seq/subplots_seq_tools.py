# plot_seq_tools.py

import os, pandas as pd, matplotlib.pyplot as plt, numpy as np, re
from auxiliary import cm2inch
from itertools import chain

""" choosing plotting style """
# plt.style.use("seaborn-darkgrid") # plt.style.available
plt.style.use("classic") # plt.style.available


class SubplotManager():
  def __init__(self, notebook, nrows = 1, ncols = 1,sharex=False, sharey=False, squeeze=True, subplot_kw=None, gridspec_kw=None, figsize = (8,8), **fig_kw):
    self.fig, self.ax = plt.subplots(
    nrows=nrows,
    ncols=ncols,
    sharex=sharex,
    sharey=sharey,
    squeeze=squeeze,
    subplot_kw=subplot_kw,
    gridspec_kw=gridspec_kw,
    figsize = figsize,
    **fig_kw,
    )
    # plt.subplots_adjust(left=1, bottom=1, right=1, top=1, wspace=1, hspace=1)
    self.shape = (nrows, ncols)
    self.size = nrows*ncols
    self.savefig = False # save plotting preliminiary subplots until we are through all subfolders.

    self.flataxes = list(chain(*self.ax)) if self.size > 2 else list(chain(self.ax))

    self.notebook = notebook
    self.notebook._textsize = 10
    self.notebook._ticksize = 7
    self.remove_xlabel_and_xticks = False
    self.dpi = 250

    """ this is to modify the legend size... """
    import matplotlib
    matplotlib.rcParams.update({'font.size': self.notebook._textsize})


  # def show(self):
  #   plt.show()


  def _reduce_view(self, df):
    """ reducing the number of displayed datapoints to X
    for neutron data this removes all kinks and is not preferable. """
    if self.notebook.datdftype == "dioptas":
      number_of_points_displayed = 100#(notebook.seqdf.shape[0]-1) // 10
    elif self.notebook.datdftype == "dmc":
      number_of_points_displayed = df.shape[0]-1
    view = [int(i) for i in np.linspace(0, df.shape[0]-1, number_of_points_displayed)]
    view = set(view)
    view = sorted(list(view))
    view = df.iloc[view]
    return view

  def _get_nonmagnetic_phases(self):
    return [phase for phase in self.notebook.phases if not " magnetic" in phase]


  def _label_text(self, mystring, label):
    """ returns a latexified string to be used in plt.
    e.g. 500oC --> 500$^o$C """
    trans1 = re.sub("(\d)oC","\g<1>°C",mystring)
    trans2 = re.sub(" nuclear","",label)
    return trans1 + ": " + trans2



  def _add_subplot(self, df, ax, y = "y", yerr = "yerr", label = "label"):
    if ax == "":
      ax = df.plot(y=y,yerr=yerr, label = label, figsize = cm2inch(8,6))
      return ax
    else:
      df.plot(y=y,yerr=yerr, ax = ax, label = self._label_text(self.notebook.exp_name, label) )


  def _setting_up_plot(self, ax, sm, title, ylabel_text="ylabel_text"):
    """ handling graph text """
    # ax.autoscale_view('tight')


    """ ylabel text and size """
    ax.set_ylabel(ylabel_text, size = self.notebook._textsize)
    # title = self.notebook.ref_name if title == "" else title
    # title = ""
    # ax.set_title(title, size = self.notebook._textsize)
    for tick in ax.xaxis.get_major_ticks():
      tick.label.set_fontsize(self.notebook._ticksize)
    for tick in ax.yaxis.get_major_ticks():
      tick.label.set_fontsize(self.notebook._ticksize)

    if sm.remove_xlabel_and_xticks:
      ticklabels = [label for label in ax.xaxis.get_ticklabels()]
      ax.xaxis.set_ticklabels(["" for x in ticklabels])
      # import pdb; pdb.set_trace();
      # ax.get_xaxis().get_major_ticks._visible = False
      ax.set_xlabel("", size = self.notebook._textsize)
    else:
      ax.set_xlabel(self.notebook.seqdf.index.name, size = self.notebook._textsize)

    """ ensure output directory exists """
    if not os.path.exists(self.notebook.suboutpath):
      os.makedirs(self.notebook.suboutpath)

    """ adjusting ylim """
    ax.set_ylim([-5,125])


    ax.grid()


    """ adding background color to legends """
    mytext = ax.legend().get_texts()
    legend = ax.legend(frameon = 1, loc = "best", prop = {"size": self.notebook._ticksize} )
    frame = legend.get_frame()
    frame.set_facecolor('white')
    frame.set_edgecolor('black')
    if len(mytext) > 4:
      ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),
            ncol=3, fancybox=True, shadow=True)
    elif len(mytext) > 2:
      ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),
            ncol=2, fancybox=True, shadow=True)
    else:
      pass
      # ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),
      #       ncol=2, fancybox=True, shadow=True)
    """ this is to modify the legend size... """
    import matplotlib
    matplotlib.rcParams.update({'font.size': self.notebook._ticksize})



  def plotphaseweightfractions(self,  sm = "subplotmanager", title = "", ax = ""):
    """ plotting the phase weight fractions from seqdf for all phases in refined model """

    """ defining path to save plot """
    outpath = self.notebook.suboutpath if ax == "" else self.notebook.outpath

    def get_cols_to_plot(df):
      """ making a list of weight_fractions for all phases.

      this became a subfunctions in order to skip it when debugging..."""
      cols_to_plot = []
      """ a bit tricky construct. we are working with both magnetic and nuclear
      phases. I can only assume that the FP user has bundled all open parameters
      to one phase (either nuclear or magnetic). We already have a list of
      lorentsian size distributions. we assume these belong to same phase as the
      refined intensity / weight_fraction """
      i = 0
      for col in df.columns:
        if "Weight_Fraction" in col and not col.endswith("_err"):
          if col.lstrip("Weight_Fraction") in self.notebook.lorsizelist[i]:
            cols_to_plot.append(col)
            i+=1
      return cols_to_plot


    """ organising reduced dataframe (view), the phase names and the columns to plot (ignoring magnetic phases) """
    view = self._reduce_view(self.notebook.seqdf)
    phases = self._get_nonmagnetic_phases()
    cols_to_plot = get_cols_to_plot(self.notebook.seqdf)

    """ plotting phase weight fraction for all nonmagnetic phases in model """
    for phase, col in zip(phases, cols_to_plot):
      # self._add_subplot(view, ax, y = col, yerr = col+"_err", label = phase)
      view.plot(y=col,yerr=col+"_err", ax = ax, label = self._label_text(self.notebook.exp_name, phase) )


    """ handling x, y, title labels and adjusting graphs etc.. """
    self._setting_up_plot(ax, sm, title, ylabel_text = "phase weight fraction [%]")

    # plt.tight_layout()
    """ saving graph """
    if sm.savefig:
      plt.tight_layout()
      sm.fig.savefig(os.path.join(outpath, "PVF_"+title+".png"), dpi = sm.dpi)
    #
    # """ avoid memory leak """
    # plt.close()
    return



  def size_plot(self, sm, title = "", ax = ""):
    """ plotting the app. cryst. sizes found in sizedf """

    """ defining path to save plot """
    outpath = self.notebook.suboutpath if ax == "" else self.notebook.outpath

    """ check if sizedf is empty """
    if self.notebook.sizedf.size == 0:
      message = "self.notebook.sizedf.size = " + str(self.notebook.sizedf.size)
      with open(os.path.join(self.notebook.suboutpath,self.notebook.ref_name+".txt"), "w") as writing:
        writing.write(message)
      print("        " + message)
      return

    """ reducing the number of points displayed... """
    view = self._reduce_view(self.notebook.sizedf)

    """ plotting app. cryst. sizes for all phases in refined model """
    for phase, col in zip(self._get_nonmagnetic_phases(), self.notebook.lorsizelist):
      target = "ab-size" + col.strip("Y-cos") # Y-cos is lorentzian size broadening
      self._add_subplot(view, ax, y = target, yerr = target+"_err", label = phase)

    self._setting_up_plot(ax, sm, title, ylabel_text = "app. cryst. size [nm]")

    # """ ensuring every text is within plot """
    """ saving plot in ./root/_mytest """
    if sm.savefig:
      plt.tight_layout()
      sm.fig.savefig(os.path.join(outpath,"size_"+title+".png"), dpi = sm.dpi)

    # """ avoiding memory leak """
    # plt.close()
    return









# end
