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

from logger import logger_worker as logger


def process_upload(file_path: str, user: User, readme_path: str):
    try:
        _process_upload(file_path, user, readme_path)
    except BaseException:
        logger.error(traceback.format_exc())


def _process_upload(file_path: str, user: User, readme_path: str):
    logger.info(f" --------- processing file {file_path} in background from user {user.username}")
    logger.info("1")
    path_only, file_name_with_ext = os.path.split(file_path)
    logger.info("2")
    file_name, file_ext = os.path.splitext(file_name_with_ext)
    logger.info("3")
    parquet_path = os.path.join(path_only, f"{file_name}.parquet")
    logger.info("4")
    ldx_path = os.path.splitext(file_path)[0] + ".ldx"
    logger.info("5")
    zip_path = os.path.splitext(file_path)[0] + ".zip"
    logger.info("6")

    logger.info("Created path names")

    head, chans = ldp.read_ldfile(file_path)

    logger.info("Loaded head and channel from file")

    if head.event == "AC_LIVE":
        logger.error("Detected wrong ld file, aborting")
        os.remove(file_path)
        os.remove(ldx_path)
        return

    # print(type(head))
    # print(head.venue)  # track
    # print(head.event)  # car

    # read laps from xml files
    laps = np.array(telemetry.laps(file_path))
    logger.info("Read laps")
    # create DataStore that is used later to get pandas DataFrame
    ds = telemetry.LDDataStore(chans, laps, freq=20, acc=head.event != 'AC_LIVE')

    # print(ds.laps_times)
    fastest_lap_time = min(ds.laps_times)
    # print(f"fastest lap was {fastest_lap_time}")
    fastest_lap_ix = ds.laps_times.index(fastest_lap_time)
    # print(fastest_lap_ix)
    fastest_lap = ds.get_data_frame(lap=fastest_lap_ix)
    # print(fastest_lap.keys())

    logger.info("Got fastest lap from data.")

    # print(fastest_lap[["speedkmh", "dist_lap", "time_lap"]])

    car = db.session.query(Car).filter_by(internal_name=head.event).first()
    # check if car exists
    if car is None:
        car = Car(internal_name=head.event)

    # -------------------------------- CAR
    # try to write car
    logger.info("trying to add car.")
    db.session.begin_nested()
    try:
        db.session.add(car)
        db.session.commit()
    except IntegrityError as e:
        # if it fails another one has written the car, so now just load
        db.session.rollback()
        car = db.session.query(Car).filter_by(internal_name=head.event).first()
    except BaseException as e:
        logger.error(traceback.format_exc())

    # -------------------------------- TRACK
    logger.info("trying to add track.")
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
    except BaseException as e:
        logger.error(traceback.format_exc())

    # -------------------------------- FILE
    # print("saving telemetry file to db...")
    fastest_lap[["speedkmh", "throttle", "brake", "dist_lap", "time_lap"]].to_parquet(path=parquet_path, index=True)

    try:
        logger.info(f"writing file to database SUCEEDED, {file_path}")
        file = File(owner=user, car=car, track=track, filename=file_name, fastest_lap_time=fastest_lap_time)
        db.session.add(file)
        db.session.commit()
    except:
        logger.error(f"writing file to database FAILED, {file_path}")
        logger.error(traceback.format_exc())
        with contextlib.suppress(FileNotFoundError):
            os.remove(file_path)
            os.remove(ldx_path)
            os.remove(parquet_path)
        return

    # if everything worked well, create zip file
    with zipfile.ZipFile(zip_path, 'w') as zipF:
        zipF.write(file_path, basename(file_path), compress_type=zipfile.ZIP_DEFLATED)
        zipF.write(ldx_path, basename(ldx_path), compress_type=zipfile.ZIP_DEFLATED)
        logger.info(f"now adding readme file {readme_path}")
        try:
            zipF.write(readme_path, basename(readme_path), compress_type=zipfile.ZIP_DEFLATED)
        except BaseException:
            logger.error(traceback.format_exc())

    # now delete big raw files!
    os.remove(file_path)
    os.remove(ldx_path)

    logger.info(f" --------- finished processing file {file_path} in background from user {user.username}")
