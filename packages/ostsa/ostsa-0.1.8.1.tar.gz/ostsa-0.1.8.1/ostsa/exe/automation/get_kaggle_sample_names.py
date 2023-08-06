import os

###############################################################################

def get_kaggle_sample_names(directory):
    """Return all of the samples in the specified directory.
    
    A sample is considered in the directory if there exists both a .bytes file
    and a .asm file with the sample's name.
    
    The list returned will contain only the names of all of the samples. The
    names will not contain file extensions or the directory.
    
    The list will be sorted alphabetically.
    """
    
    # Retrieve all of the files in the directory.
    files = set(os.listdir(directory))
    
    # Each sample should have 1) a .bytes file and 2) a .asm file. Both files
    # should have the same name minus the extension. This name should be the md5
    # hash that is used to uniquely identify the file. In order to retrieve all
    # of the potential hashes in the directory, we can remove all of the file
    # extensions and filter out duplicate names.
    names = set(os.path.splitext(file)[0] for file in files)
    
    # Ensure each unique name has both an associated .bytes and associated
    # .asm file.
    names = list(name for name in names if ('%s.bytes' % name) in files 
                                        and ('%s.asm' % name) in files)
    
    # Sort the names alphabetically.
    names.sort()
    
    return names