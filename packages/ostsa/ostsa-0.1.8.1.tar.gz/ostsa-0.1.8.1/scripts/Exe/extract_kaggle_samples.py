# Command line arguments:
#
#   1 - Sample directory path
#   2 - Database file path
#   3 - Log file path
from ostsa.exe.automation import extract_kaggle_batch
import os

if (len(os.sys.argv) != 4):
    print('Usage:\tpython extract_kaggle_samples.py { Sample Directory } ' +\
          '{ Database Path } { Log File Path }')
    os.sys.exit(1)
    
sample_directory = os.sys.argv[1]
database_path = os.sys.argv[2]
log_file_path = os.sys.argv[3]

extract_kaggle_batch(sample_directory, database_path, 
                     log_file_path=log_file_path, update_features='*')
