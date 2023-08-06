import unittest
from unittest import TestCase
from ostsa.storage.SampleDao import percent_difference
from ostsa.storage.SampleDao import euclidean_distance
from ostsa.storage.SampleDao import search
        
###############################################################################

class TestPercentDifference(TestCase):
    
    def test_euclidean_distance(self):
        
        def test(list1, list2, expected):
            actual = euclidean_distance(list1, list2)
            self.assertAlmostEqual(expected, actual, places=3)
            
        test([1, 2, 3, 4], [1, 2, 3, 4], 0)
        test([-7, -4], [17, 6.5], 26.196)
        test([23, 0, -12, -1], [-29, -12, 34, -3], 70.484041)
    
    def test_percent_difference(self):
        
        def test(list1, list2, expected):
            actual = percent_difference(list1, list2)
            self.assertAlmostEqual(expected, actual, places=3)
            
        test([1, 2, 3, 4], [1, 2, 3, 4], 0)
        test([48, 3.84, 45, 1], [8514.1, 5, 3, 0.00001], 1.497)
        test([87, 2, 3.31, 125], [1.21, 21, 32.5, 42.0], 1.555)
        
    def test_search(self):
        
        feature_matrix = [['A', 1, 2, 3, 4],
                          ['B', 5, 10, 15, 20],
                          ['C', -5, 20, -20, 5],
                          ['D', 4, 3, 2, 1]]
                          
        def test(features, num_samples, *expected_labels):
            actual = [r[0] for r in search(feature_matrix, features, 
                                           num_samples=num_samples)]
            self.assertEqual(list(expected_labels), actual)
            
        test([1, 2, 3, 4], 1, 'A')
        test([6, 9, 16, 19], 1, 'B')
        test([1, 2, 2, 2], 2, 'A', 'D')
        test([1, 2, 3, 4], 4, 'A', 'D', 'B', 'C')
        
###############################################################################

if __name__ == '__main__':
    unittest().main()
