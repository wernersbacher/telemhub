from models.models import User
from logic import telemetry
from logic import ldparser as ldp
import numpy as np

def process_upload(file_path: str, user: User):
    print(f"processed file {file_path} in background from user {user.username}")


    head, chans = ldp.read_ldfile(file_path)
    print(type(head))
    print(head.venue)
    print(head.event)

    # read laps from xml files
    laps = np.array(telemetry.laps(file_path))

    # create DataStore that is used later to get pandas DataFrame
    ds = telemetry.LDDataStore(chans, laps, freq=10, acc=head.event != 'AC_LIVE')
    
    print(ds.laps_times)
    fastest_lap_time = min(ds.laps_times)
    print(f"fastest lap was {fastest_lap_time}")
    fastest_lap_ix = ds.laps_times.index(fastest_lap_time)
    #print(fastest_lap_ix)
    fastest_lap = ds.get_data_frame(lap=fastest_lap_ix)
    #print(fastest_lap.keys())

    print(fastest_lap[["speedkmh", "dist_lap", "time_lap"]])

