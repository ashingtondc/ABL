import numpy as np
from parse import *
import os
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import multiprocessing as mp
import statistics
import datetime as dt


def speed_helper(speed):
    filename = "var_speed%s.txt" % str(speed)
    # print(speed)
    os.system("python main_new.py -r 1620 -t 1000 -c 0 -vs %d > %s" % (speed, filename))
    data = parseData(filename)
    os.remove(filename)
    interactions = data['MV_MV_P'] + data['MV_MV_B']
    return (speed, interactions/1000)

def speed():
    pool = mp.Pool()
    results = [pool.apply_async(speed_helper, args=[speed]) for speed in range(4, 27, 2)]
    output = [p.get() for p in results]
    pool.close()
    
    x = [m[0] * 2.237 for m in output]
    y = [m[1] for m in output]
    end = dt.datetime.now()
    fig = plt.figure(figsize=(8, 6))
    ax1 = fig.add_subplot()
    ax1.set_xlabel("Miles per Hour")
    ax1.set_ylabel("MVxMVxVRU Interactions/Hour")
    ax1.plot(x, y)

    # KM/HR Axis
    left, right = ax1.get_xlim()
    ax2 = ax1.twiny()
    ax2.set_xlim(left * 1.609, right * 1.609)
    ax2.set_xlabel("Kilometers per Hour")

    ax2.set_title("Influence of Varying Motor Vehicle Speeds")
    plt.show()
    return end

def length_helper(length):
    filename = "var_length%s.txt" % str(length)

    os.system("python main_new.py -t 10 -p 0 -r %d > %s" % (length, filename))
    data = parseData(filename)
    os.remove(filename)
    interactions = data['MV_MV_P'] + data['MV_MV_B']
    return (length, interactions/10)

def length():
    pool = mp.Pool()
    results = [pool.apply_async(length_helper, args=[length]) for length in range(100, 2100, 100)]
    output = [p.get() for p in results]
    pool.close()
    
    x = [m[0] for m in output]
    y = [m[1] for m in output]

    fig = plt.figure()
    ax1 = fig.add_subplot()
    ax1.set_xlabel("Facility Length (m)")
    ax1.set_ylabel("MVxMVxVRU Interactions/Hour")
    ax1.set_title("Influence of Varying Facility Length")
    ax1.plot(x, y)
    plt.show()
    return end

def bike_vol(vol):
    filename = "var_volume%s.txt" % str(vol)

    os.system("python main_new.py -t 10 -p 0 -c %d > %s" % (vol, filename))
    data = parseData(filename)
    os.remove(filename)
    interactions = data['MV_MV_P'] + data['MV_MV_B']
    return (vol, interactions/10)

def ped_vol(vol):
    filename = "var_volume%s.txt" % str(vol)

    os.system("python main_new.py -t 10 -c 0 -p %d > %s" % (vol, filename))
    data = parseData(filename)
    os.remove(filename)
    interactions = data['MV_MV_P'] + data['MV_MV_B']
    return (vol, interactions/10)

def volume():
    pool = mp.Pool()
    results = [pool.apply_async(bike_vol, args=[vol]) for vol in range(5, 65, 5)]
    output = [p.get() for p in results]
    pool.close()
    
    x_bikes = [m[0] for m in output]
    y_bikes = [m[1] for m in output]

    fig = plt.figure()
    ax1 = fig.add_subplot()
    ax1.set_xlabel("VRU Volume/HR")
    ax1.set_ylabel("MVxMVxVRU Interactions/Hour")
    ax1.set_title("Influence of Varying VRU Volumes")
    ax1.plot(x_bikes, y_bikes, 'b')

    pool = mp.Pool()
    results = [pool.apply_async(ped_vol, args=[vol]) for vol in range(5, 65, 5)]
    output = [p.get() for p in results]
    pool.close()
    
    x_peds = [m[0] for m in output]
    y_peds = [m[1] for m in output]

    ax1.plot(x_peds, y_peds, 'r')
    ax1.legend(['Bicycles', 'Pedestrians'])
    plt.show()

def ped_split(split):
    filename = "var_split%s.txt" % str(split)

    os.system("python main_new.py -sd 1 -t 10 -c 0 -vp %d > %s" % (split, filename))
    data = parseData(filename)
    os.remove(filename)
    interactions = data['MV_MV_P'] + data['MV_MV_B']
    return (split, interactions/10)

def bike_split(split):
    filename = "var_split%s.txt" % str(split)

    os.system("python main_new.py -sd 1 -t 10 -p 0 -vp %d > %s" % (split, filename))
    data = parseData(filename)
    os.remove(filename)
    interactions = data['MV_MV_P'] + data['MV_MV_B']
    return (split, interactions/10)

def mv_split(split):
    filename = "var_split%s.txt" % str(split)

    os.system("python main_new.py -sd 1 -t 10 -vp %d > %s" % (split, filename))
    data = parseData(filename)
    os.remove(filename)
    interactions = data['MV_MV_P'] + data['MV_MV_B']
    return (split, interactions/10)

def dir_split():
    pool = mp.Pool()
    results = [pool.apply_async(bike_split, args=[split]) for split in range(0, 110, 10)]
    output = [p.get() for p in results]
    pool.close()
    
    x_bikes = [m[0] for m in output]
    y_bikes = [m[1] for m in output]

    fig = plt.figure()
    ax1 = fig.add_subplot()
    ax1.set_xlabel("Percent of Motor Vehicles Traveling East")
    ax1.set_ylabel("MVxMVxVRU Interactions/Hour")
    ax1.set_title("Influence of Varying Directional Splits")
    ax1.plot(x_bikes, y_bikes, 'b')

    pool = mp.Pool()
    results = [pool.apply_async(ped_split, args=[split]) for split in range(0, 110, 10)]
    output = [p.get() for p in results]
    pool.close()
    
    x_peds = [m[0] for m in output]
    y_peds = [m[1] for m in output]

    ax1.plot(x_peds, y_peds, 'r')

    pool = mp.Pool()
    results = [pool.apply_async(mv_split, args=[split]) for split in range(0, 110, 10)]
    output = [p.get() for p in results]
    pool.close()

    x_mv = [m[0] for m in output]
    y_mv = [m[1] for m in output]

    ax1.plot(x_mv, y_mv, 'g')
    ax1.legend(['Bicycles', 'Pedestrians', 'All'])

    plt.show()

if __name__ == '__main__':
    start = dt.datetime.now()
    end = speed()
    print(end - start)