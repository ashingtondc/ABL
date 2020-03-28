import numpy as np
from parse import *
import os
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import multiprocessing as mp
import statistics


def speed_helper(speed):
    filename = "var_speed%s.txt" % str(speed)
    # print(speed)
    os.system("python main_new.py -r 1620 -t 500 -c 0 -vs %d > %s" % (speed, filename))
    data = parseData(filename)
    # os.remove(filename)
    interactions = data['MV_MV_P'] + data['MV_MV_B']
    return (speed, interactions/10)

def speed():
    pool = mp.Pool()
    results = [pool.apply_async(speed_helper, args=[speed]) for speed in range(4, 27, 2)]
    output = [p.get() for p in results]
    pool.close()
    
    x = [m[0] for m in output]
    y = [m[1] for m in output]

    fig = plt.figure()
    ax1 = fig.add_subplot()
    ax1.set_xlabel("MV Speed (m/s)")
    ax1.set_ylabel("MVxMVxVRU Interactions/Hour")
    ax1.set_title("Influence of Varying Motor Vehicle Speeds")
    ax1.plot(x, y)
    plt.show()

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
    speed()