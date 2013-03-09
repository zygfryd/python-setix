import unittest

import setix

class NumpyTests (unittest.TestCase):
    def test_basic (self):
        ii = setix.SetIntersectionIndex ("numpy")
        ii.add ((1, 2, 3, 4))
        ii.add ((1, 3, 5, 6), "foo")
        ii.add ((1, 3, 5, 6), "bar")
        ii.add ((2, 4, 6, 7))
        ii.add ((2, 4, 5, 6))
        
        desired = [(3, [(1, 2, 3, 4)]),
                   (2, ["foo", "bar"])]
        actual = ii.find ((1, 2, 3), threshold=2).get_list ()
        
        self.assertTrue (len(actual) == len(desired))
        self.assertTrue (all (actual[i] == desired[i] for i in range(len(actual))))
        
        desired = [(0.75, [(1, 2, 3, 4)]),
                   (0.4,  ["foo", "bar"])]
        actual = ii.find_similar ((1, 2, 3), threshold=0.3).get_list ()
        
        self.assertTrue (len(actual) == len(desired))
        self.assertTrue (all (actual[i] == desired[i] for i in range(len(actual))))
        
        self.assertTrue (set (ii.most_frequent()) == set([6, 5, 4, 3, 2, 1]))
        self.assertTrue (set (ii.most_frequent(with_counts=True)) == set([(6,4), (5,3), (4,3), (3,3), (2,3), (1,3)]))
        self.assertTrue (set (ii.most_frequent(max_results=1)) == set([6]))
