from . import ExeClassifier

import xgboost as xgb

###############################################################################

class XGBClassifier(ExeClassifier):
    """The ExeXGBClassifier is a classifier for Windows Executable Files that
    uses XGBoost as the model.
    
    Note that in order for this class to be used, XGBoost will need to be
    installed. Unfortunately, this is not as simple as running a pip command
    in Windows. If you are running Windows and need to install XGBoost, take
    the following steps:
        
        1. Clone the XGBoost repository locally. The repository contains
           submodules, so you will need to do a recursive clone. You can use
           the following git command:
               
               git clone --recursive https://github.com/dmlc/xgboost
        
        2. Download the "libxgboost.dll" file from PicNet:
            
                http://www.picnet.com.au/blogs/guido/post/2016/09/22/xgboost-windows-x64-binaries-for-download/
           
           The most recent build at the time of writing and the one currently
           used is 20170106. If there are any compatibility issues, download
           this version if possible.
           
        3. In the directory you cloned the repository into, navigate to:
            
                xgboost/python-package/xgboost
                
           Paste the "libxgboost.dll" file you downloaded in this folder.
           
        4. Open a command window in the directory above the one containing the 
           dll and run the following command:
               
               python setup.py develop --user

           This will only install XGBoost for the current user, so it should
           not need Admin permissions.
           
    If these steps do not work for you, try the official installation guide:
        
        https://xgboost.readthedocs.io/en/latest/build.html
    """
           
    def __init__(self, features=None, labels=None, training_ratio=0.7, 
                 bagging_iterations=10, **kwargs):
        """Initialize a new classifier that fits to the specified data.
        
        features is a feature matrix and should be a 2D list-like structure.
        
        labels is the list of labels and should have the same number of
        elements as the feature matrix has rows.
        
        training_ratio is a value between 0 and 1 that defines the ratio of
        the given data that will be used for training. The rest will be used
        for testing. The default is 0.7.
        """
        
        model = xgb.XGBClassifier(**kwargs)        
        super(XGBClassifier, self).__init__(model, features, labels,
                                            training_ratio, 
                                            bagging_iterations)
