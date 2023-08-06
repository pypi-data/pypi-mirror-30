# Command line arguments:
#
#     1 - Training feature matrix file path
#     2 - Sample labels file path
#     3 - Classifier File Path
#     4 - Confusion Matrix File Path
#     5 - Scoresheet File Path
from ostsa.exe.classification import XGBClassifier
import csv
import os

if (len(os.sys.argv) != 6):
    print('Invalid number of args. Check python script.')
    os.sys.exit(1)

feature_matrix_file = os.sys.argv[1]
sample_labels_file = os.sys.argv[2]
classifier_file = os.sys.argv[3]
confusion_matrix_file = os.sys.argv[4]
scoresheet_file = os.sys.argv[5]

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

# Create the classifier.
print('Training classifier...')
classifier = XGBClassifier(features, labels, training_ratio=0.7)

# Save the classifier.
print('Saving classifier...')
classifier.save(classifier_file)

# Create the confusion matrix.
print('Creating confusion matrix...')
classifier.save_confusion_matrix(confusion_matrix_file)

# Calculate accuracy.
print('Calculating accuracy...')
accuracy = classifier.accuracy()
with open(scoresheet_file, 'w') as file:
    file.write('{0:<30}{1}'.format('Accuracy:', accuracy))
    
# Calculate logloss.
print('Calculating log loss...')
logloss = classifier.logloss()
with open(scoresheet_file, 'a') as file:
    file.write('\r\n{0:<30}{1}'.format('Log loss:', logloss))
    
# Calculate cross validation.
print('Cross validating (this will take a while)...')
cross_vals = classifier.cross_val_scores()
average = sum(cross_vals) / float(len(cross_vals))
with open(scoresheet_file, 'a') as file:
    file.write('\r\n{0}-Fold Cross Validation:'.format(len(cross_vals)))
    file.write('\r\n'.join('{0}{1}'.format(' ' * 30, x) for x in cross_vals))
    file.write((' ' * 30) + ('-' * 17))
    file.write('{0}{1}', (' ' * 30) + str(average))
    
print('\nSuccessfully evaluated classifier!')

