import sys
import os
import main
from parse import parseData, extract_nums
import unittest
from scipy import stats
from cruncher import *
import statistics


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
        # Check road users time spent on road
        for user in data['road_users']['list']:
            if not user['left_on_road']:
                if not user['platoon']:
                    time = user['removed'] - user['created']
                    self.assertAlmostEqual(time, 500/abs(user['velocity']), delta=1, msg="Failed: Road User ID: " + str(user['id']))
                else:
                    time = user['removed'] - user['created']
                    # Add 0.1 to account for rounding
                    self.assertTrue(time + 0.1 >= 500/abs(user['velocity']), msg="Failed: Road User ID: " + str(user['id']))

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

class TestSpeeds(unittest.TestCase):
    def test_constant(self):
        os.system("python main.py -t 0.2 -cd 0 -pd 0 -vd 0 > test_speeds.txt") 
        data = parseData("test_speeds.txt")
        clock_step = data['clock']['tick_length']
        users = data['road_users']['list']
        for user in users:
            # Verify distance/tick of road users
            self.assertAlmostEqual(user['velocity_tick'], user['velocity'] * clock_step, delta=0.1)
            # Verify constant speed - equality check
            if user['type'] == "Pedestrian":
                self.assertAlmostEqual(data['ped_speed'], abs(user['velocity']), delta=0.1)
            if user['type'] == "Bicycle":
                self.assertAlmostEqual(data['bike_speed'], abs(user['velocity']), delta=0.1)
            if user['type'] == "Motor Vehicle":
                self.assertAlmostEqual(data['mv_speed'], abs(user['velocity']), delta=0.1)
            
            # Verify speed corresponds to direction
            if user['direction'] == "EastBound":
                self.assertTrue(user['velocity'] > 0)
            else:
                self.assertTrue(user['velocity'] < 0)
    
    def test_distributions(self):
        os.system("python main.py -c 50 -p 50 > test_speeds.txt")
        data = parseData("test_speeds.txt")
        ped_speeds = []
        bike_speeds = []
        veh_speeds = []
        for user in data['road_users']['list']:
            if user['type'] == 'Pedestrian':
                ped_speeds.append(abs(user['velocity']))
            elif user['type'] == 'Bicycle':
                bike_speeds.append(abs(user['velocity']))
            else:
                veh_speeds.append(abs(user['velocity']))
        self.assertAlmostEqual(data['ped_speed'], statistics.median(ped_speeds), delta=2)
        self.assertAlmostEqual(data['bike_speed'], statistics.median(bike_speeds), delta=2)
        self.assertAlmostEqual(data['mv_speed'], statistics.median(veh_speeds), delta=2)


class TestLocations(unittest.TestCase):
    def test_loc(self):
        os.system("python main.py -t 0.2 > test_locations.txt") 
        data = parseData("test_locations.txt")
        sources = data['sources']
        users = data['road_users']['list']
        for user in users:
            direction = user['direction']
            user_type = user['type']
            src = None
            for source in sources:
                if source['direction'] == direction and source['type'] in user_type:
                    src = source
            self.assertAlmostEqual(src['location'], user['create_pos'], delta=1, msg="Failed: Road User ID: " + str(user['id']))

# These need to be re-written to use a normal distribution of sample means
class TestVols(unittest.TestCase):
    # Test the directional split
    # Disabled because it takes a while
    def test_dir_split(self):
        data = crunch(30, test_helper_dir_vol_split)

        peds = [item[0] for item in data]
        bikes = [item[1] for item in data]
        cars = [item[2] for item in data]

        pval = stats.normaltest(peds).pvalue
        self.assertGreater(pval, 0.05, msg="Enough evidence to reject null hypothesis that the data follows a normal distribution")
        pval = stats.normaltest(bikes).pvalue
        self.assertGreater(pval, 0.05, msg="Enough evidence to reject null hypothesis that the data follows a normal distribution")
        pval = stats.normaltest(cars).pvalue
        self.assertGreater(pval, 0.05, msg="Enough evidence to reject null hypothesis that the data follows a normal distribution")


        self.assertAlmostEqual(0.1, statistics.mean(peds), delta=0.05)
        self.assertAlmostEqual(0.7, statistics.mean(bikes), delta=0.05)
        self.assertAlmostEqual(0.5, statistics.mean(cars), delta=0.05)


    # See if we are producing the right amount of users per hour
    def test_user_vols(self):
        data = crunch(30, test_helper_user_vols)
        peds = [item[0] for item in data]
        bikes = [item[1] for item in data]
        cars = [item[2] for item in data]

        pval = stats.normaltest(peds).pvalue
        self.assertGreater(pval, 0.05, msg="Enough evidence to reject null hypothesis that the data follows a normal distribution")
        pval = stats.normaltest(bikes).pvalue
        self.assertGreater(pval, 0.05, msg="Enough evidence to reject null hypothesis that the data follows a normal distribution")
        pval = stats.normaltest(cars).pvalue
        self.assertGreater(pval, 0.05, msg="Enough evidence to reject null hypothesis that the data follows a normal distribution")

        self.assertAlmostEqual(20, statistics.median(peds), delta=2)
        self.assertAlmostEqual(30, statistics.median(bikes), delta=2)
        self.assertAlmostEqual(50, statistics.median(cars), delta=2)


class TestPlatooning(unittest.TestCase):
    # Cannot have platoon of 1
    # Need to consider when slow followed by fast, then immediately after slow followed by fast
    def test_number(self):
        os.system("python main.py -t 1 > test_platoon.txt") 
        data = parseData("test_platoon.txt")

        users = data['road_users']['list']
        east_platooners = 0
        west_platooners = 0
        for user in users:
            if user['direction'] == "EastBound":
                if user['platoon']:
                    east_platooners += 1
                else:
                    self.assertFalse(east_platooners == 1)
                    east_platooners = 0
            else:
                if user['platoon']:
                    west_platooners += 1
                else:
                    self.assertFalse(west_platooners == 1)
                    west_platooners = 0
        self.assertFalse(east_platooners == 1)
        self.assertFalse(west_platooners == 1)

    # Ensure bikes and peds do not platoon
    def test_types(self):
        os.system("python main.py -t 1 > test_platoon.txt") 
        data = parseData("test_platoon.txt")

        users = data['road_users']['list']
        for user in users:
            if user['platoon']:
                self.assertTrue(user['type'] == "Motor Vehicle")
class TestPhaseOne(unittest.TestCase):
    # Test predicted total interactions/hour
    # Disabled due to it taking too long
    def test_one(self):
        data = crunch(50, test_helper_ph1)
        pval = stats.normaltest(data).pvalue
        self.assertGreater(pval, 0.05, msg="Enough evidence to reject null hypothesis that the data follows a normal distribution")
        pred_meetings = ((0.5 * 50)**2) * (1000/11.176) / 1800
        median = statistics.median(data)
        self.assertAlmostEqual(pred_meetings, median, delta=6)

    def test_two(self):
        os.system("python main.py -t 1 -c 0 -p 0 -vd 0 > test_phase1.txt") 
        data = parseData("test_phase1.txt")
        pred_meetings = ((25/3600) / data['mv_speed'] * data['road_length']) + ((25/3600) * (data['road_length'] / data['mv_speed']))
        counts = []
        for user in data['road_users']['list']:
            count = 0
            for event in data['interactions']:
                for participant in event['road_users']:
                    if user['id'] == participant['id']:
                        count += 1
            counts.append(count)
        self.assertAlmostEqual(pred_meetings, statistics.median(counts), delta=0.5)

if __name__ == '__main__': 
    unittest.main() 