import sys
import os
import main
from parse import parseData
import unittest




class TestRoadLength(unittest.TestCase): 
  
    # Test a user supplied road length (500)
    def test_set(self):         
        os.system("python main.py -t 0.2 -r 500 > test_road.txt") 
        data = parseData("test_road.txt")
        # Check the cmd line arg
        self.assertEqual(500, data['road_length'])
        # Do the math
        self.assertEqual(500, data['road']['east_end'] - data['road']['west_end'])
        # Check road sources
        for src in data['sources']:
            if src['direction'] == "WestBound":
                self.assertEqual(500, src['location'])
        # Check road users
        for user in data['road_users']['list']:
            if not user['platoon']:
                time = user['removed'] - user['created']
                self.assertAlmostEqual(500, abs(time*user['velocity']), delta=1, msg="Failed: Road User ID: " + str(user['id']))

    # Test the default road length (1000)
    def test_default(self):
        os.system("python main.py -t 0.2 > test_road.txt") 
        data = parseData("test_road.txt")
        # Check the cmd line arg
        self.assertEqual(1000, data['road_length'])
        # Do the math
        self.assertEqual(1000, data['road']['east_end'] - data['road']['west_end'])
        # Check road sources
        for src in data['sources']:
            if src['direction'] == "WestBound":
                self.assertEqual(1000, src['location'])

class TestClock(unittest.TestCase):

    def test_set(self):
        os.system("python main.py -t 0.2 > test_clock.txt") 
        data = parseData("test_clock.txt")

        self.assertEqual(0.2, data['clock']['total'])

        os.system("python main.py -t 0.5 > test_clock.txt") 
        data = parseData("test_clock.txt")

        self.assertEqual(0.5, data['clock']['total'])

    # Worked when I ran it, but it takes forever...
    """ def test_default(self):
        os.system("python main.py > test_clock.txt") 
        data = parseData("test_clock.txt")

        self.assertEqual(20, data['clock']['total']) """
if __name__ == '__main__': 
    unittest.main() 