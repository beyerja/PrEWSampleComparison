from copy import copy
import logging as log
import numpy as np
from tqdm import tqdm

import RKDistrReader as RKDR

# ------------------------------------------------------------------------------

class RKDistrMatcher:
  """ Class that helps match the distribution from Robert Karls matrix element
      level distributions to new distributions (from MC).
  """
  
  MC_to_RK_names = {
    "WW_muminus" : "WW_semilep_MuAntiNu",
    "WW_muplus" : "WW_semilep_AntiMuNu",
    "SingleW_eminus" : "singleWplussemileptonic",
    "SingleW_eplus" : "singleWminussemileptonic"
  }
  
  RK_binning = {
    "WW_semilep_MuAntiNu" : ["costh_Wminus_star","costh_l_star","phi_l_star"],
    "WW_semilep_AntiMuNu" : ["costh_Wminus_star","costh_l_star","phi_l_star"],
    "singleWplussemileptonic" : ["costh_Whad_star", "costh_e_star", "m_enu"],
    "singleWminussemileptonic" : ["costh_Whad_star", "costh_e_star", "m_enu"]
  }
  
  # Sometimes binning is different (without affecting the cross section)
  RK_bin_manipulator = {
    # Roberts WW distribution have a wrong Phi_l^* binning
    "WW_semilep_MuAntiNu" : lambda x: np.array([x[0], x[1], (x[2] - np.pi) * 9.0/10.0]),
    "WW_semilep_AntiMuNu" : lambda x: np.array([x[0], x[1], (x[2] - np.pi) * 9.0/10.0])
  }
  
  def __init__(self, RK_distrs=None):
    self.RK_distrs = [] if (RK_distrs == None) else RK_distrs
      
  def add_RK_file(self, file_path, tree_name):
    """ Use the RK distributions from the tree in the given file.
    """
    for distr in RKDR.RKDistrReader(file_path, tree_name).distrs:
      self.RK_distrs.append(distr)

  def get_distr(self, name):
    """ Return the distribution of the given name.
    """
    found_distrs = []
    for distr in self.RK_distrs:
      if (distr.name == name):
        found_distrs.append(distr)
            
    n_found = len(found_distrs)
    if (n_found == 0):
      raise ValueError("Didn't find distribution {}".format(name))
    elif (n_found > 1):
      raise ValueError("Found more than one distribution {}, found {}".format(name, n_found))
      
    return found_distrs[0]    

  def get_matched_distrs(self, distr_name, eM_chirality, eP_chirality, distr_data):
    """ Add the values from the RK distribution to data for the given 
        distribution.
    """
    if not distr_name in self.MC_to_RK_names:
      log.warning("\tRK distribution not found for {}".format(distr_name))
      return distr_data
    else:
      log.debug("Distribution available, will attemp matching.")
      
    RK_name = self.MC_to_RK_names[distr_name]
    RK_distr = self.get_distr(RK_name)
    RK_coords = copy(RK_distr.bin_centers) # Copy RK bin center array
      
    # See if bins are supposed to be manipulated
    bin_manipulator = False
    if RK_name in self.RK_bin_manipulator:
      log.debug("Got bin manipulator.")
      bin_manipulator = self.RK_bin_manipulator[RK_name]
      RK_coords = np.apply_along_axis(bin_manipulator, axis=1, arr=RK_coords)
      
    # Find the chiral cross section for each bin
    distr_data["RKdistr"] = []
    bin_range = range(len(distr_data["Cross sections"]))
    log.debug("Got {} bins to look for.".format(len(bin_range)))
    for b in tqdm(bin_range, desc="\tMatching RK distr"):
      # Get the (adjusted coordinates) of
      coords = [distr_data["BinCenters:{}".format(coord_name)][b] for coord_name in self.RK_binning[RK_name]]
      
      # Find the correct bin
      index = None
      diff = np.absolute( RK_coords - coords )
      diff_check = np.all(diff < 0.001, axis=1) # Check which coordinates match up
      indices = np.where(diff_check)[0]
      
      # Check if exactly one index was found
      if len(indices) == 0:
        raise ValueError("Didn't find matching bin {} \nAvailable bins : {}".format(coords,RK_coords))
      elif (len(indices) > 1):
        raise ValueError("Found more than one fitting bin for {}: {}".format(coords,[RK_coords[i] for i in indices]))
      else:
        log.debug("Found index for bin {}.".format(b))
        
      index = indices[0]
          
      # Find and add the appropriate chiral cross section
      xsection = None
      if (eM_chirality == -1) and (eP_chirality == +1):
        xsection = RK_distr.xsections_LR[index]
      elif (eM_chirality == +1) and (eP_chirality == -1):
        xsection = RK_distr.xsections_RL[index]
      elif (eM_chirality == -1) and (eP_chirality == -1):
        xsection = RK_distr.xsections_LL[index]
      elif (eM_chirality == +1) and (eP_chirality == +1):
        xsection = RK_distr.xsections_RR[index]
      else:
        raise ValueError("Unknown chiralities {} {}".format(eM_chirality, eP_chirality))
              
      distr_data["RKdistr"].append(xsection)

    return distr_data
        
# ------------------------------------------------------------------------------

def default_distr_matcher():
  """ Get the default distribution matcher that looks in all known RK 
      distributions (at 250 GeV!!!).
  """
  matcher = RKDistrMatcher()
  # matcher.add_RK_file("/afs/desy.de/group/flc/pool/beyerjac/TGCAnalysis/GlobalFit/UnifiedApproach/MinimizationProcessFiles/ROOTfiles/MinimizationProcessesListFile_500_250Full_Elektroweak_menu_2018_04_03.root", "MinimizationProcesses250GeV")
  # matcher.add_RK_file("/nfs/dust/ilc/group/ild/beyerjac/TGCAnalysis/SampleProduction/WW_charge_separated/distributions/combined/Distribution_250GeV_WW_semilep_AntiMuNu.root", "MinimizationProcesses250GeV")
  # matcher.add_RK_file("/nfs/dust/ilc/group/ild/beyerjac/TGCAnalysis/SampleProduction/WW_charge_separated/distributions/combined/Distribution_250GeV_WW_semilep_MuAntiNu.root", "MinimizationProcesses250GeV")
  matcher.add_RK_file("/home/jakob/Documents/DESY/MountPoints/POOLMount/TGCAnalysis/GlobalFit/UnifiedApproach/MinimizationProcessFiles/ROOTfiles/MinimizationProcessesListFile_500_250Full_Elektroweak_menu_2018_04_03.root", "MinimizationProcesses250GeV")
  matcher.add_RK_file("/home/jakob/Documents/DESY/MountPoints/DUSTMount/TGCAnalysis/SampleProduction/WW_charge_separated/distributions/combined/Distribution_250GeV_WW_semilep_AntiMuNu.root", "MinimizationProcesses250GeV")
  matcher.add_RK_file("/home/jakob/Documents/DESY/MountPoints/DUSTMount/TGCAnalysis/SampleProduction/WW_charge_separated/distributions/combined/Distribution_250GeV_WW_semilep_MuAntiNu.root", "MinimizationProcesses250GeV")
  return matcher

# ------------------------------------------------------------------------------