# Command line arguments:
#
#     1 - Classifier file path
#     2 - Testing feature matrix
#     3 - Submission file path
from ostsa.classification import load_classifier
from ostsa.storage import create_dirs

import csv
import os

if (len(os.sys.argv) != 4):
    print('Usage:\tpython create_classifier { Classifier File } '\
        + '{ Testing Feature Matrix File } { Submission File Path }')
    os.sys.exit(1)
    
classifier_file = os.sys.argv[1]
testing_features_file = os.sys.argv[2]
submission_file = os.sys.argv[3]

# Load the classifier.
print('Loading Classifier...')
classifier = load_classifier(classifier_file)

# Load the testing feature matrix and ids.
print('Loading testing feature matrix...')
with open(testing_features_file) as file:
    samples = {row[0]: row[1:] for row in csv.reader(file)}

# Generate predictions for each sample.
print('Generating predictions...')
predictions = [[id, *classifier.predict(samples[id])] for id in samples.keys()]

# Create submission file.
print('Creating submission file...')
create_dirs(submission_file)
with open(submission_file, 'w') as file:
    writer = csv.writer(file, lineterminator='\n')
    
    # Write headings.
    writer.writerow(['id', *['Prediction%d' % i for i in range(1, 10)]])
    
    # Write predictions.
    writer.writerows(predictions)
    
print('\nSuccessfully created submission file: %s' % submission_file)
