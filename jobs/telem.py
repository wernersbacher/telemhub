import contextlib
import zipfile
from os.path import basename

from flask import url_for
from sqlalchemy.exc import IntegrityError
from models.models import User, File, Car, Track
from logic import telemetry
from logic import ldparser as ldp
import numpy as np
from database import db
import os
import traceback

from logger import logger_worker as logger
import notifications


def process_upload(file_path: str, user: User, readme_path: str):
    try:
        _process_upload(file_path, user, readme_path)
    except BaseException:
        logger.error(traceback.format_exc())


def create_fail_notif(user, file_name, reason):
    # create success notification
    notif = notifications.create_notif(type=notifications.TELEM_FAIL, owner=user,
                                       fargs={"filename": file_name, "reason": reason})
    if not user.is_anon():
        print("user is not anonym", user.username)
        db.session.add(notif)
        db.session.commit()


def _process_upload(file_path_temp: str, user: User, readme_path: str):
    print("calling upload")
    logger.info(f" --------- processing file {file_path_temp} in background from user {user}")
    path_only, file_name_with_ext = os.path.split(file_path_temp)
    ldx_path = os.path.splitext(file_path_temp)[0] + ".ldx"

    file_name, file_ext = os.path.splitext(file_name_with_ext)
    head, chans = ldp.read_ldfile(file_path_temp)

    logger.info("Loaded head and channel from file")

    if head.event == "AC_LIVE":
        logger.error("Detected wrong ld file, aborting")
        os.remove(file_path_temp)
        os.remove(ldx_path)
        create_fail_notif(user, file_name, "Wrong game or wrong file format detected.")
        return

    # print(type(head))
    # print(head.venue)  # track
    # print(head.event)  # car

    # read laps from xml files
    laps = np.array(telemetry.laps(file_path_temp))
    logger.info("Read laps")
    # create DataStore that is used later to get pandas DataFrame
    ds = telemetry.LDDataStore(chans, laps, freq=30, acc=head.event != 'AC_LIVE')

    # print(ds.laps_times)
    fastest_lap_time = min(ds.laps_times)
    if fastest_lap_time < 20:
        logger.error("Fastest lap time is way too short, maybe the file way just empty! Aborting.")
        create_fail_notif(user, file_name, "No valid lap was found. Some files are empty, try to upload a different one.")
        return

    # print(f"fastest lap was {fastest_lap_time}")
    fastest_lap_ix = ds.laps_times.index(fastest_lap_time)
    # print(fastest_lap_ix)
    fastest_lap = ds.get_data_frame(lap=fastest_lap_ix)
    # print(fastest_lap.keys())

    logger.info("Got fastest lap from data.")

    # print(fastest_lap[["speedkmh", "dist_lap", "time_lap"]])

    db.session.begin_nested()

    if not user.is_authenticated:
        user = db.session.query(User).filter_by(role=1).first()

    # -------------------------------- CAR
    # try to write car
    car = db.session.query(Car).filter_by(internal_name=head.event).first()
    # check if car exists
    if car is None:
        car = Car(internal_name=head.event)
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
    track = db.session.query(Track).filter_by(internal_name=head.venue).first()
    if track is None:
        track = Track(internal_name=head.venue)
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

    try:
        file = File(owner=user, car=car, track=track, filename=file_name, fastest_lap_time=fastest_lap_time)
        db.session.add(file)
        db.session.commit()
        logger.info(f"Created file with id {file.id}")
        logger.info(f"writing file to database SUCEEDED, {file_path_temp}")
    except:
        logger.error(f"writing file to database FAILED, {file_path_temp}")
        logger.error(traceback.format_exc())
        with contextlib.suppress(FileNotFoundError):
            os.remove(file_path_temp)
            os.remove(ldx_path)
            create_fail_notif(user, file_name, "Could not create database entry!")
        return

    # create success notification
    notif = notifications.create_notif(type=notifications.TELEM_SUCCESS, owner=user,
                                       fargs={"car": car.get_pretty_name(), "track": track.get_pretty_name(), "filename": file_name,
                                        "show_url": url_for("main.telemetry_show", id=file.id)})
    if not user.is_anonymous:
        db.session.add(notif)
        db.session.commit()

    parquet_path = file.get_path_parquet()
    zip_path = file.get_path_zip()
    # create directories
    os.makedirs(os.path.dirname(parquet_path), exist_ok=True)
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)
    logger.info(f"parquet path: {parquet_path}")
    logger.info(f"zip_path: {zip_path}")

    # create parquet file
    fastest_lap[["speedkmh", "throttle", "brake", "dist_lap", "time_lap"]].to_parquet(path=parquet_path, index=True)

    # if everything worked well, create zip file
    with zipfile.ZipFile(zip_path, 'w') as zipF:
        zipF.write(file_path_temp, basename(file_path_temp), compress_type=zipfile.ZIP_DEFLATED)
        zipF.write(ldx_path, basename(ldx_path), compress_type=zipfile.ZIP_DEFLATED)
        logger.info(f"now adding readme file {readme_path}")
        try:
            zipF.write(readme_path, basename(readme_path), compress_type=zipfile.ZIP_DEFLATED)
        except BaseException:
            logger.error(traceback.format_exc())

    # now delete big raw files!
    os.remove(file_path_temp)
    os.remove(ldx_path)

    logger.info(f" --------- finished processing file {file_path_temp} in background from user {user.username}")
