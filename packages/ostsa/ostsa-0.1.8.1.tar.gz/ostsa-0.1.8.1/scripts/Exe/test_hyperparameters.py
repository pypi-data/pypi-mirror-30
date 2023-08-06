# Command line arguments:
#
#     1 - Training feature matrix file
#     2 - Sample labels file path
#     3 - Results file name
from ostsa.automation import hyperparameter_grid_search
from ostsa.exe.classification import XGBClassifier
import csv
import os

if __name__ == '__main__':
    if (len(os.sys.argv) != 4):
        print('Invalid number of arguments: %d' % len(os.sys.argv))
        os.sys.exit(1)
        
    feature_matrix_file = os.sys.argv[1]
    sample_labels_file = os.sys.argv[2]
    results_file = os.sys.argv[3]
    
    # Load in the feature matrix and ids.
    print('Loading features...')
    with open(feature_matrix_file) as file:
        rows = [row for row in csv.reader(file)]
        
        ids = [row[0] for row in rows]
        features = [row[1:] for row in rows]
        
    # Load in the labels.
    print('Loading labels...')
    with open(sample_labels_file) as file:
        rows = [row for row in csv.reader(file)]
        labels_dict = {row[0]: row[1] for row in rows[1:]}
        
    labels = [labels_dict[id] for id in ids]
    
    # Perform the hyperparameter grid search.
    print('Performing hyperparameter grid search...')
    hyperparameter_grid_search(XGBClassifier, features, labels, results_file,
                               learning_rate=[0.01, 0.1, 0.2],
                               max_depth=[3, 9],
                               min_child_weight=[0.5, 1.5],
                               gamma=[0, 0.1],
                               subsample=[0.5, 1])
