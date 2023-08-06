# Command Line Arguments:
#
#     1 - Database file path
#     2 - Feature Matrix file path

import os
from ostsa.exe.storage import ExeKaggleSample
from ostsa.storage import SampleDao

if (len(os.sys.argv) != 3):
    print('Usage:\tpython save_feature_matrix.py { Database Path } ' +\
          '{ Feature Matrix File }')
    os.sys.exit(1)
    
database_path = os.sys.argv[1]
feature_matrix_file = os.sys.argv[2]

dao = SampleDao(ExeKaggleSample, database_path)

print('Saving feature matrix...')
dao.save_feature_matrix(feature_matrix_file, include_ids=True)
print('Feature matrix successfully saved to %s' % feature_matrix_file)
