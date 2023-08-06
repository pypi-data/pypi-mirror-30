from ..storage import ExeRawSample
from ...classification import BaggedClassifier

###############################################################################

class ExeClassifier(BaggedClassifier):
    """An ExeClassifier is a classifier that can classify Windows Executable
    files. 
    
    All ExeClassifiers make use of the ensemble bagging technique.
    """
    
    def __init__(self, model, features=None, labels=None, training_ratio=0.7, 
                 bagging_iterations=10):
        """Initialize a new exe classifier that fits the specified model to 
        the specified data.
        
        model is the Sciki-Learn model to train.
        
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
        super(ExeClassifier, self).__init__(model, features, labels, 
                                            training_ratio, bagging_iterations)
                                            
    def classify_exe(self, exe_file_name):
        """Classifies the specified Windows Executable (.exe) file."""
        
        # Extract all of the features from the executable file.
        with ExeRawSample(exe_file_name) as sample:
            sample.optimize()
            features = sample.features()
            
        return self.classify(features)