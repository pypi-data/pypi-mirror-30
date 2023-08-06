from sklearn.ensemble import BaggingClassifier
from .Classifier import Classifier

class BaggedClassifier(Classifier):
    """A BaggedClassifier is a type of classifier that implements bagging
    on a given model.
    """

    def __init__(self, model, features, labels, training_ratio=0.7, 
                 bagging_iterations=10):
        """Initialize a new classifier that fits the specified model with
        the specified data and performs the specified number of iterations
        of bagging on the model.
        """
        
        # Wrap the model inside a bagging classifier.
        model = BaggingClassifier(model, bagging_iterations)

        super(BaggedClassifier, self).__init__(model, features, labels, 
                                               training_ratio)