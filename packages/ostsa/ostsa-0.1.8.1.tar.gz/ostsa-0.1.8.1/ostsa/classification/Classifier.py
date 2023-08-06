from ..storage import create_dirs
from sklearn.metrics import accuracy_score, confusion_matrix, log_loss
from sklearn.model_selection import cross_val_score, train_test_split
from sys import version_info

import matplotlib.pyplot as plot
import numpy as np
import pickle

###############################################################################

def load_classifier(filename, classifier_type=None):
    """Load in the classifier from the specified file.
    
    classifier_type should be a class inheriting from Classifier. If specified,
    the classifier will be loaded as that type instead of the type specified
    in the classifier's file.
    """
    
    # Load data from the file.
    with open(filename, 'rb') as file:
        
        # NOTE: There are compatibility issues with Python 2 and 3 when it
        #       comes to numpy arrays. If the classifier was saved in Python 2
        #       and Python 3 is used to load it, an encoding will need to be
        #       specified in order to prevent issues.
        data = pickle.load(file, encoding='latin1') if version_info >= (3, 0) \
                                                    else pickle.load(file)
        
    # If the file was correctly formatted, the data should contain the model,
    # the training data, and the testing data.
    cls = data[0]
    model = data[1]
    
    # Recreate the classifier with the items read in from the file.
    classifier = Classifier(model)
    
    # Modify the type of the classifier if necessary.
    if (classifier_type):
        classifier.__class__ = classifier_type
    else:
        classifier.__class__ = cls
    
    # Load the training and testing data if it is present.
    if (len(data) > 2):
        classifier._training_features = data[2]
        classifier._training_labels = data[3]
        classifier._testing_features = data[4]
        classifier._testing_labels = data[5]
    
    return classifier
    
###############################################################################

