import numpy as np
from parse import *
import os
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import multiprocessing as mp
import statistics


def speed_helper(speed):
    filename = "var_speed%s.txt" % str(speed)

    os.system("python main_new.py -r 1000 -t 10 -vs %d > %s" % (speed, filename))
    data = parseData(filename)
    os.remove(filename)
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

    os.system("python main_new.py -t 10 -r %d > %s" % (length, filename))
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

if __name__ == '__main__':
    length()