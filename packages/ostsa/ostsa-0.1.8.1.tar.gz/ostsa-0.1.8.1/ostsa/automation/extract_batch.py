import sys
import time

from ..storage import create_dirs, SampleDao

###############################################################################

def extract_batch(sample_type, samples, database_file_path, 
                  log_file_path=None, verbose=True, update_features=None):
    """Parse the specified list of samples and store them in the specified
    database file.
    
    sample_type should be the type of the samples that should be stored in the
    database.
    
    samples should be a list of the Sample objects that should be stored in
    the database. All samples in the list should be of the sample type.
    
    database_file_path should be the path to the database where the samples
    should be stored. If the database file does not exist, it will be
    created.
    
    log_file_path is the optional path to the log file that the status of
    the feature parsing should be saved to. The log file will be appended
    to the document, so the contents of the log will not be overwrittern.
    If this file does not exist, it will be created.
    
    If verbose is set to true, the status of the feature parsing will be
    written to stdout. It is turned off by default.
    
    update_features is the list of features that should be updated for any
    sample that is already contained in the database. If this is none or an
    empty list, duplicates will be skipped. If this is simply the string '*',
    then any missing features will be filled in for duplicates. If this is the
    string 'ALL', all features will be updated for duplicates. Otherwise,
    this should be a list containing strings representing feature names for the
    features to be updated.
    """
    
    def write(text):
        """Writes the specified text to stdout or the log file depending on
        the settings.
        """
        
        # Stdout
        if (verbose):
            sys.stdout.write(text)
            sys.stdout.flush()
            
        # Log file
        if (log_file_path):
            log_file.write(text)
            
    # Ensure valid value for update_features.
    if (update_features == 'ALL'):
        update_features = [f[0] for f in sample_type.feature_methods()]
                           
    valid = isinstance(update_features, (list, tuple)) or \
            update_features == '*' or \
            update_features is None
    if (not valid):
        raise ValueError('Invalid value for update_features: %s' 
                         % str(update_features))
    
    # Create the log file.
    if (log_file_path):
        create_dirs(log_file_path)
        log_file = open(log_file_path, 'a')
        
    # Ensure samples were passed in.
    if (not samples):
        write('No samples found.')
        return
        
    # Log all of the samples passed in.
    samples_log = 'Found {0} samples:\n\t'.format(len(samples))
    samples_log += '\n\t'.join(sample.identifier for sample in samples)
    samples_log += '\n\n'
    write(samples_log)
        
    # Create a dao for the type of the samples.
    dao = SampleDao(sample_type, database_file_path)
    
    # Track how long the parsing takes.
    total_start = time.clock()
    
    # Track which samples were added, which already existed in the database,
    # and which samples caused an error while extracting.
    added_samples    = []
    error_samples    = []
    existing_samples = []
    
    # Add each sample to the database.
    for sample in samples:
        
        # Skip the sample if it is already in the database and the option to
        # skip duplicates is set.
        existing = dao.exists(sample.identifier)
        if (existing and not update_features):
            existing_samples.append(sample)
            write('{0} is already in database. Skipping...\n\n'.format(
                                                            sample.identifier))
            continue
        
        # Log sample start.
        write('Extracting features from {0}...\n'.format(sample.identifier))
        start = time.clock()
        
        # Add or update sample.
        try:
            sample.optimize()
            if (existing):
                features = None if update_features == '*' else update_features
                dao.update_sample(sample, features, verbose_callback=write)
            else:
                dao.add_sample(sample, verbose_callback=write)
            sample.cleanup()
            
        # Catch any errors that may have occurred due to the feature 
        # extraction. These would likely be caused by a derived Sample class.
        except Exception as e:
            
            # Log exception.
            write(str(e) + '\n\n')
            
            # Add to the list of errored samples.
            error_samples.append(sample)
            
        # If the sample extracted successfully, log the end of the sample.
        else:
            
             # Log sample end.
            elapsed = time.clock() - start / 1000
            write('Finished extraction in {0:.5} seconds.\n\n'.format(elapsed))
            
            # Add the sample to the appropriate list.
            if (existing):
                existing_samples.append(sample)
                
            else:
                added_samples.append(sample)
                
    # Close the database.
    dao.close()
                
    # Log the results of the extraction.
    if (added_samples):
        added_text = 'Added {0} samples:\n\t'.format(len(added_samples))
        added_text += '\n\t'.join(sample.identifier for sample
                                                    in added_samples)
        added_text += '\n\n'
        write(added_text)
        
    if (existing_samples):
        action = 'Skipped' if not update_features else 'Updated'
        existing_text = '{0} {1} samples:\n\t'.format(action, 
                                                      len(existing_samples))
        existing_text += '\n\t'.join(sample.identifier for sample 
                                                       in existing_samples)
        existing_text += '\n\n'
        write(existing_text)
        
    if (error_samples):
        error_text = 'Encountered errors with {0} samples:\n\t'.format(
                                                            len(error_samples))
        error_text += '\n\t'.join(sample.identifier for sample 
                                                    in error_samples)
        error_text += '\n\n'
        write(error_text)
        
    # Log the amount of time the entire process took.
    total_elapsed = time.clock() - total_start
    write('Finished in {0:.5} seconds.\n\n'.format(total_elapsed))
    
    # Close the log file.
    if (log_file_path):
        log_file.close()
