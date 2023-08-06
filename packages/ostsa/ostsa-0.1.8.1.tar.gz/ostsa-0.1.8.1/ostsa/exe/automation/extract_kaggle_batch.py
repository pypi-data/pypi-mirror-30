from . import get_kaggle_sample_names
from ..storage import ExeKaggleSample
from ...automation import extract_batch

import os

###############################################################################

def extract_kaggle_batch(directory, database_file_path, log_file_path=None, 
                         verbose=True, update_features=None):
    """Extracts all of the exe samples found in the specified directory and
    stores them in the specified database.
    
    directory should be a folder directory that contains sets of Kaggle
    .exe samples.
    
    database_file_path should be a path to the database file to store all of
    the Kaggle samples in.
    
    log_file_path is an optional path to a log file where the output of the
    batch operation should be written. The log will be appended to, so the
    original contents of the file will not be lost.
    
    If verbose is true, all of the logged output will be logged to stdout as
    well.
    
    if skip_duplicates is true, any duplicate sample names will be skipped
    instead of updated.
    """
    
    # Ensure the directory exists.
    if (not os.path.isdir(directory)):
        raise ValueError('Could not find directory %s' % directory)
        
    # Retrieve all of the sample names in the directory.
    sample_names = get_kaggle_sample_names(directory)
    
    # Construct a list of kaggle samples.
    samples = []
    for sample_name in sample_names:
        
        # Construct the names of the files.
        hex_file_name = os.path.join(directory, sample_name + '.bytes')
        asm_file_name = os.path.join(directory, sample_name + '.asm')
        
        # Construct the sample.
        sample = ExeKaggleSample(hex_file_name, asm_file_name)
        samples.append(sample)
        
    # Extract features from all of the samples.
    extract_batch(ExeKaggleSample, samples, database_file_path, 
                  log_file_path=log_file_path, verbose=verbose, 
                  update_features=update_features)