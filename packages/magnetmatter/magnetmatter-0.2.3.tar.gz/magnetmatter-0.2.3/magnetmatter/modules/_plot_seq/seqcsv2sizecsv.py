# plot_seq_tools.py

import pandas as pd, numpy as np, math
# from plot_seq_tools import Notebook # amazingly we don't need to import Notebook!

""" global variable... """
upper_limit_in_nm = 120

def calculate_size(notebook):
  """
  df:
    pandas.dataframe with columns of refined parameters extracted from FullProf's .seq file
  wavelength:
    floating point number in Ångstrøm.

  What is calculated:
    Extracted from Anna's Excel Sheet. Do not change!

    CITATIONS MISSING!

    Y[°]	from .out as "Y-cos_ph1_pat1"

    σ_Y[°]	from .out error for above

    S_z[Å^-1]	from .out as "L-Size_ph1_pat1"

    σ_sz[Å^-1]	from .out error for above.

    Y[Å^-1] = Y[°] * PI^2 / 180 / 2 / wavelength[Å] * 1000

    σ_Y[Å^-1] = σ_Y[°] * PI^2 / 180 / 2 / wavelength * 1000

    # ab size

    a,b-size[nm] = 100 / Y[Å^-1]

    σ_a,b-size[nm] = 100 * (σ_Y[Å^-1]^2 / Y[Å^-1]^4)^0.5

    # c size

    c-size[nm] = 100 / (Y[Å^-1] + S_Z[Å^-1])

    σ_c-size[nm] = =100 * ((σ_Y[Å^-1]^2 + σ_sz[Å^-1]^2) / (Y[Å^-1] + S_z[Å^-1])^4)^0.5

  """
  def calc_inverse_lorentzian(ydegree):
    """ helper function (can also be used for ydegree_error!)

    Y[Å^-1] = Y[°] * PI^2 / 180 / 2 / wavelength[Å] * 1000

    this function only works because <wavelength> is already defined in the parent function

    """
    yinverseangstroem = ydegree * math.pow(math.pi, 2) / 36.0 / notebook.wavelength * 100
    return yinverseangstroem

  def multiply_invers_100(somevalue):
    """ helper function

    a,b-size[nm] = 100 / Y[Å^-1]

    """
    try:
      absize = 100 / somevalue
    except ZeroDivisionError:
      """ we return 100 nm. This is well beyound the reoslution limitation
      of DMC (reliable below 40 nm) and also for synchrotrons such as P02.1
      beamline at Petra III (resolution limit below ~ 100 nm) """
      global upper_limit_in_nm
      absize = upper_limit_in_nm
    return absize


  columnnames = []

  for col in notebook.lorsizelist:
    """ working with Y-cos_ph1_pat1
    to create L-Size_ph1_pat1, ab-size and c-size
    plus all errors """
    lorsize = "Y-cos"
    columnnames.append(col)
    columnnames.append(col + "_err")
    stripped = col.strip(lorsize)
    lorsizedistribution = "L-Size"
    columnnames.append(lorsizedistribution+stripped)
    columnnames.append(lorsizedistribution+stripped+"_err")
    absize = "ab-size"
    columnnames.append(absize+stripped)
    columnnames.append(absize+stripped+"_err")
    csize = "c-size"
    columnnames.append(csize+stripped)
    columnnames.append(csize+stripped+"_err")

  """ creating the outlay for the sizedf filled with zeros """
  myzeros = np.zeros( shape=(notebook.seqdf[notebook.lorsizelist[0]].size, 8*len(notebook.lorsizelist)) )

  """ initializing sizedf with columns from columnnames"""
  newdf = pd.DataFrame(myzeros, index = notebook.seqdf.index, columns = columnnames)
  for col in newdf.columns:
    try:
      """ importing columns from seqdf to sizedf """
      newdf[col] = notebook.seqdf[col]
    except KeyError:
      pass
  for col in columnnames:
    """ filling out the columns corresponding to ab- and c-size """
    if lorsize in col and not col.endswith("_err"):
      newdf[col] = newdf[col].apply(calc_inverse_lorentzian)
      newdf[col+"_err"] = newdf[col+"_err"].apply(calc_inverse_lorentzian)
      stripped = col.strip(lorsize)
      newdf[absize+stripped] = newdf[col].apply(multiply_invers_100)
      """ σ_a,b-size[nm] = 100 * (σ_Y[Å^-1]^2 / Y[Å^-1]^4)^0.5 """
      target = absize+stripped+"_err"
      newdf[target] = newdf[col+"_err"].apply(lambda x: math.pow(x,2))
      newdf[target] = newdf[target].div(newdf[col].apply(lambda x: math.pow(x,4)))
      newdf[target] = newdf[target].apply(lambda x: math.sqrt(x))
      newdf[target] = newdf[target].apply(lambda x: x*100)
      """ c-size[nm] = 100 / (Y[Å^-1] + S_Z[Å^-1]) """
      target = csize+stripped
      newdf[target] = newdf[col] + newdf[lorsizedistribution+stripped]
      newdf[target] = newdf[target].apply(multiply_invers_100)
      """ σ_c-size[nm] = =100 * ((σ_Y[Å^-1]^2 + σ_sz[Å^-1]^2) / (Y[Å^-1] + S_z[Å^-1])^4)^0.5 """
      target = csize+stripped+"_err"
      # if "_ph3" in col:
      #   print("None =",None)
      #   import pdb; pdb.set_trace();
      newdf[target] = newdf[col+"_err"].apply(lambda x: math.pow(x,2))
      newdf[target] = newdf[target] \
        + newdf[lorsizedistribution+stripped+"_err"].apply(lambda x: math.pow(x,2))
      newdf[target] = newdf[target] \
        .div((newdf[col] + newdf[lorsizedistribution+stripped]).apply(lambda x: math.pow(x,4)))
      newdf[target] = newdf[target].apply(lambda x: math.sqrt(x))
      newdf[target] = newdf[target].apply(lambda x: x*100)
      """ some NaNs may have been introduced, we replace by 100 (nm) that marks
      the upper insturmental resolution for both neutron and synchrotron diffraction

      EDIT: infinity was introduced in calculating error. These infinity are
      replaced with 100 as well."""
      # celebrate!
  global upper_limit_in_nm
  newdf.fillna(upper_limit_in_nm,inplace=True)
  newdf = newdf.replace(np.inf, upper_limit_in_nm)
  for col in columnnames:
    if col.endswith("_err"):
      continue
    indices_to_change = np.where(newdf[col] >= upper_limit_in_nm)[0]
    if indices_to_change.size != 0:
      newdf[col][newdf.index[indices_to_change]] = upper_limit_in_nm
      newdf[col+"_err"][newdf.index[indices_to_change]] = 0


  # print("notebook.exp_name =",notebook.exp_name)
  # import pdb; pdb.set_trace();

  """ cleaning up if NaNs have been introduced by the multiply_invers_100 function

  EDIT: cleaning up (that is removing all entries with NaN) caused the sizedf
  to be empty, even though one phase had a defined calculated size. But a second
  phase without a broadening could hide this fact. Instead of NaN, a 200 nm is appended
  in the multiply_invers_100 function.

  The code below has not been changed... should still work. """
  indices_with_nan = set(np.where(np.isnan(newdf))[0])
  indices_to_keep  = [index for index in range(newdf.index.size) if index not in indices_with_nan]
  newdf = newdf.iloc[indices_to_keep]
  """ saving to .csv """
  newdf.to_csv("_size.csv")
  """ return the sizedf dataframe """
  return newdf







# end
