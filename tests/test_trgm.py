import unittest

import setix.trgm

class TrgmTests (unittest.TestCase):
    def test_basic (self):
        ii = setix.trgm.TrigramIndex ()
        
        ii.add ("adam mickiewicz")
        ii.add ("adam mckiewicz")
        ii.add ("adm mickiewicz")
        ii.add ("adam mickiewizc")
        
        desired = [(1.00, ['adam mickiewicz']),
                   (0.72, ['adm mickiewicz']),
                   (0.72, ['adam mckiewicz']),
                   (0.68, ['adam mickiewizc'])]
        actual = ii.find_similar ("adam mickiewicz", threshold=0.1).get_list ()
        
        self.assertTrue (len(actual) == len(desired))
        self.assertTrue (all ((actual[i][1] == desired[i][1] and abs(actual[i][0] - desired[i][0]) < 0.01) for i in range(len(actual))))
