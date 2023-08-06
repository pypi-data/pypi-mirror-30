from ..storage import create_dirs

import csv
import itertools
import multiprocessing
import os

def __hgs(args):
    def __hgs_worker(classifier_type, features, labels, results_file_name,
                     train_ratio, param_names, params):
        """A worker function to be used for multiprocessing assistance in the
        hyperparameter_grid_search function.
        """
                
        # Train the classifier.
        classifier = classifier_type(features, labels, training_ratio=0.7,
                                     **params)
                                     
        # Print the metrics for the classifier to the file.
        accuracy = classifier.accuracy()
        logloss = classifier.logloss()
        
        row = [params[name] for name in param_names]
        row += [accuracy, logloss]
        
        # Print results to file.
        with open(results_file_name, 'a') as file:
            csv.writer(file, lineterminator='\n').writerow(row)
            
        # Indicate that a classifier has finished.
        print('Finished a classifier...')
    
    __hgs_worker(*args)

def hyperparameter_grid_search(classifier_type, features, labels, 
                               results_file_name, train_ratio=0.7,
                               num_processes=4, **parameter_subsets):
    """Performs a grid search hyperparameter optimization for the specified
    classifier type and prints the results to the specified file.
    
    classifier_type should be the type of the classifier to use. The Classifier
    should have a constructor that takes a set of keyword arguments that are
    used to set the parameters for the underlying model.
    
    features should be the feature matrix for the sample set to test the
    classifier on.
    
    labels should be the list of labels for the sample set to test the
    classifier on.
    
    results_file_name should be the name of the csv file that the results 
    should be output to.
    
    train_ratio is the ratio of the included sample set to be used for
    training. The result will be used for testing.
    
    num_processes is the number of processes that can be spawned to train the
    classifiers concurrently.
    
    parameter_subsets should specify the list of values to test for each
    hyperparameter. The key for each entry should directly reference a specific
    hyperparameter in the model and each value should be a list of values to
    test for that model.
    
    Note that this function will train a model for every combination of
    hyperparameters values supplied. This function may take a very long time to
    complete. If this is stopped prematurely, the results_file will only
    contain the results for the models that were already trained.
    """    
                
    # Ensure the directory for the results file exists.
    create_dirs(results_file_name)
        
    # Retrieve a list of all of the parameter keys. This is necessary to 
    # ensure that the keys are always in the same order.
    names = sorted(parameter_subsets.keys())
    
    # If the file already exists, determine the order of the hyperparameters
    # from the file and grab the sets that are already evaluated.
    if (os.path.isfile(results_file_name)):
        with open(results_file_name) as file:
            reader = csv.reader(file)
            
            # Read headers
            # Note: The last two columns are accuracy and logloss.
            headers = next(reader)[:-2]
            
            # If the labels do not match the names, trying to write the new
            # results to the file will only cause problems.
            if (sorted(headers) != names):
                raise ValueError('The specified results file already exists '
                                 'and already contains entries that have '
                                 'different set hyperparameters than the '
                                 'ones specified.')
                                 
            names = headers
            sets_in_file = [tuple(float(x) for x in row[:-2]) 
                            for row in reader]
            
    # If the file does not already exist, we need to create it and write the
    # headers.
    else:
        with open(results_file_name, 'w') as file:
            headers = names + ['Accuracy', 'Logloss']
            csv.writer(file, lineterminator='\n').writerow(headers) 
    
    # Retrieve the cartesion product of all of the sets of values.
    parameter_sets = list(itertools.product(*[parameter_subsets[key] 
                                              for key in names]))
                                                  
    # If the file exists and parameter sets were found, remove any of the sets
    # already evaluated.
    if (sets_in_file):
        removed = [set for set in sets_in_file if set in parameter_sets]
        for set in removed:
            parameter_sets.remove(set)
        
        print('Removed %d sets that were already in the file.' % len(removed))
    
    # Each set is currently a list of all of the parameters. In order to 
    # set the parameters, each list will need to be converted to a 
    # dictionary to associate the parameter names with their values.
    parameter_sets = [dict(zip(names, set)) for set in parameter_sets]
        
    # Indicate how many classifiers need to be trained.
    print('Training %d classifiers...' % len(parameter_sets))
    
    # Create a pool of processes to train the classifiers.
    pool = multiprocessing.Pool(num_processes)
    args = [[classifier_type, features, labels, results_file_name, train_ratio,
            names, parameter_set] for parameter_set in parameter_sets]
    pool.map(__hgs, args)

#    # Test each set of parameters.
#    for parameters in parameter_sets:
#        
#        # Train the classifier.
#        classifier = classifier_type(features, labels, 
#                                     training_ratio=train_ratio,
#                                     **parameters)
#                                     
#        # Measure the performance measures of the classifier.
#        accuracy = classifier.accuracy()
#        logloss = classifier.logloss()
#        
#        row = [parameters[name] for name in names]
#        row += [accuracy, logloss]
#        
#        # Print results to file.
#        with open(results_file_name, 'a') as file:
#            csv.writer(file, lineterminator='\n').writerow(row)
#            
#        # Indicate that a classifier has finished.
#        print('Finished a classifier...')
                      
                      