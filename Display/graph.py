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

def speed(data):
    x = data['x']
    y = data['y']
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

def length(data):
    x = data['x']
    y = data['y']
    fig = plt.figure()
    ax1 = fig.add_subplot()
    ax1.set_xlabel("Facility Length (m)")
    ax1.set_ylabel("MVxMVxVRU Interactions/Hour")
    ax1.set_title("Influence of Varying Facility Length")
    ax1.plot(x, y)
    plt.show()

def volume(data):
    x_bikes = data['x_bikes']
    y_bikes = data['y_bikes']

    fig = plt.figure()
    ax1 = fig.add_subplot()
    ax1.set_xlabel("VRU Volume/HR")
    ax1.set_ylabel("MVxMVxVRU Interactions/Hour")
    ax1.set_title("Influence of Varying VRU Volumes")
    ax1.plot(x_bikes, y_bikes, 'b')

    
    x_peds = data['x_peds']
    y_peds = data['y_peds']

    ax1.plot(x_peds, y_peds, 'r')
    ax1.legend(['Bicycles', 'Pedestrians'])
    plt.show()

def dir_split(data):
    x_bikes = data['x_bikes']
    y_bikes = data['y_bikes']

    fig = plt.figure()
    ax1 = fig.add_subplot()
    ax1.set_xlabel("Percent of Motor Vehicles Traveling East")
    ax1.set_ylabel("MVxMVxVRU Interactions/Hour")
    ax1.set_title("Influence of Varying Directional Splits")
    ax1.plot(x_bikes, y_bikes, 'b')

    x_peds = data['x_peds']
    y_peds = data['y_peds']

    ax1.plot(x_peds, y_peds, 'r')

    x_mv = data['x_mv']
    y_mv = data['y_mv']

    ax1.plot(x_mv, y_mv, 'g')
    ax1.legend(['Bicycles', 'Pedestrians', 'All'])

    plt.show()

if __name__ == "__main__":
    filename = "data/length.json"
    with open(filename, "r") as file:
        data = json.load(file)
        length(data)