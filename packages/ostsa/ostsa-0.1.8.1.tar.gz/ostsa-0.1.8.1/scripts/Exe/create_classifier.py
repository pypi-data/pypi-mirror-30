# Command line arguments:
#
#    1 - Training feature matrix file path
#    2 - Sample labels file path
#    3 - Classifier file path
#    4 - Feature Matrix + Labels File Path
from ostsa.exe.classification import XGBClassifier
import csv
import os

if (len(os.sys.argv) != 5):
    print('Usage:\tpython create_classifier { Training Feature Matrix File } '
          '{ Training Labels File } { Classifier File Path } '
          ' { Labelled Feature Matrix File }')
    os.sys.exit(1)
        
feature_matrix_file = os.sys.argv[1]
sample_labels_file = os.sys.argv[2]
classifier_file = os.sys.argv[3]
labelled_features_file = os.sys.argv[4]

# Load in the feature matrix and ids.
print('Loading features...')
with open(feature_matrix_file) as file:
    rows = [row for row in csv.reader(file)]
    
    ids = [row[0] for row in rows]
    features = [row[1:] for row in rows]
    
# Load in the labels.
print('Loading labels...')
with open(sample_labels_file) as file:
    label_rows = [row for row in csv.reader(file)]
    labels_dict = {row[0]: row[1] for row in label_rows[1:]}
    
labels = [labels_dict[id] for id in ids]

# Create the classifier.
print('Training classifier...')
classifier = XGBClassifier(features, labels, training_ratio=1,
                           gamma=0,
                           max_depth=3,
                           subsample=1,
                           min_child_weight=0.5,
                           learning_rate=0.2)

# Save the classifier.
print('Saving classifier...')
classifier.save(classifier_file, include_data=False)

# Combine the feature matrix and labels.
print('Combining feature matrix and labels...')

labelled_rows = [row + [label] for row, label in zip(rows, labels)]
with open(labelled_features_file, 'w') as file:
    writer = csv.writer(file, lineterminator='\n').writerows(labelled_rows)

print('\nSuccessfully created classifier file: %s' % classifier_file)
