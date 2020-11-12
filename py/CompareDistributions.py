import logging as log
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys

sys.path.append("ComparisonHelp")
import MatchedDistr as MD
sys.path.append("IO")
import CSVMetadataReader as CMR
import SysHelpers as SH
sys.path.append("RKHelp")
import RKDistrMatcher as RDM

# ------------------------------------------------------------------------------

default_label_dict = {
  "costh_Wminus_star" : r"$\cos\theta_{W^-}^{*}$",
  "phi_l_star" : r"$\phi_{l}^{*} [rad]$",
  "costh_l_star" : r"$\cos\theta_{l}^{*}$",
  "costh_Whad_star" : r"$\cos\theta_{W_h}^{*}$",
  "costh_e_star" : r"$\cos\theta_{e}^{*}$",
  "m_enu" : r"$m_{e\nu} [GeV]$"
}

# ------------------------------------------------------------------------------

def single_comparison(csv_path,output_base,label_dict=default_label_dict):
  """ Compare the distribution from a single given CSV file with the 
      corresponding matrix element level one.
  """
  # Read relevant metadata
  metadata_reader = CMR.CSVMetadataReader(csv_path)
  distr_name = metadata_reader.get("Name")
  eM_chirality = metadata_reader.get("e-Chirality")
  eP_chirality = metadata_reader.get("e+Chirality")
  
  # Create the output directory
  output_subdir = "{}_{}_{}".format(distr_name,eM_chirality,eP_chirality)
  output_path = "{}/{}".format(output_base,output_subdir)
  SH.create_dir(output_path)
  
  # Get the MC distribution data
  data = pd.read_csv(csv_path, header=metadata_reader.get_data_header_line()).to_dict()
  
  # Match the RK distribution data
  distr_matcher = RDM.default_distr_matcher()
  data = distr_matcher.get_matched_distrs(distr_name, eM_chirality, eP_chirality, data)
  
  matched_distrs = MD.MatchedDistr(data)
    
  projections = matched_distrs.all_projections()
  for coord, proj in projections.items():
    fig, ax = plt.subplots(tight_layout=True)
    
    x = proj["x"]
    y_MC = proj["MC"]
    y_ME = proj["ME"]
    
    ax.hist(x, weights=y_MC, histtype="step", lw=2, label="MC")
    ax.hist(x, weights=y_ME, histtype="step", lw=2, label="ME")
    
    ax.set_xlabel(label_dict[coord], ha='right', x=1.0)
    ax.set_ylabel(r"$d\sigma$ [fb$^{-1}$]", ha='right', y=1.0)
    
    title = r"""$P_{{e^{{-}}}}=${0}
$P_{{e^{{+}}}}=${1}""".format(eM_chirality, eP_chirality)
    ax.legend(loc=0, title=title)
    fig.savefig("{}/{}.pdf".format(output_path,coord))
    plt.close()


# ------------------------------------------------------------------------------

def main():
  """ Compare all new MC distributions with old ME distributions.
  """
  log.basicConfig(level=log.INFO) # Set logging level

  output_base = "/home/jakob/Documents/DESY/MountPoints/POOLMount/TGCAnalysis/Results/SampleChecks/NewMC/plots"
  
  # --- Compare WW -------------------------------------------------------------
  
  input_base_WW = "/home/jakob/Documents/DESY/MountPoints/DUSTMount/TGCAnalysis/SampleProduction/NewMCProduction/4f_WW_sl/PrEWInput"
  files_WW = ["WW_muplus_250_eLpR.csv", "WW_muplus_250_eRpL.csv", 
              "WW_muminus_250_eLpR.csv", "WW_muminus_250_eRpL.csv"]
  
  for file in files_WW:
    log.info("Looking into file: {}".format(file))
    single_comparison("{}/{}".format(input_base_WW,file),output_base)
  
  # --- Compare single-W -------------------------------------------------------
  
  input_base_singleW = "/home/jakob/Documents/DESY/MountPoints/DUSTMount/TGCAnalysis/SampleProduction/NewMCProduction/4f_sW_sl/PrEWInput"
  files_singleW = ["SingleW_eminus_250_eLpR.csv", "SingleW_eminus_250_eRpL.csv", "SingleW_eminus_250_eRpR.csv",
                   "SingleW_eplus_250_eLpR.csv", "SingleW_eplus_250_eRpL.csv", "SingleW_eplus_250_eLpL.csv"]

  for file in files_singleW:
    log.info("Looking into file: {}".format(file))
    single_comparison("{}/{}".format(input_base_singleW,file),output_base)
  
# ------------------------------------------------------------------------------

if __name__ == "__main__":
  main()
  