import logging as log
import numpy as np

# ------------------------------------------------------------------------------

class MatchedDistr:
  """ Class that hold and can analyse the matched distributions (MC one and 
      matrix element one from RK).
  """
  
  def __init__(self, data):
    # Find the distributions
    MC_vals_dict = data["Cross sections"]
    self.MC_distr = np.array([MC_vals_dict[b] for b in range(len(MC_vals_dict))])
    self.ME_distr = np.array(data["RKdistr"])
    
    # Find the bin centers
    self.bin_centers = {} # search for BinCenters: and transform into np array -> Easy projection
    self.find_bin_centers(data)
  
  # --- Access functions -------------------------------------------------------
  
  def projection(self, coord):
    """ Return the projection of both the Monte Carlo and the matrix element 
        distributions along the given coordinate.
    """
    
    # Find bin center keys that fit the given coordinate
    avail_keys = self.bin_centers.keys()
    keys = [key for key in self.bin_centers.keys() if coord in key]
    
    # Check if exactly one key was found
    if len(keys) == 0:
      raise ValueError("Didn't find matching key for {} \nAvailable keys : {}".format(coord,avail_keys))
    elif (len(keys) > 1):
      raise ValueError("Found more than one fitting key for {}: {}".format(coord,keys))
    else:
      log.debug("Found key for bin {}.".format(coord))
      
    # Bin centers in this direction
    bin_centers = self.bin_centers[keys[0]]
    
    # Find all unique values (within 0.001 uncertainty)
    rounded_bin_centers = np.around(bin_centers, decimals=3)
    unique_bin_centers = np.unique(rounded_bin_centers)
    
    # Find the projection
    projection = {"x" : [], "MC" : [], "ME" : []}
    for x in unique_bin_centers:
      projection["x"].append(x)
      
      matching_bins = np.where( np.abs(bin_centers - x) < 0.001 )
      projection["MC"].append(np.sum( self.MC_distr[matching_bins]) )
      projection["ME"].append(np.sum( self.ME_distr[matching_bins]) )
    
    return projection
    
  def all_projections(self):
    """ Return all projections along all possible coordinates.
    """
    projections = {}
    for coord in self.bin_centers:
      proj_label = coord.split(":")[1].strip()
      projections[proj_label] = self.projection(proj_label)
    return projections
    
  def integral(self):
    """ Return the integrals for MC and ME.
    """
    integrals = {
      "MC": np.sum(self.MC_distr),
      "ME": np.sum(self.ME_distr)
    }
    return integrals
    
  # --- Internal functions -----------------------------------------------------
  
  def find_bin_centers(self, data):
    """ Find the bin centers in the given data.
    """
    for key, val_arr in data.items():
      if "BinCenters:" in key:
        
        self.bin_centers[key] = np.array([val_arr[b] for b in range(len(val_arr))])

# ------------------------------------------------------------------------------