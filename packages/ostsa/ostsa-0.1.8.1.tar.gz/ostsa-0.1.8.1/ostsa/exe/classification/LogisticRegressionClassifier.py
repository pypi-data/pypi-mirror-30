from . import ExeClassifier
from sklearn.linear_model import LogisticRegression

###############################################################################

class LogisticRegressionClassifier(ExeClassifier):
    """The ExeLogisticRegressionClassifier is a classifier for Windows
    Executable Files that uses the Logistic Regression model combined with
    bagging.
    """
    
    def __init__(self, features=None, labels=None, training_ratio=0.7, 
                 bagging_iterations=10):
        """Initialize a new classifier that fits to the specified data.
        
        features is a feature matrix and should be a 2D list-like structure.
        
        labels is the list of labels and should have the same number of
        elements as the feature matrix has rows.
        
        training_ratio is a value between 0 and 1 that defines the ratio of
        the given data that will be used for training. The rest will be used
        for testing. The default is 0.7.
        
        bagging_iterations is the number of bagging iterations that will be
        performed. More iterations means longer training times but can in
        theory lead to better results. The default is 10, which is the
        generally recommended value.
        """
        
        model = LogisticRegression()        
        super(LogisticRegressionClassifier, self).__init__(model, features, 
                                                           labels, 
                                                           training_ratio,
                                                           bagging_iterations)




