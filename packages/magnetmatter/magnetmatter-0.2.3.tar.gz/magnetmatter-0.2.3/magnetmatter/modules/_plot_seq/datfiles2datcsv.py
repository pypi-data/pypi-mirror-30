# datfiles2csv.py

import os, numpy as np, pandas as pd, sys, re
import numpy as np, pandas as pd, re, os
sys.path.append(r"C:\AU-PHD\General_Data\_python\PyPi\magnetmatter\magnetmatter\modules")
from auxiliary import natural_keys
from wrappers import time_response





@time_response
def genereate_CSV_from_dioptas_dat(workingdir = ""):
    """ generate CSV from dioptas .dat files.

    last edit: 2018-01-31

    Function is written to extract 2th values and Intensities from
    2D plots transformed to line diffractograms by the software Dioptas.

    OUTPUT:
        Saves a pd.DataFrame to "mycsv.csv" at "path/python_output".
    NOTE:
        if two frames have different number of angles, NaNs will be present.
        NaNs are replaced with zeroes.
    Note to Pelle:
        DO NOT TRY TO EXTRACT ERRORS. THERE ARE NONE GENERATED FROM DIOPTAS.
    """
    workingdir = workingdir if workingdir != "" else os.getcwd()
    os.chdir(workingdir)

    """get all dat files"""
    files = [d for d in os.listdir() if d.endswith(".dat")]

    """ skipping treatment if no dat files are found """
    if len(files) == 0:
      return pd.DataFrame

    """sorting the frames"""
    files.sort(key = natural_keys)

    """ only take every skipping'th frame to plot
    the higher number for skipping, the faster (but cruder)
    the visualization of the data frames will be.

    EDIT: removed... well left for rapid testing..."""
    # files = files[::100]

    """extacting 2th and counts"""
    df = 0
    index = "angle"
    i = 0; imax = len(files)

    """ loops through all .dat files"""
    for dat in files:
      i += 1
      # if i-1 == imax:
      #     break
      frame = dat.strip(r".dat")
      """friendly output to user"""
      if i % 100 == 0:
        print(i, "of", imax,". df.shape =",df.shape)

      with open(dat) as f:
        """loads in data and merge on angles"""

        """ the dioptas generated dat files are created with numpy's
        .savetxt function. Therefore loadtxt is used without hesitation """
        loaded = np.loadtxt(f)

        """ transforming loaded numpy array to pandas dataframe """
        df_tmp = pd.DataFrame(loaded, columns = [index, frame])

        """ checking if df is a pandas.DataFrame """
        if type(df) != type(df_tmp):
          df = df_tmp
        else:
          """ merges dataframes by filling nonmatching dimensions with NaNs """
          df = df.merge(df_tmp, on = index, how = "outer")

    """ fills all NaN with zeroes """
    df = df.fillna(0)

    """ saves pd.DataFrame to .csv"""
    df.to_csv(os.path.join(os.path.join("..","_dioptas_dats.csv")), index = False)

    return df






def generate_CSV_from_dmc_dat(workingdir = ""):
  """Extract predata from .dat files (DMC instrument)
  Args:
    path: full path to folder with .dat files.
  Returns:
    pandas.DataFrame with columns = timestamps, index = 2th angles, values = extracted signal values.
  Note:
    the errors are also extracted, but not returned in the current code.
  """
  oldpath = os.getcwd()
  os.chdir(workingdir)
  dats = [dat for dat in os.listdir() if dat.endswith(".dat")]
  if len(dats) == 0:
    print("skipping ",os.getcwd())
    return -1
  """return int if char is a digit, otherwise a string char is returned"""
  # return_chars_or_digits = lambda text: int(text) if text.isdigit() else text
  '''alist.sort(key=natural_keys) sorts in human order'''
  # natural_keys = lambda text: [return_chars_or_digits(c) for c in re.split("(\d+)", text)]
  """sorting the frames"""
  dats.sort(key=natural_keys)

  firstRun = True
  frames = []
  for num, file in enumerate(dats):
    frames.append(num+1) #float(file.strip("frame").strip(".dat")) )
    with open(file,"r") as fileHandler:
      open_file = fileHandler.read().split("\n")

    gdic = dict()
    for index, line in enumerate(open_file):
      # print(line)
      for linei in line.split(","):
        for i in linei.split(";"):
          g = re.search("(.*)=(.*)",i)
          if g:
            gdic[g.group(1).strip()] = g.group(2).strip("'")
    metadata1 = open_file[:3]
    data = open_file[3:-7]
    if firstRun:
      for i, line in enumerate(open_file):
        if "Filelist" in line:
          startmetadata2 = i
          break
    metadata2 = open_file[startmetadata2:]
    halfway = int(len(data) / 2)
    signal = data[ : - halfway ]
    error =  data[ halfway : ]

    signal = [s.split() for s in signal]
    error = [s.split() for s in error]

    flatten = lambda l: [float(item) for sublist in l for item in sublist]

    signal = flatten(signal)
    error = flatten(error)

    metadata1 = [line.split(",") for line in metadata1]
    metadata2 = [line.split() for line in metadata2]

    sample_description = metadata1[0][1]
    wavelength = metadata1[1][0]
    date = metadata1[1][-1]
    angle = metadata1[2][0]
    sample = metadata1[2][1]
    frame_number = metadata2[0]

    metadata = [sample_description, wavelength, date, sample, frame_number]

    if firstRun:
      # angle = [float(i) for i in angle.split()]
      angles = [int(float(i)*10) for i in angle.split()]
      low2th, step2th, high2th, maxcounts = angles
      # break
      angles = [float(i)/10 for i in range( low2th, high2th + 1, step2th) ] # +1 for pythons range system
      angles = np.array(angles)
      signals = np.ndarray(shape = ( len(dats), len(signal) ), dtype="float64")
      errors = np.ndarray(shape = ( len(dats), len(error) ), dtype="float64")
      # metadatas = np.ndarray(shape = ( len(dats), len(metadata) ), dtype="s20")
      metadatas = []
      firstRun = False
    signals[num] = signal
    errors[num] = error
    metadatas.append(metadata)
  import pandas as pd
  from datetime import datetime
  import datetime as dt
  frames = [" ".join(["frame",str(int(num))]) for num in frames]
  df = pd.DataFrame(data=signals.T, index=angles, columns = frames)
  df.index.name = "angle"

  """extracting true frame and timestamps from .dat files"""
  dates = list(); frames = list()
  for dat in dats:
    with open(dat, "r") as datfile:
      for line in datfile:
        found1 = re.search("Date=\'([\d\s\-:]+).*\'",line) # Date='2016-12-21 17:04:35'
        found2 = re.search("Filelist=\'.*:\d*:(\d+-\d+)\'",line) # Filelist='dmc:2016:91790-91793'
        if found1:
          date = found1.group(1)
          date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
          dates.append(date)
          continue
        elif found2:
          frame = found2.group(1)
          frames.append(frame)
          break
  # + 8 to accomodate that it took 8 minutes to acquire first frame.
  # first_frame_timedelta = dt.timedelta(minutes = 8)
  deltatimes = [date - dates[0] for date in dates]
  seconds = [dt.seconds for dt in deltatimes]
  minutes = [second / 60.0 for second in seconds]
  df.columns = minutes
  # import pdb; pdb.set_trace();
  df.to_csv(os.path.join(os.path.join("..","_dmc_dats.csv")), index = True)
  os.chdir(oldpath)
  return df
#
#
#


















  # end
