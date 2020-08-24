import numpy as np
from parse import *
import os
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import multiprocessing as mp
import statistics
import datetime as dt
import json
import argparse


def fhwa_helper(setting, bikes, hours):
    vol = setting[0]
    speed = setting[1] // 2.237
    filename = "var_fhwa%s.txt" % str(bikes)
    os.system("python main.py  -p 0 -t %d -c %d -v %d -vs %d > %s" % (hours, bikes, vol, speed, filename))

    return (bikes, filename)


def fhwa(start, outfile, hours):
    settings = [(300, 25, "Preferred - Slow"), (300, 35, "Preferred - Fast"), (600, 35, "Potential Fast"), (600, 25, "Potential - Slow")]
    lines = []
    for setting in settings:
        pool = mp.Pool(processes=30)
        results = [pool.apply_async(fhwa_helper, args=[setting, bikes, hours]) for bikes in range(0, 105, 5)]
        output = [p.get() for p in results]
        pool.close()
        
        x = [m[0] for m in output]
        filenames = [m[1] for m in output]
        y = []

        for filename in filenames:
            data = parseDataLite(filename)
            os.remove(filename)
            interactions = data['vru_interactions']
            y.append(interactions/hours)
        line = {
            "x": x,
            "y": y,
            "type": setting[2]
        }
        lines.append(line)
    end = dt.datetime.now()

    with open(outfile, "w") as file:
        data = {
            "datasets": lines,
            "start": str(start),
            "end": str(end),
            "cmd": "python main.py  -p 0 -t hours -c bikes -v vehicles -vs vehicle_speed > filename"
        }

        json.dump(data, file, indent=4)
    return end

def duration_helper(hours, duration):
    filename = "var_duration%s.txt" % str(duration)
    # print(speed)
    os.system("python main.py -t %d -it %d > %s" % (hours, duration, filename))
    
    return (duration, filename)

def duration(start, outfile, hours):
    pool = mp.Pool()
    results = [pool.apply_async(duration_helper, args=[hours, duration]) for duration in range(0, 21)]
    output = [p.get() for p in results]
    pool.close()
    
    x = [m[0] for m in output]
    filenames = [m[1] for m in output]
    y = []

    for filename in filenames:
        data = parseDataLite(filename)
        os.remove(filename)
        interactions = data['vru_interactions']
        y.append(interactions/hours)

    end = dt.datetime.now()

    with open(outfile, "w") as file:
        data = {
            "x": x,
            "y": y,
            "start": str(start),
            "end": str(end),
            "cmd": "python main.py -t time -it duration > filename"
        }

        json.dump(data, file, indent=4)
    return end

def speed_helper(hours, speed):
    filename = "var_speed%s.txt" % str(speed)
    # print(speed)
    os.system("python main.py -r 1620 -t %d -vs %d > %s" % (hours, speed/2.23693629, filename))
    
    return (speed, filename)

def speed(start, outfile, hours):
    pool = mp.Pool(processes=60)
    results = [pool.apply_async(speed_helper, args=[hours, speed]) for speed in range(20, 65, 5)]
    output = [p.get() for p in results]
    pool.close()
    
    x = [m for m in range(20, 65, 5)]
    filenames = [m[1] for m in output]
    y = []

    for filename in filenames:
        data = parseDataLite(filename)
        os.remove(filename)
        interactions = data['vru_interactions']
        y.append(interactions/hours)

    end = dt.datetime.now()

    with open(outfile, "w") as file:
        data = {
            "x": x,
            "y": y,
            "start": str(start),
            "end": str(end),
            "cmd": "python main.py -r 1620 -t time -vs speed > filename"
        }

        json.dump(data, file, indent=4)
    return end

def length_v2_helper(hours, length, speed):
    filename = "var_length_v2%s_%s.txt" % (str(length), str(speed))

    os.system("python main.py -t %d -vs %d -r %d > %s" % (hours, speed, length, filename))
    
    return (length, filename)

