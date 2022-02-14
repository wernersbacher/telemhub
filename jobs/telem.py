import contextlib
from sqlalchemy.exc import IntegrityError
from models.models import User, File, Car, Track
from logic import telemetry
from logic import ldparser as ldp
import numpy as np
from database import db
import os
import traceback


def process_upload(file_path: str, user: User):
    print(f"processing file {file_path} in background from user {user.username}")
    path_only, file_name = os.path.split(file_path)
    file_name, file_ext = os.path.splitext(file_name)
    parquet_path = os.path.join(path_only, f"{file_name}.parquet")
    ldx_path = os.path.splitext(file_path)[0] + ".ldx"

    head, chans = ldp.read_ldfile(file_path)
    # print(type(head))
    # print(head.venue)  # track
    # print(head.event)  # car

    # read laps from xml files
    laps = np.array(telemetry.laps(file_path))

    # create DataStore that is used later to get pandas DataFrame
    ds = telemetry.LDDataStore(chans, laps, freq=10, acc=head.event != 'AC_LIVE')

    # print(ds.laps_times)
    fastest_lap_time = min(ds.laps_times)
    # print(f"fastest lap was {fastest_lap_time}")
    fastest_lap_ix = ds.laps_times.index(fastest_lap_time)
    # print(fastest_lap_ix)
    fastest_lap = ds.get_data_frame(lap=fastest_lap_ix)
    # print(fastest_lap.keys())

    # print(fastest_lap[["speedkmh", "dist_lap", "time_lap"]])

    car = db.session.query(Car).filter_by(internal_name=head.event).first()
    # check if car exists
    if car is None:
        car = Car(internal_name=head.event)

    # -------------------------------- CAR
    # try to write car
    db.session.begin_nested()
    try:
        db.session.add(car)
        db.session.commit()
    except IntegrityError as e:
        # if it fails another one has written the car, so now just load
        db.session.rollback()
        car = db.session.query(Car).filter_by(internal_name=head.event).first()
    except BaseException as e:
        print(traceback.format_exc())

    # -------------------------------- TRACK
    # print("Get or updating track...")
    track = db.session.query(Track).filter_by(internal_name=head.venue).first()
    if track is None:
        track = Track(internal_name=head.venue)

    db.session.begin_nested()
    try:
        db.session.add(track)
        db.session.commit()
    except IntegrityError as e:
        # if it fails another one has written the track, so now just load
        db.session.rollback()
        track = db.session.query(Track).filter_by(internal_name=head.venue).first()

    # -------------------------------- FILE
    # print("saving telemetry file to db...")
    fastest_lap[["speedkmh", "dist_lap", "time_lap"]].to_parquet(path=parquet_path, index=True)

    try:
        print(f"writing file to database SUCEEDED, {file_path}")
        file = File(owner=user, car=car, track=track, filename=file_name, fastest_lap_time=fastest_lap_time)
        db.session.add(file)
        db.session.commit()
    except:
        print(f"writing file to database FAILED, {file_path}")
        print(traceback.format_exc())
        with contextlib.suppress(FileNotFoundError):
            os.remove(file_path)
            os.remove(ldx_path)
            os.remove(parquet_path)
