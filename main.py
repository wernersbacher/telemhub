import os
from itertools import groupby

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import ldparser as ldp
import telemetry

CUR_DIR = os.path.dirname(__file__)

TELEM_DIR = os.path.join(CUR_DIR, "telem")


def list_files():
    for root, dirs, files in os.walk(TELEM_DIR, topdown=False):
        for name in files:
            if name.endswith(".ld"):
                source_file = os.path.join(root, name)
                yield source_file


def plot_file_debug(file_path):
    l = ldp.ldData.fromfile(file_path)
    print(l.head)
    print(list(map(str, l)))
    print()

    # create plots for all channels with the same frequency
    for f, g in groupby(l.channs, lambda x: x.freq):

        df = pd.DataFrame({i.name.lower(): i.data for i in g})
        print(df.keys())
        print(df.values)
        if len(df) > 0:
            df.plot()
            plt.show()


for file in list_files():
    #plot_file_debug(file)

    head_, chans = ldp.read_ldfile(file)

    # read laps from xml files
    laps = np.array(telemetry.laps(file))

    # create DataStore that is used later to get pandas DataFrame
    ds = telemetry.LDDataStore(chans, laps, acc=head_.event != 'AC_LIVE')

    """ Problem: Die Daten sind nach zeit, nicht nach distanz konstruiert"""

    print(ds.laps_times)
    fastest_lap_ix = ds.laps_times.index(min(ds.laps_times))
    print(fastest_lap_ix)
    fastest_lap = ds.get_data_frame(lap=fastest_lap_ix)
    print(fastest_lap.keys())
    print(fastest_lap[["speedkmh", "dist_lap", "time_lap"]])

    #fastest_lap[["speedkmh", "throttle", "brake"]].plot()
    #plt.show()




print("Done")
