import unittest
import os

class TestCase(unittest.TestCase):
    """The base class of all test cases in this project. Intended to provide
    convenience methods to allow easier test case creation.
    """
    
    def compare_list(self, value_list, expected):
        """Assert that the list of values is equivalent to the specified
        expected list of values.
        
        The expected value can either be another list or the name of a file
        containing the expected list.
        """
        
        # Load the list from a file if necessary.
        if (type(expected) is str):
            expected = self.results(expected)
            
        # Ensure the lists have the same lengths.
        if (len(value_list) != len(expected)):
            raise AssertionError('Lists are not equal. Actual list contains ' \
                                 + '%d more elements than expected.' \
                                 % (len(value_list) - len(expected)))
                                 
        # Check each element in the list.
        for i in range(len(expected)):
            actual = value_list[i]
            exp = expected[i]
            self.assertAlmostEqual(actual, exp, 4, 
                                   ('List are not equal at element ' \
                                   + '{0}\n\nActual: {1}\nExpected: ' \
                                   + '{2}').format((i+1), actual, exp))
    
    def results(self, file_name):
        """Load the results stored in the specified file name.
        
        The specified file is assumed to be within the directory pointed to
        by the results_directory instance variable. This variable should be
        set by subclasses to ensure the results can be found.
        """
        
        # Ensure the results_directory is set.
        if (not hasattr(self, 'results_directory')):
            raise ValueError('You must set the results_directory variable in'
                             + ' your subclass to make use of the results '
                             + 'method.')
                             
        # Construct the full path for the specified file.
        file_path = os.path.join(self.results_directory, file_name)
        
        # Read in the results from the file as a list of int values.
        try:
            with open(file_path) as results_file:
                return [float(line) for line in results_file]
        
        except IOError:
            raise IOError('Invalid results file: %s' % file_path)