def length_v2(start, outfile, hours):
    storage = []
    # List of tuples of the format (speed, x, y)
    for speed in range(20, 75, 5):
        print("Starting  batch for speed %d", speed)
        pool = mp.Pool(processes=30)
        results = [pool.apply_async(length_v2_helper, args=[hours, length, speed/2.23693629]) for length in range(100, 2100, 100)]
        output = [p.get() for p in results]
        pool.close()
        
        x = [m[0] for m in output]
        filenames = [m[1] for m in output]
        y = []

        for filename in filenames:
            data = parseDataLite(filename)
            os.remove(filename)
            interactions = data['vru_interactions']
            y.append(interactions/hours)
        storage.append((speed, x, y))
    
    end = dt.datetime.now()

    with open(outfile, "w") as file:
        data = {
            "graphs": storage,
            "start": str(start),
            "end": str(end),
            "cmd": "python main.py -t time -vs speed -r length > filename"
        }

        json.dump(data, file, indent=4)
    return end

def length_helper(hours, length):
    filename = "var_length%s.txt" % str(length)

    os.system("python main.py -t %d -p 0 -r %d > %s" % (hours, length, filename))
    
    return (length, filename)

def length(start, outfile, hours):
    pool = mp.Pool()
    results = [pool.apply_async(length_helper, args=[hours, length]) for length in range(100, 2100, 100)]
    output = [p.get() for p in results]
    pool.close()
    
    x = [m[0] for m in output]
    filenames = [m[1] for m in output]
    y = []

    for filename in filenames:
        data = parseData(filename)
        os.remove(filename)
        interactions = data['vru_interactions']
        y.append(interactions/hours)
    
    end = dt.datetime.now()

    with open(outfile, "w") as file:
        data = {
            "x": x,
            "y": y,
            "start": str(start),
            "end": str(end),
            "cmd": "python main.py -t time -p 0 -r length > filename"
        }

        json.dump(data, file, indent=4)
    return end

def volume_2_helper(hours, vol):
    filename = "var_volume2_%s.txt" % str(vol)

    os.system("python main.py -t %d -p 0 -c 0 -v %d > %s" % (hours, vol, filename))
   
    return (vol, filename)

def volume_2(start, outfile, hours):
    pool = mp.Pool(processes=30)
    results = [pool.apply_async(volume_2_helper, args=[hours, vol]) for vol in range(0, 625, 25)]
    output = [p.get() for p in results]
    pool.close()
    
    x = [m[0] for m in output]
    filenames = [m[1] for m in output]
    y = []

    for filename in filenames:
        data = parseDataLite(filename)
        os.remove(filename)
        interactions = data['mvxmv_interactions']
        y.append(interactions/hours)

    end = dt.datetime.now()

    with open(outfile, "w") as file:
        data = {
            "x": x,
            "y": y,
            "start": str(start),
            "end": str(end),
            "cmd": "python main.py -t hours -p 0 -c 0 -v volume > filename"
        }

        json.dump(data, file, indent=4)
    return end

def bike_vol(hours, vol):
    filename = "var_volume%s.txt" % str(vol)

    os.system("python main.py -t %d -p 0 -cd 0 -c %d > %s" % (hours, vol, filename))
   
    return (vol, filename)

def ped_vol(hours, vol):
    filename = "var_volume%s.txt" % str(vol)

    os.system("python main.py -t %d -c 0 -pd 0 -p %d > %s" % (hours, vol, filename))
    
    return (vol, filename)