class Classifier(object):
    """Classifier is the base class for all types of classifiers. It defines 
    the base logic that all classes should take advantage of. In particular, 
    the base constructor can be used to handle verifying and splitting a passed 
    in data set.
    
    A Classifier takes in a set of labeled data and then allows classifying
    unlabeled data based on what it learned from the passed in labeled data.
    
    All concrete subclasses should implement the model property to return the
    model that should be used for the classification. The Classifier class
    can handle the rest of the logic.
    """
    
    file_extension = '.clsf'
    
    def __init__(self, model, features=None, labels=None, training_ratio=0.7):
        """Initialize a new Model that fits to the specified data.
        
        features is a feature matrix which should be represented by a 2D-array 
        or 2D-array-like object. Each row in the feature matrix represents a 
        sample.
        
        model is the machine learning model that should be used by the
        classifier. If data is specified, the model will be trained with the 
        data. An already trained model can be passed in by specifying no data.
        
        labels is the list of labels that correspond to each sample in the 
        feature matrix. Each element in the list corresponds to a row in the 
        feature matrix. That means that len(features) must equal len(labels).
        
        training_ratio is a float between 0 and 1 that specifies what portion 
        of the data will be used for training. The remaining portion of the 
        data will then be used for testing. The default values is 0.7.
        """
        
        # Set the model.
        self._model = model
        
        # Check if any data was passed in.
        if (features is None):
            return

        # Verify that the number of labels and features is consistent.
        if (len(features) != len(labels)):
            raise ValueError('The numbers of labels and samples are not ' + \
                             'consistent')
            
        # Split the dataset into training and testing data.
        if (training_ratio == 1.0):
            self._training_features = features
            self._training_labels = labels
            self._testing_features = []
            self._testing_labels = []

        else:
            self._training_features, self._testing_features, \
            self._training_labels, self._testing_labels = \
                train_test_split(features, labels, train_size=training_ratio)

        # Train the model with the training set.
        self.model.fit(self.training_features, self.training_labels)
            
    @property
    def model(self):
        """Get the trained model used by the classifier."""
        return self._model
        
    @property
    def testing_features(self):
        """Get the feature matrix used for testing the model. This will be a
        2D-array with the same length as the testing_labels.
        """
        return self._testing_features
        
    @property
    def testing_labels(self):
        """Get the list of labels used for testing the model. This will be a
        list with the same length as the training_features.
        """
        return self._testing_labels
    
    @property
    def training_features(self):
        """Get the feature matrix used for training the model. This will be a
        a 2D-array with the same length as the training_labels.
        """
        return self._training_features
    
    @property
    def training_labels(self):
        """Get the list of labels used for training the model. This will be a
        list with the same length as the training_features.
        """
        return self._training_labels
        
    def accuracy(self, testing_features=None, testing_labels=None):
        """Calculate the accuracy of the classifier by validating against a
        set of labeled test data.
        
        The labeled test data can be passed in. If no testing data is
        specified, the portion of the original data set that was reserved for
        testing will be used instead.
        
        testing_features is the feature matrix for the specified test data.
        This should be 2D-array.
        
        testing_labels is the list of labels for the specified feature matrix.
        This should be a list with the same length as testing_features.
        """
        
        # Ensure either both or neither testing parameters were specified.
        if ((testing_features is None) != (testing_labels is None)):
            raise ValueError("Must specify both testing features and labels")
            
        # Use default testing data if necessary.
        testing_features = testing_features or self.testing_features
        testing_labels = testing_labels or self.testing_labels
        
        # Determine the accuracy of the model.
        predicted = self.model.predict(testing_features)
        return accuracy_score(testing_labels, predicted)
            
    def classify(self, *samples):
        """Classifies the specified samples and returns a predicted label for
        each.
        
        Each sample should be a list of features. The number of features must
        be equal to the number of features each sample passed into the
        classifier used.
        
        A list of classification results for each sample will be returned. If
        only one sample is passed in, the return value will just be the
        classification result for the sample.
        """
            
        # Classify each sample.
        results = self.model.predict(np.array(samples))
        
        # If there is only one sample, just return the result. If there were
        # multiple samples, return the full list.
        return results if len(results) != 1 else results[0]

    def confusion_matrix(self, testing_features=None, testing_labels=None):
        """Calculate the confusion matrix for the classifier based on the
        specified set of labelled test data.

        The labeled test data can be passed in. If no testing data is
        specified, the portion of the original data set that was reserved for
        testing will be used instead.

        testing_features is the feature matrix for the specified test data.
        This should be 2D-array.
        
        testing_labels is the list of labels for the specified feature matrix.
        This should be a list with the same length as testing_features.
        """

        # Ensure either both or neither testing parameters were specified.
        if ((testing_features is None) != (testing_labels is None)):
            raise ValueError("Must specify both testing features and labels")
            
        # Use default testing data if necessary.
        testing_features = testing_features or self.testing_features
        testing_labels = testing_labels or self.testing_labels
        
        # Determine the confusion matrix of the model.
        predicted = self.model.predict(testing_features)
        return confusion_matrix(testing_labels, predicted)

    def cross_val_score(self, testing_features=None, testing_labels=None):
        """Performs Cross Validation on the classifier's model using
        the specified data. If no data is specified, the portion of the 
        original data that was reserved for testing will be used insetad.

        NOTE: This will take a substantially long time to compute. Make sure
              to store the result in a variable when calling.
        """
        # Ensure either both or neither testing parameters were specified.
        if ((testing_features is None) != (testing_labels is None)):
            raise ValueError("Must specify both testing features and labels")
            
        # Use default testing data if necessary.
        testing_features = testing_features or (self.training_features \
                                                + self.testing_features)
        testing_labels = testing_labels or (self.training_labels \
                                            + self.testing_labels)
        
        # Find the cross validation score for the model.
        return cross_val_score(self.model, testing_features, testing_labels)

    def logloss(self, testing_features=None, testing_labels=None, 
                labels=None):
        """Calculate the logloss of the classifier by validating against a
        set of labeled test data.
        
        The labeled test data can be passed in. If no testing data is
        specified, the portion of the original data set that was reserved for
        testing will be used instead.

	  It is best to specify the list of labels through the labels parameter
        to ensure an accurate result.
        
        testing_features is the feature matrix for the specified test data.
        This should be 2D-array.
        
        testing_labels is the list of labels for the specified feature matrix.
        This should be a list with the same length as testing_features.
        """
        
        # Ensure either both or neither testing parameters were specified.
        if ((testing_features is None) != (testing_labels is None)):
            raise ValueError("Must specify both testing features and labels")
            
        # Use default testing data if necessary.
        testing_features = testing_features or self.testing_features
        testing_labels = testing_labels or self.testing_labels
        
        # Determine the logloss of the model.
        predicted = self.model.predict_proba(testing_features)
        return log_loss(testing_labels, predicted, labels=labels)
        
    def predict(self, *samples):
        """Calculate the probabilities of each of the specified samples
        belonging to each of the classes.
        
        For each sample, a list of percentages is returned. Each percentage
        represents the confidence interval for the corresponding class.
        """
        
        # Predict the probabilities for each sample.
        probabilities = self.model.predict_proba(samples)
        
        # If there is only one sample, just return the result. If there were
        # multiple samples, return the full list.
        return probabilities if len(probabilities) != 1 else probabilities[0]


    def save(self, filename, include_data=True):
        """Save the classifier to a file to be loaded back in later.
        
        The classifier will be saved to a file with the specified name. The
        file extension for the file name will be automatically added by the
        method. 
        
        The classifier can be loaded back in using the load_classifier 
        function.
        
        The classifier file will contain the following items in the specified
        order:
            
            1. Classifier Type
            2. Trained Model
            3. Classifier Training Data (feature matrix followed by labels)
            4. Classifier Testing Data (feature matrix followed by labels)
        
        These items will be saved into a list, and the list will be saved into
        the file.
        
        If include_data is set to false, the training and testing data will
        not be included in the saved file.
        """
        
        # Append the file extension to the file name.
        filename += Classifier.file_extension
        
        # Ensure the directory for the file exists.
        create_dirs(filename)
        
        # Save all of the data to the file.
        data = [self.__class__, self.model]
        
        if (include_data):
            data += [self.training_features, self.training_labels, 
                     self.testing_features, self.testing_labels]
        
        with open(filename, 'wb') as file:
            pickle.dump(data, file, protocol=2)
            
    def save_confusion_matrix(self, filename, class_labels=None, 
                              cmap=plot.cm.Blues):
        """Create an image to display the classifier's confusion matrix and 
        save it to the specified file. The image type will be png. The
        extension will automatically be added.
        
        class_labels is an array of all of the labels that will be used to
        mark the classes. A list of strings can be specified. If no labels
        are specified, numbers will be used.
        
        cmap is the color scheme to be used for the cmap. The Blues color
        scheme is the default. More can be found in the 
        matplotlib.pyplot.cm module.
        """
        
        # Retrieve the confusion matrix.
        matrix = self.confusion_matrix()
        
        # Create a normalized version of the matrix.
        normalized = [[float(x) / float(sum(row)) for x in row] 
                      for row in matrix]
        
        # Add total columns and rows with 
        
        # Create the matrix plot.
        plot.clf()
        figure = plot.figure()
        matrix_plot = figure.add_subplot(111)
        matrix_plot.set_aspect(1)
        
        # Axis Labels
        plot.xlabel('Predicted')
        plot.ylabel('Actual')
        
        # X-Axis on top
        matrix_plot.xaxis.tick_top()
        matrix_plot.xaxis.set_label_position('top')
        
        # No tick marks.
        matrix_plot.tick_params(axis='both', which='both', length=0)
        
        # Use colors to represent normalized values.
        matrix_plot.imshow(np.array(normalized), cmap,
                           interpolation='nearest')
        
        # Set the label for each cell.
        width, height = matrix.shape
        for x in range(width):
            for y in range(height):
                # Use white text for darker shades.
                color = 'w' if normalized[x][y] > 0.7 else 'k'
                matrix_plot.annotate(str(matrix[x][y]), xy=(y, x),
                                     horizontalalignment='center',
                                     verticalalignment='center',
                                     color=color)
                
        # Set the tick mark labels.
        class_labels = class_labels or \
                       [str(i) for i in range(1, width+1)]
        plot.xticks(range(width), class_labels)
        plot.yticks(range(height), class_labels)
        
        # Rotate X-Axis labels if any class label is more than 3 chars.
        if (any(len(class_label) > 3 for class_label in class_labels)):
            xlabels = matrix_plot.xaxis.get_majorticklabels()
            matrix_plot.set_xticklabels(xlabels, rotation=45)
        
        # Save the plot.
        filename += '.png'
        plot.tight_layout()
        plot.savefig(filename, format='png')
            