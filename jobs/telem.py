import contextlib
import zipfile
from os.path import basename

from sqlalchemy.exc import IntegrityError
from models.models import User, File, Car, Track
from logic import telemetry
from logic import ldparser as ldp
import numpy as np
from database import db
import os
import traceback


def process_upload(file_path: str, user: User, readme_path: str):
    print(f"processing file {file_path} in background from user {user.username}")
    path_only, file_name_with_ext = os.path.split(file_path)
    file_name, file_ext = os.path.splitext(file_name_with_ext)
    parquet_path = os.path.join(path_only, f"{file_name}.parquet")
    ldx_path = os.path.splitext(file_path)[0] + ".ldx"
    zip_path = os.path.splitext(file_path)[0] + ".zip"

    head, chans = ldp.read_ldfile(file_path)

    if head.event == "AC_LIVE":
        print("Detected wrong ld file, aborting")
        os.remove(file_path)
        os.remove(ldx_path)
        return

    # print(type(head))
    # print(head.venue)  # track
    # print(head.event)  # car

    # read laps from xml files
    laps = np.array(telemetry.laps(file_path))

    # create DataStore that is used later to get pandas DataFrame
    ds = telemetry.LDDataStore(chans, laps, freq=20, acc=head.event != 'AC_LIVE')

    # print(ds.laps_times)
    fastest_lap_time = min(ds.laps_times)
    # print(f"fastest lap was {fastest_lap_time}")
    fastest_lap_ix = ds.laps_times.index(fastest_lap_time)
    # print(fastest_lap_ix)
    fastest_lap = ds.get_data_frame(lap=fastest_lap_ix)
    # print(fastest_lap.keys())

    print("Got fastest lap from data.")

    # print(fastest_lap[["speedkmh", "dist_lap", "time_lap"]])

    car = db.session.query(Car).filter_by(internal_name=head.event).first()
    # check if car exists
    if car is None:
        car = Car(internal_name=head.event)

    # -------------------------------- CAR
    # try to write car
    print("trying to add car.")
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
    print("trying to add track.")
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
    fastest_lap[["speedkmh", "throttle", "brake", "dist_lap", "time_lap"]].to_parquet(path=parquet_path, index=True)

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
        return

    # if everything worked well, create zip file
    with zipfile.ZipFile(zip_path, 'w') as zipF:
        zipF.write(file_path, basename(file_path), compress_type=zipfile.ZIP_DEFLATED)
        zipF.write(ldx_path, basename(ldx_path), compress_type=zipfile.ZIP_DEFLATED)
        print(f"now adding readme file {readme_path}")
        try:
            zipF.write(readme_path, basename(readme_path), compress_type=zipfile.ZIP_DEFLATED)
        except BaseException:
            print(traceback.format_exc())


    # now delete big raw files!
    os.remove(file_path)
    os.remove(ldx_path)
