# bragg_peak_indications.py

from math import cos, sqrt, sin, asin, pi
import numpy as np, os, sys
sys.path.append( r"C:\AU-PHD\General_Data\_python\PyPi\magnetmatter\magnetmatter\modules" )

from extract_pcr import getwavelength
from find_tools import findfile_abspath

""" things to remember:
forbindden reflections for e.g. BCC, FCC, diamond, triangular lattice

"""

""" where did I get the formulars for the lattice spacing d?
wikipedia, yes: https://en.wikipedia.org/wiki/Crystal_structure
"""

class Crystals():
  """ to contain all Crystal objects. """
  def __init__(self, abs_path_to_pcr = ""):
    self.crystals = list()
    if abs_path_to_pcr == "":
      self.pcr = findfile_abspath(".pcr")
    else:
      self.pcr = abs_path_to_pcr
    self.wavelength = getwavelength(self.pcr)
    self.parse_pcr()

  def parse_pcr(self):
    crystals = list()
    with open(self.pcr, "r") as reading:
      for line in reading:
        if "!  Data for PHASE number: " in line:
          reading.__next__() # not important line.
          phasename = reading.__next__().strip()
        if "!     a          b         c " in line:
          """
          !     a          b         c        alpha      beta       gamma      #Cell Info
             5.144739   5.144739  14.266463  90.000000  90.000000 120.000000
          """
          line = reading.__next__()
          unitcell_dimensions = tuple(line.split()[0:6])
          mycrystal = Crystal( *(phasename, self.wavelength, *unitcell_dimensions) )
          # will this set all crystals to same object?
          # no, it does not appear to do so
          self.crystals.append( mycrystal )



class Crystal():
  """ keep track of crystal system
  optimally we search .pcr file for needed information
  when this object is initiated...

  how to handle multiple phases?
    shall these be contained within the same Crystal object?
  how to handle magnetic phases?
    ignore
  """
  def __init__(self, phasename, wavelength, a,b,c,alpha,beta,gamma):
    """ is it possible to give this information as a tuple? """
    self.phasename = phasename
    self.wavelength = wavelength
    self.a = float(a)
    self.b = float(b)
    self.c = float(c)
    self.alpha = float(alpha)
    self.beta = float(beta)
    self.gamma = float(gamma)
    self.nb_hkl_values = 999
    self.d = np.empty((self.nb_hkl_values,4)) # keys = hkl (int), value = d (float)
    """ two below lines could be moved to calculate_d """
    calculate_d = self.get_d_function()
    for hkl in range(0,self.nb_hkl_values):
      strhkl = "00" + str(hkl+1)
      strhkl = strhkl[-3:]
      self.d[hkl,0:3] = tuple( int(i) for i in list(strhkl) )
      # print("hkl =",hkl)
      # print("self.d[hkl,0:3] =",self.d[hkl,0:3])
      # print("calculate_d( *tuple(self.d[hkl,0:3]) ) =",calculate_d( *tuple(self.d[hkl,0:3]) ))
      # import pdb; pdb.set_trace();
      self.d[hkl,3] = calculate_d( *tuple(self.d[hkl,0:3]) ) # distances according to crystal system. could be optimized by directly inputting values.
      # import pdb; pdb.set_trace();
      self.d[hkl,3] = self.calculate_two_theta(self.d[hkl,3])

    """ dropping all 2theta entries of NaN """
    self.d = self.d[~np.isnan(self.d)[:,3]]
    """ sorting """
    self.d = self.d[self.d[:,3].argsort()]
    """ unique reflections below 180 degree """
    self.unique = np.unique(self.d[:,3])


    # self.d = np.flipud(self.d)
    # self.d[:,0] = range(0,1000) # all hkl values. needed to remove forbidden reflections & duplicates.

  def get_d_function(self):
    """
    inputs:
      lattice parameter a, b, c
      angles alpha, beta, gamma
    """
    if (self.a == self.b and self.b == self.c and self.alpha == 90, self.beta == 90 and self.gamma == 90):
      return self.cubic_d
    elif (self.a == self.b and self.b != self.c and self.alpha == 90 and self.beta == 90 and self.gamma == 90):
      return self.tetragonal_d
    elif (self.a == self.b and self.alpha == 90 and self.beta == 90 and self.gamma == 120):
      return self.hexagonal_d

  def calculate_two_theta(self, d):
    """ based on Bragg's law
    2d sin theta = n lambda

    we make d a function of hkl
    (which include the higher harmonics corresponding to n != 1)

    2 d sin(theta) = lambda

    asin(lambda / 2 / d) = theta
    """
    try:
      """ something is wrong with radians vs degrees... """
      return asin(self.wavelength / 2 / d) * 360 / pi # returns 2theta.
    except:
      """ lambda / 2 / d > 1, that means 2 theta > 180 which is unphysically. """
      return np.nan





  def cubic_d(self, h,k,l):
    """ remember forbidden reflections on body-centered and face-centered.
    a = b = c
    alpha = beta = gamma = 90deg
    """
    return self.a / (sqrt( h**2 + k**2 + l**2 ))

  def tetragonal_d(self):
    inside = ( (h**2 + k**2) / self.a**2 ) + l**2/self.c**2
    d = sqrt( 1 / inside )

  def hexagonal_d(self, h,k,l):
    inside = 4/3 * (h**2 + h*k + k**2)/ self.a**2 + l**2 / self.c**2
    d = sqrt( 1 / inside )

  def rhombohedral_d(self):
    top = self.a**2 * (1 - 3* cos(self.alpha)**2 + 2 * cos(self.alpha)**3)
    bottom = (h**2 + k**2 + l**2) * sin(self.alpha)**2 + 2*(h*k+k*l+h*l)*(cos(self.alpha)**2 - cos(self.alpha))
    d = math.sqrt( top / bottom )

  def orthorhombic_d(self):
    inside = h**2/self.a**2 + k**2 / self.b**2 + l**2/self.c**2
    d = sqrt( 1 / inside)

  """ other systems include
  monoclinic
  triclinic
  """
# END

if __name__ == "__main__":
  abs_pcr_path = r"C:\AU-PHD\General_Data\Report R1D1\furnaces\Ofurnace\TF10_R1D1 - hematite\_aFe2O3_Fe3O4_.pcr"
  mycrystrals = Crystals(abs_pcr_path)
  import pdb; pdb.set_trace();
