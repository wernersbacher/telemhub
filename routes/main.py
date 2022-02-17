import os
from sqlalchemy import and_
import pandas as pd
from flask import Blueprint, render_template, request, flash, url_for, send_from_directory
from werkzeug.utils import redirect

import utils
from database import db
from logic.plot import create_telem_plot
from models.models import File, Car, Track

main = Blueprint("main", __name__)

ROWS_PER_PAGE = 10
ALLOWED_EXTENSIONS = {'ld', "ldx"}


@main.route('/')
def home():
    return render_template('index.html')


@main.route('/telemetry')
def telemetry():
    page = request.args.get('page', 1, type=int)
    car_id = request.args.get('car', 0, type=int)
    track_id = request.args.get('track', 0, type=int)
    print(car_id, track_id)

    filter = []
    if car_id > 0:
        filter.append(File.car_id == car_id)
    if track_id > 0:
        filter.append(File.track_id == track_id)

    files = db.session.query(File). \
        filter(and_(*filter)).\
        order_by(File.fastest_lap_time).\
        paginate(page=page, per_page=ROWS_PER_PAGE)

    cars = db.session.query(Car).all()
    tracks = db.session.query(Track).all()

    return render_template('telemetry.html', files=files, cars=cars, tracks=tracks,
                           selected_track=track_id, selected_car=car_id)


@main.route("/telemetry/show/<id>")
def telemetry_show(id):
    print("Trying to load id")
    file = db.session.query(File).filter_by(id=id).first()
    if file is None:
        flash("Sorry, this telemetry doesn't exist (anymore)!", category="danger")
        return redirect(url_for('main.home'))

    db.session.commit()
    # update views with locking to avoid racing conditions
    file_up = File.query.with_for_update(of=File, nowait=True).filter(File.id == id).first()
    file_up.views = utils.increment_without_error(file_up.views)
    db.session.commit()

    # load fastest lap from disk
    parquet_path = file.get_path_parquet()

    df = pd.read_parquet(parquet_path)

    print(df)
    vplot = create_telem_plot(df)

    return render_template("telemetry_show.html", file=file, vplot=vplot)


@main.route("/telemetry/download/<id>")
def download_telem(id):
    file = db.session.query(File).filter_by(id=id).first()
    if file is None:
        flash("Sorry, this telemetry doesn't exist (anymore)!", category="danger")
        return redirect(url_for('main.home'))

    try:
        return send_from_directory(file.owner.get_telemetry_path(), path=file.filename + ".zip", as_attachment=True)
    except FileNotFoundError:
        flash("Sorry, this telemetry doesn't exist (anymore)!", category="danger")
        return redirect(url_for('main.home'))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


