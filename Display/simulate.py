import numpy as np
from parse import *
import os
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import multiprocessing as mp
import statistics
import datetime as dt
import json
import time
import argparse


def speed_helper(hours, speed):
    filename = "var_speed%s.txt" % str(speed)
    # print(speed)
    os.system("python main_new.py -r 1620 -t %d -c 0 -vs %d > %s" % (hours, speed, filename))
    data = parseData(filename)
    os.remove(filename)
    interactions = data['MV_MV_P'] + data['MV_MV_B']
    return (speed, interactions/hours)

def speed(start, filename, hours):
    pool = mp.Pool()
    results = [pool.apply_async(speed_helper, args=[hours, speed]) for speed in range(4, 27, 2)]
    output = [p.get() for p in results]
    pool.close()
    
    x = [m[0] * 2.237 for m in output]
    y = [m[1] for m in output]
    end = dt.datetime.now()

    with open(filename, "w") as file:
        data = {
            "x": x,
            "y": y,
            "start": str(start),
            "end": str(end)
        }

        json.dump(data, file, indent=4)
    return end

def length_helper(hours, length):
    filename = "var_length%s.txt" % str(length)

    os.system("python main_new.py -t %d -p 0 -r %d > %s" % (hours, length, filename))
    data = parseData(filename)
    os.remove(filename)
    interactions = data['MV_MV_P'] + data['MV_MV_B']
    return (length, interactions/hours)

def length(start, filename, hours):
    pool = mp.Pool()
    results = [pool.apply_async(length_helper, args=[hours, length]) for length in range(100, 2100, 100)]
    output = [p.get() for p in results]
    pool.close()
    end = dt.datetime.now()
    
    x = [m[0] for m in output]
    y = [m[1] for m in output]

    with open(filename, "w") as file:
        data = {
            "x": x,
            "y": y,
            "start": str(start),
            "end": str(end)
        }

        json.dump(data, file, indent=4)
    return end

def bike_vol(hours, vol):
    filename = "var_volume%s.txt" % str(vol)

    os.system("python main_new.py -t %d -p 0 -c %d > %s" % (hours, vol, filename))
    data = parseData(filename)
    os.remove(filename)
    interactions = data['MV_MV_P'] + data['MV_MV_B']
    return (vol, interactions/hours)

def ped_vol(hours, vol):
    filename = "var_volume%s.txt" % str(vol)

    os.system("python main_new.py -t %d -c 0 -p %d > %s" % (hours, vol, filename))
    data = parseData(filename)
    os.remove(filename)
    interactions = data['MV_MV_P'] + data['MV_MV_B']
    return (vol, interactions/hours)

def volume(start, filename, hours):
    pool = mp.Pool()
    results = [pool.apply_async(bike_vol, args=[hours, vol]) for vol in range(5, 65, 5)]
    output = [p.get() for p in results]
    pool.close()
    
    x_bikes = [m[0] for m in output]
    y_bikes = [m[1] for m in output]

    pool = mp.Pool()
    results = [pool.apply_async(ped_vol, args=[hours, vol]) for vol in range(5, 65, 5)]
    output = [p.get() for p in results]
    pool.close()
    end = dt.datetime.now()

    x_peds = [m[0] for m in output]
    y_peds = [m[1] for m in output]

    with open(filename, "w") as file:
        data = {
            "x_bikes": x_bikes,
            "y_bikes": y_bikes,
            "x_peds": x_peds,
            "y_peds": y_peds,
            "start": str(start),
            "end": str(end)
        }

        json.dump(data, file, indent=4)
    return end

def ped_split(hours, split):
    filename = "var_split%s.txt" % str(split)

    os.system("python main_new.py -sd 1 -t %d -c 0 -vp %d > %s" % (hours, split, filename))
    data = parseData(filename)
    os.remove(filename)
    interactions = data['MV_MV_P'] + data['MV_MV_B']
    return (split, interactions/hours)

def bike_split(hours, split):
    filename = "var_split%s.txt" % str(split)

    os.system("python main_new.py -sd 1 -t %d -p 0 -vp %d > %s" % (hours, split, filename))
    data = parseData(filename)
    os.remove(filename)
    interactions = data['MV_MV_P'] + data['MV_MV_B']
    return (split, interactions/hours)

def mv_split(hours, split):
    filename = "var_split%s.txt" % str(split)

    os.system("python main_new.py -sd 1 -t %d -vp %d > %s" % (hours, split, filename))
    data = parseData(filename)
    os.remove(filename)
    interactions = data['MV_MV_P'] + data['MV_MV_B']
    return (split, interactions/hours)

def dir_split(start, filename, hours):
    pool = mp.Pool()
    results = [pool.apply_async(bike_split, args=[hours, split]) for split in range(0, 110, 10)]
    output = [p.get() for p in results]
    pool.close()
    
    x_bikes = [m[0] for m in output]
    y_bikes = [m[1] for m in output]

    pool = mp.Pool()
    results = [pool.apply_async(ped_split, args=[hours, split]) for split in range(0, 110, 10)]
    output = [p.get() for p in results]
    pool.close()
    
    x_peds = [m[0] for m in output]
    y_peds = [m[1] for m in output]

    pool = mp.Pool()
    results = [pool.apply_async(mv_split, args=[hours, split]) for split in range(0, 110, 10)]
    output = [p.get() for p in results]
    pool.close()
    
    end = dt.datetime.now()

    x_mv = [m[0] for m in output]
    y_mv = [m[1] for m in output]

    with open(filename, "w") as file:
        data = {
            "x_bikes": x_bikes,
            "y_bikes": y_bikes,
            "x_peds": x_peds,
            "y_peds": y_peds,
            "x_mv": x_mv,
            "y_mv": y_mv,
            "start": str(start),
            "end": str(end)
        }

        json.dump(data, file, indent=4)
    return end

if __name__ == '__main__':
    try:
        print("Starting volume")
        time.sleep(5)
        start = dt.datetime.now()
        end = volume(start, "data/volume.json", 5000)
        print(end - start)
    except:
        print("Failed volume")
    time.sleep(5)
    try:
        print("Starting dir_split")
        time.sleep(5)
        start = dt.datetime.now()
        end = dir_split(start, "data/dir_split.json", 5000)
        print(end - start)
    except:
        print("Failed dir_split")
