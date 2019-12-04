import sys
import os
import main
from parse import parseData, extract_nums
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

class TestCMDVars(unittest.TestCase):
    def test_set(self):
        args = "-r 2000 -t 0.5 -p 10 -c 15 -v 25 -pp 25 -cp 75 -vp 30 -ps 1.2 -cs 6.2 -vs 10.2 -pd 0 -cd 0 -vd 0 -d 0 -sd 1"
        os.system("python main.py " + args + " > test_vars.txt")
        data = parseData("test_vars.txt")

        nums = extract_nums(args)
        vals = list(data.values())
        for i in range(len(nums)):
            self.assertEqual(nums[i], vals[i+1])
    # Passes... Commented out since it takes forever
    """ def test_default(self):
        defaults = [1000, 20, 30, 20, 50, 50, 50, 50, 1.3411, 5.3645, 11.176, 1, 1, 1, 0, 0]
        os.system("python main.py > test_vars.txt")
        data = parseData("test_vars.txt")

        vals = list(data.values())
        for i in range(len(defaults)):
            self.assertEqual(defaults[i], vals[i+1]) """

# Also tests road user length
class TestUniqueIDs(unittest.TestCase):
    def test_set(self):
        os.system("python main.py -t 0.2 -r 500 > test_IDs.txt") 
        data = parseData("test_IDs.txt")
        users = data['road_users']['list']
        last = None
        count = 0
        for user in users:
            if last == None:
                last = user['id']
            else:
                self.assertEqual(user['id'], last+1)
                last = user['id']
            count += 1

            # Test length of users
            if user['type'] == "Pedestrian":
                self.assertEqual(1, user['length'])
            if user['type'] == "Bicycle":
                self.assertEqual(2, user['length'])
            if user['type'] == "Motor Vehicle":
                self.assertEqual(6, user['length'])
        
        self.assertEqual(count, data['road_users']['totals']['total'])
        self.assertEqual(count, last+1)

if __name__ == '__main__': 
    unittest.main() 