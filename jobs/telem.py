from models.models import User, File, Car, Track
from logic import telemetry
from logic import ldparser as ldp
import numpy as np
from database import db
import os
import traceback


def process_upload(file_path: str, user: User):
    print(f"processed file {file_path} in background from user {user.username}")
    path_only, file_name = os.path.split(file_path)
    file_name, file_ext = os.path.splitext(file_name)
    parquet_path = os.path.join(path_only, f"{file_name}.parquet")

    head, chans = ldp.read_ldfile(file_path)
    print(type(head))
    print(head.venue)  # track
    print(head.event)  # car

    # read laps from xml files
    laps = np.array(telemetry.laps(file_path))

    # create DataStore that is used later to get pandas DataFrame
    ds = telemetry.LDDataStore(chans, laps, freq=10, acc=head.event != 'AC_LIVE')

    print(ds.laps_times)
    fastest_lap_time = min(ds.laps_times)
    print(f"fastest lap was {fastest_lap_time}")
    fastest_lap_ix = ds.laps_times.index(fastest_lap_time)
    # print(fastest_lap_ix)
    fastest_lap = ds.get_data_frame(lap=fastest_lap_ix)
    # print(fastest_lap.keys())

    # print(fastest_lap[["speedkmh", "dist_lap", "time_lap"]])

    car = db.session.query(Car.id).filter_by(internal_name=head.event).first()
    # check if car exists
    if car is None:
        car = Car(internal_name=head.event)

    track = db.session.query(Track.id).filter_by(internal_name=head.venue).first()
    if track is None:
        track = Track(internal_name=head.venue)

    try:
        fastest_lap[["speedkmh", "dist_lap", "time_lap"]].to_parquet(path=parquet_path, index=True)

        file = File(owner=user, car=car, track=track, filename=file_name, fastest_lap_time=fastest_lap_time)

        db.session.add(car)
        db.session.add(track)
        db.session.add(file)
    except:
        print(traceback.format_exc())
    db.session.commit()
