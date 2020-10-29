import ROOT
import cppyy
import numpy as np

# ------------------------------------------------------------------------------

""" Classes needed to read the distribution files provided by Robert Karl.
"""

# ------------------------------------------------------------------------------

class RKDistr:
  """ Class describing a distribution created by Robert Karl.
  """

  def __init__(self):
    self.name = ""
    self.bin_centers = []
    
    self.xsections_LR = []
    self.xsections_RL = []
    self.xsections_LL = []
    self.xsections_RR = []

# ------------------------------------------------------------------------------

class RKDistrReader:
    """ Class that can read the distributions (cross sections, bins) that are 
        stored in files created by Robert Karl (or in his style).
    """
    
    def __init__(self, file_path, tree_name):
        self.distrs = []
        
        # Read the distributions form the file
        file = ROOT.TFile(file_path)
        tree = file.Get(tree_name)
        self.read_distrs(tree)
        file.Close()
        
    def read_distrs(self, tree):
        """ Read all the distributions from the given file
        """
        tree.GetEntry(0)
        for entry in tree:         
            # Each entry is a distribution
            distr = RKDistr()
            
            # Extract all the distribution quantities from the tree
            distr.name = str(entry.describtion)
            
            n_rows = entry.angular_center.GetNrows()
            n_cols = entry.angular_center.GetNcols()
            if (distr.name in ["Zhadronic", "Zleptonic"]):
              n_cols = 1 # This is stored falsly in the TTree
            
            distr.bin_centers = np.array([[float(entry.angular_center[row][col]) for col in range(n_cols)] for row in range(n_rows)])
            
            distr.xsections_LR = np.array([float(xsection) for xsection in entry.differential_sigma_LR])
            distr.xsections_RL = np.array([float(xsection) for xsection in entry.differential_sigma_RL])
            distr.xsections_LL = np.array([float(xsection) for xsection in entry.differential_sigma_LL])
            distr.xsections_RR = np.array([float(xsection) for xsection in entry.differential_sigma_RR])
            
            self.distrs.append(distr)
            
    def get_distr(self, name):
        """ Return the distribution of the given name.
        """
        found_distrs = []
        for distr in self.distrs:
            if (distr.name == name):
                found_distrs.append(distr)
                
        n_found = len(found_distrs)
        if (n_found == 0):
            raise ValueError("Didn't find distribution {}".format(name))
        elif (n_found > 1):
            raise ValueError("Found more than one distribution {}, found {}".format(name, n_found))
          
        return found_distrs[0]

# ------------------------------------------------------------------------------