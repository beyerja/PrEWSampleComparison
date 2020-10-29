import logging as log

# ------------------------------------------------------------------------------

class CSVMetadataReader:
  """ Class to read the metadata from the top of an CSV file.
  """
  begin_marker = "#BEGIN-METADATA"
  end_marker = "#END-METADATA"

  def __init__(self, csv_path):
    self.metadata_lines = []
    self.metadata = {}
    self.data_header_line = None
    
    self.find_metadata_lines(csv_path)
    self.interpret_metadata_lines()

  # --- Access functions -------------------------------------------------------

  def get(self, metadata_ID):
    """ Return the read value for the given metadata ID.
    """
    return self.metadata[metadata_ID]
      
  def get_data_header_line(self):
    """ Get the line index at which the actual CSV data starts.
    """
    return self.data_header_line

  # --- Internal functions -----------------------------------------------------
    
  def find_metadata_lines(self, csv_path):
    """ Find the lines in the given file that correspond to the metadata.
    """
    # Look line by line
    line_index = 0
    in_metadata = False 
    with open(csv_path, 'r') as read_obj:
      # Check line by line
      for line in read_obj:
        line_index += 1
        line = line.strip() # Remove trailing/leading whitespaces etc.
        if self.end_marker in line:
          break
        elif self.begin_marker in line:
          in_metadata = True
        elif in_metadata:
          self.metadata_lines.append(line)
        else:
          raise ValueError("Unexpected line before CSV Metadata: {}".format(line))
          
      
    self.data_header_line = line_index
    
  def interpret_metadata_lines(self):
    """ Interpret the metadata lines found in the CSV file.
    """
    # Split each line by the ":" separator and store its value
    for line in self.metadata_lines:
      log.debug("Interpreting line: {}".format(line))
      ID, value = line.split(":")
      value = value.strip() # Remove trailing/leading whitespaces etc.
      
      if (ID == "Energy") or (ID == "e-Chirality") or (ID == "e+Chirality"):
        value = int(float(value))
    
      self.metadata[ID] = value
    
# ------------------------------------------------------------------------------

def test():
  """ Test the metadata reader.
  """
  log.basicConfig(level=log.DEBUG) # Set logging level
  test_file = "/home/jakob/Documents/DESY/MountPoints/DUSTMount/TGCAnalysis/SampleProduction/NewMCProduction/4f_WW_sl/PrEWInput/WW_muplus_250_eLpR.csv"
  metadata_reader = CSVMetadataReader(test_file)
  log.info(metadata_reader.get("Energy"))
  log.info(metadata_reader.get("e-Chirality"))
  log.info(metadata_reader.get("e+Chirality"))
  log.info(metadata_reader.get_data_header_line())

if __name__ == "__main__":
  """ If this script is called directly perform the test function.
  """
  test()

# ------------------------------------------------------------------------------