def volume(start, outfile, hours):
    pool = mp.Pool(processes=31)
    results = [pool.apply_async(bike_vol, args=[hours, vol]) for vol in range(10, 310, 10)]
    output = [p.get() for p in results]
    pool.close()
    
    x_bikes = [m[0] for m in output]
    filenames = [m[1] for m in output]
    y_bikes = []

    for filename in filenames:
        data = parseDataLite(filename)
        os.remove(filename)
        interactions = data['vru_interactions']
        y_bikes.append(interactions/hours)

    pool = mp.Pool(processes=31)
    results = [pool.apply_async(ped_vol, args=[hours, vol]) for vol in range(10, 310, 10)]
    output = [p.get() for p in results]
    pool.close()

    x_peds = [m[0] for m in output]
    filenames = [m[1] for m in output]
    y_peds = []

    for filename in filenames:
        data = parseDataLite(filename)
        os.remove(filename)
        interactions = data['vru_interactions']
        y_peds.append(interactions/hours)

    end = dt.datetime.now()

    with open(outfile, "w") as file:
        data = {
            "x_bikes": x_bikes,
            "y_bikes": y_bikes,
            "x_peds": x_peds,
            "y_peds": y_peds,
            "start": str(start),
            "end": str(end),
            "cmd": ["python main.py -t time -p 0 -cd 0 -c volume > filename", "python main.py -t time -c 0 -pd 0 -p volume > filename"]
        }

        json.dump(data, file, indent=4)
    return end

def ped_split(hours, split):
    filename = "var_split%s.txt" % str(split)

    os.system("python main.py -sd 1 -t %d -c 0 -vp %d > %s" % (hours, split, filename))
    
    return (split, filename)

def bike_split(hours, split):
    filename = "var_split%s.txt" % str(split)

    os.system("python main.py -sd 1 -t %d -p 0 -vp %d > %s" % (hours, split, filename))

    return (split, filename)

def mv_split(hours, split):
    filename = "var_split%s.txt" % str(split)

    os.system("python main.py -sd 1 -t %d -vp %d > %s" % (hours, split, filename))

    return (split, filename)

def dir_split(start, outfile, hours):
    pool = mp.Pool(processes=4)
    results = [pool.apply_async(bike_split, args=[hours, split]) for split in range(0, 110, 10)]
    output = [p.get() for p in results]
    pool.close()
    
    x_bikes = [m[0] for m in output]
    filenames = [m[1] for m in output]
    y_bikes = []

    for filename in filenames:
        data = parseDataLite(filename)
        os.remove(filename)
        interactions = data['vru_interactions']
        y_bikes.append(interactions/hours)

    pool = mp.Pool(processes=4)
    results = [pool.apply_async(ped_split, args=[hours, split]) for split in range(0, 110, 10)]
    output = [p.get() for p in results]
    pool.close()
    
    x_peds = [m[0] for m in output]
    filenames = [m[1] for m in output]
    y_peds = []

    for filename in filenames:
        data = parseDataLite(filename)
        os.remove(filename)
        interactions = data['vru_interactions']
        y_peds.append(interactions/hours)

    pool = mp.Pool(processes=4)
    results = [pool.apply_async(mv_split, args=[hours, split]) for split in range(0, 110, 10)]
    output = [p.get() for p in results]
    pool.close()
    
    x_mv = [m[0] for m in output]
    filenames = [m[1] for m in output]
    y_mv = []

    for filename in filenames:
        data = parseDataLite(filename)
        os.remove(filename)
        interactions = data['vru_interactions']
        y_mv.append(interactions/hours)

    end = dt.datetime.now()

    with open(outfile, "w") as file:
        data = {
            "x_bikes": x_bikes,
            "y_bikes": y_bikes,
            "x_peds": x_peds,
            "y_peds": y_peds,
            "x_mv": x_mv,
            "y_mv": y_mv,
            "start": str(start),
            "end": str(end),
            "cmd": ["python main.py -sd 1 -t time -c 0 -vp split > filename", "python main.py -sd 1 -t time -p 0 -vp split > filename", "python main.py -sd 1 -t time -vp split > filename"]
        }

        json.dump(data, file, indent=4)
    return end

if __name__ == '__main__':
    start = dt.datetime.now()
    end = volume(start, "data/volume.json", 2500)
    print(end - start)