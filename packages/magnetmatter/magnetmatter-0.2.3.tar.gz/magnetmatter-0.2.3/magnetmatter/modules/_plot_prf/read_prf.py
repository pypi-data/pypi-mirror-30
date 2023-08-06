from prf_plot_tools import excluded_regions
import pandas as pd, numpy as np
import re

def read_prf(prfpath = ""):
  """ determines the type of the requested prf, reads it in accordingly and
  returns a tuple of prf_type and pd.dataframe

  THIS IS THE MAIN FUNCTION OF THIS COLLECTION
  """
  if prfpath == "": return ("NO PRF PATH GIVEN", -1)
  prf_type = get_prf_type(prfpath)
  if prf_type == "dmc":
    df = read_dmc(prfpath)
  elif prf_type == "xray":
    df = read_xray(prfpath)
  else:
    return ("NO PRF READ!", -1)
  return (prf_type, df)

def get_prf_type(prfpath):
  """ searching prf file until indicators for a specific diffraction data type is found.

  prf supported:
    dmc (and also HRPT)
    xray (and also dioptas generated 1-line patterns from synchrotrons)
  """
  with open(prfpath, "r") as reading:
    for num,line in enumerate(reading):
      is_dmc = re.search(".*92.*12.800.*0.10000", line)
      is_xray = re.search(".*2Theta.*Yobs.*Ycal.*Yobs-Ycal.*Backg.*Posr.*(hkl).*K",line)
      if is_dmc:
        return "dmc"
      elif is_xray:
        return "xray"
  return "no known prf-type was found..."


def read_dmc(prfpath):
  """ reading dmc/hrpt prf file and returns a pd.dataframe """
  with open(prfpath, "r") as reading:
    for num,line in enumerate(reading):
      if num >= 5:
        numbers = [float(number) for number in line.strip().split() ]
        if len(yobs) != entries:
          yobs += numbers
        elif len(ycalc) != entries:
          ycalc += numbers
        else:
          bragg_reflections += numbers
      elif num == 2:
        end,start,step = [float(number) for number in line.strip().split()[0:3]]
        angles = np.arange(start,end+step,step)
        entries = len(angles)
        yobs = list()
        ycalc = list()
        bragg_reflections = list()

  """ preparing dataframe """
  df = pd.DataFrame()
  for col_name, col in zip(["2Theta", "Yobs", "Ycal"], [angles, yobs, ycalc]):
    df[col_name] = col
  return df

def read_xray(prfpath):
  """ reading convential xray/synchroton prf file and returns a pd.dataframe """
  if prfpath == "": return "no valid prf was given"
  nb_excluded_regions = excluded_regions()
  df = pd.read_csv(prfpath, skiprows = 3+nb_excluded_regions, delimiter="[\t]+", engine="python")
  df = df[["2Theta","Yobs","Ycal"]]
  for col in df.columns.values:
    df[col] = pd.to_numeric(df[col], errors="coerce")
  df = df.dropna(axis=0)
  return df
