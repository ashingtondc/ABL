import numpy as np
from parse import *
import os
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import multiprocessing as mp
import statistics
from tqdm import tqdm

""" for i in range(100):
    print("Run " + str(i+1) + " of 100")
    os.system("python main.py -t 1 -c 0 -p 0 -vd 0 > vehs.txt") 
    data = parseData("vehs.txt")
    num_vehs.append(data['recorded']) """


def run(num, max_c):
    # print(str(num+1) + " of " + str(max_c))
    filename = "vehs" + str(num+1) + ".txt"
    os.system("python main.py -t 1 -c 0 -p 0 -vd 0 > " + filename) 
    data = parseData(filename)
    os.remove(filename)
    return data['recorded']

def test_helper_ph1(num, max_c):
    # print(str(num+1) + " of " + str(max_c))
    filename = "vehs" + str(num+1) + ".txt"
    os.system("python main.py -t 1 -c 0 -p 0 -vd 0 > " + filename) 
    data = parseData(filename)
    os.remove(filename)
    return data['recorded']

def test_helper_user_vols(num, max_c):
    filename = "vols" + str(num+1) + ".txt"
    os.system("python main.py -t 1 -p 20 -c 30 -v 50 > " + filename)
    data = parseData(filename)
    os.remove(filename)

    cars = data['road_users']['totals']['motor_vehicles']
    bikes = data['road_users']['totals']['bicycles']
    peds = data['road_users']['totals']['peds']

    return (peds, bikes, cars)

def test_helper_speeds(num, max_c):
    filename = "speeds" + str(num+1) + ".txt"
    os.system("python main.py -c 50 -p 50 -cs 50 -ps 10 -vs 110 > " + filename)
    data = parseData(filename)
    os.remove(filename)

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
    
    return (ped_speeds, bike_speeds, veh_speeds)

def test_helper_dir_vol_split(num, max_c):
    filename = "vols" + str(num+1) + ".txt"
    os.system("python main.py -t 1 -c 30 -p 30 -v 30 -cp 70 -pp 10 -vp 50 > " + filename) 
    data = parseData(filename)
    os.remove(filename)
    
    users = data['road_users']['list']

    east = {
        'Pedestrian': 0,
        'Bicycle': 0,
        'Motor Vehicle': 0
    }

    west = {
        'Pedestrian': 0,
        'Bicycle': 0,
        'Motor Vehicle': 0
    }

    ped_total = data['road_users']['totals']['peds']
    bike_total = data['road_users']['totals']['bicycles']
    car_total = data['road_users']['totals']['motor_vehicles']

    for user in users:
        if user['direction'] == "EastBound":
            east[user['type']] += 1
        else:
            west[user['type']] += 1

    try:
        ped_split = east['Pedestrian']/ped_total
    except:
        ped_split = 0
    try:
        bike_split = east['Bicycle']/bike_total
    except:
        bike_split = 0
    try:    
        mv_split = east['Motor Vehicle']/car_total
    except:
        mv_split = 0
    
    return (ped_split, bike_split, mv_split)


def crunch(samples, func):
    pool = mp.Pool()
    max_c = samples
    results = [pool.apply_async(func, args=(x,max_c)) for x in range(max_c)]
    output = [p.get() for p in results]
    pool.close()
    return output

if __name__ == '__main__':
    """ medians = []
    for i in tqdm(range(10)):
        pool = mp.Pool()
        max_c = 30
        func = run
        results = [pool.apply_async(func, args=(x,max_c)) for x in range(max_c)]
        output = [p.get() for p in results]
        n, bins, patches = plt.hist(output, bins='auto', facecolor='blue', alpha=0.5)
        pred_inter = ((0.5 * 50)**2) * (1000/11.176) / 1800
        print("Predicted interactions: " + str(pred_inter))
        print("Min: " + str(min(output)))
        print("Max: " + str(max(output)))
        sigma = statistics.stdev(output, xbar=pred_inter)
        print("STD DEV: " + str(sigma))
        print("Median: " + str(statistics.median(output)))
        medians.append(statistics.median(output))
        pool.close()
    print(medians)

    plt.show() """
    medians = []
    means = []
    for i in tqdm(range(10)):
        data = crunch(30, test_helper_user_vols)
        peds = [item[0] for item in data]

        medians.append(statistics.median(peds))
        means.append(statistics.mean(peds))

    print(medians)
    print(means)