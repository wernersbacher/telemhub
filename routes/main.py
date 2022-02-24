import pandas as pd
from flask import Blueprint, render_template, request, flash, url_for, send_from_directory
from flask_login import current_user
from werkzeug.utils import redirect
import utils
from database import db
from models.models import File, Car, Track
from routes.helpers.telem import telemetry_filtering
from sqlalchemy import func

main = Blueprint("main", __name__)

ROWS_PER_PAGE = 10
ALLOWED_EXTENSIONS = {'ld', "ldx"}


@main.route('/')
def home():
    tracks = db.session.query(Car).all()
    top_cars = sorted(tracks, key=lambda car: car.get_files_number(), reverse=True)[-10:]

    tracks = db.session.query(Track).all()
    top_tracks = sorted(tracks, key=lambda track: track.get_files_number(), reverse=True)[-10:]

    number_of_files = db.session.query(File).count()

    number_of_views = db.session.query(func.sum(File.views)).first()[0]

    return render_template('main/home.html', top_cars=top_cars, top_tracks=top_tracks, number_of_files=number_of_files,
                           number_of_views=number_of_views)


@main.route('/telemetry')
def telemetry():
    telem_kwargs = telemetry_filtering(request)

    return render_template('main/telemetry.html', **telem_kwargs)


@main.route("/telemetry/show/<id>")
def telemetry_show(id):
    """ shows one telemetry page """
    file = db.session.query(File).filter_by(id=id).first()
    if file is None:
        flash("Sorry, this telemetry doesn't exist (anymore)!", category="danger")
        return redirect(url_for('main.home'))

    db.session.commit()
    # update views with locking to avoid racing conditions
    file_up = File.query.with_for_update(of=File, nowait=True).filter(File.id == id).first()
    file_up.views = utils.increment_without_error(file_up.views)
    db.session.commit()

    return render_template("main/telemetry_show.html", file=file)


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
