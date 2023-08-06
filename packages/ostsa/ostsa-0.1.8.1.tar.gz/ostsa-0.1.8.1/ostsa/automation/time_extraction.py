import time

from ..storage import create_dirs

###############################################################################

def time_extraction(sample, log_file_path=None, verbose=True, optimized=False):
    """Time how long it takes to extract each of the features from the
    specified sample.
    
    The sample should be a Sample-like object that defines one or several
    feature methods to time.
    
    log_file_path is the optional path to the log file that the results of the
    test should be saved to. The log will be appended to the document, so the 
    contents of the log will not be overwrittern. If this file does not exist,
    it will be created.
    
    If verbose is set to true, the status of the feature parsing will be
    written to stdout. It is turned off by default.
    
    If optimized is set to true, the optimize method of the sample will be
    called before extracting the features from the sample. The optimization
    itself will be timed and included in the results.
    """
    
    def write(text=''):
        """Write the specified text to stdout or the log file depending on
        the settings.
        """
        
        # Stdout
        if (verbose):
            print(text)
            
        # Log file
        if (log_file_path):
            log_file.write(text + '\n')
            
    def print_time(label, time):
        """Print the time with a label in the universal format."""
        write('\t{0:>30}{1:.>30.4f} seconds'.format(label, time))
            
    def time_function(label, function):
        """Time the specified function and print the results. Return the
        resulting time.
        """
        
        # Time
        start = time.clock()
        function()
        elapsed = time.clock() - start
        
        # Print
        print_time(label, elapsed)
        
        # Return
        return elapsed
            
    # Optional: Create the log file.
    if (log_file_path):
        create_dirs(log_file_path)
        log_file = open(log_file_path, 'a')
        
    # Print header.
    write('Timing feature extraction for the sample: {0}\n'.format(
                                                            sample.identifier))
    
    # Optional: Perform optimization.
    if (optimized):
        optimize_time = time_function('Optimization', sample.optimize)
        write()    # Extra endline.
        
    # Time each feature.
    total_time = sum(time_function(f[0], lambda: f[1](sample)) for f 
                                                   in sample.feature_methods())
    # Print divier.
    write('\t' + '-' * 78)
    
    # Print total time.
    print_time('Total Time', total_time)
    
    # Optional: Add optimization time.
    if (optimized):
        print_time('...including optimization', total_time + optimize_time)
        
    # Optional: Close log file.
    if (log_file_path):
        log_file.close()