from ..parsing import memoize

###############################################################################

__families = ['Ramnit', 'Lollipop', 'Kelihos_ver3', 'Vundo', 'Simda',
              'Tracur', 'Kelihos_ver1', 'Obfuscator.ACY', 'Gatak']

@memoize
def __classifier():
    from ..classification import load_classifier
    import inspect
    import os.path

    directory = os.path.dirname(inspect.getfile(inspect.currentframe()))
    classifier_path = os.path.join(directory, 'classifier.clsf')
    
    return load_classifier(classifier_path)
    
@memoize
def __feature_matrix():
    import csv
    import inspect
    import os.path
    
    directory = os.path.dirname(inspect.getfile(inspect.currentframe()))
    feature_matrix_path = os.path.join(directory, 'feature_matrix.csv')
    
    with open(feature_matrix_path) as file:
        return [[row[0]] + [float(x) for x in row[1:]]
                for row in csv.reader(file)]
    
###############################################################################

def get_family_name(class_number):
    """Retrieve the family name for the family represented by the specified
    class number.
    
    The class number should be a value between 1 and 9.
    """
    
    if (not 1 <= class_number <= len(__families)):
        raise ValueError('Invalid class number: %d' % class_number)
        
    return __families[class_number-1]

def classify(file_path, as_family_name=False):
    """Classify the Windows executable pointed to by the specified path.
    
    If as_family_name is False, return the result as the class number. If it
    is True, return the result as the name of the family represented by the
    class number. If the class number is returned, get_family_name can be
    used to retrieve the family name later.
    """
    
    classification = int(__classifier().classify_exe(file_path))
    return get_family_name(classification) if as_family_name else classification

def search(file_path, label=None, num_samples=1):
    """Search for the samples in the database that are closest to the Windows
    executable at the specified file path.
    
    If label is set to a class number, only samples that are part of the
    specified label will be included in the search.
    
    num_samples is the number of samples to return in the search.
    
    This will return a list containing a tuple for each search result. Each
    tuple contains the following:
        
        [0] - The ID of the sample
        [1] - The distance between the sample and the specified file
        
    """
    from .storage import ExeRawSample
    from ..storage import search

    # If no label is specified, we need to remove the labels from the
    # feature matrix.
    feature_matrix = __feature_matrix()

    if (not label):
        feature_matrix = [sample[:-1] for sample in feature_matrix]

    with ExeRawSample(file_path) as sample:
        return search(feature_matrix, sample.features(), label=label,
                      num_samples=num_samples)
