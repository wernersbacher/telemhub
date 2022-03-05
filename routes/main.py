import os
from flask import Blueprint, render_template, request, flash, url_for, send_from_directory
from werkzeug.utils import redirect
import utils
from database import db
from models.models import File, Car, Track
from models.news import News
from routes.helpers.extensions import render_template_extra
from routes.helpers.telem import telemetry_filtering
from sqlalchemy import func

main = Blueprint("main", __name__)

ROWS_PER_PAGE = 30
ALLOWED_EXTENSIONS = {'ld', "ldx"}


@main.route("/")
def home():
    return redirect(url_for("main.telemetry"))


@main.route('/welcome')
def welcome():
    tracks = db.session.query(Car).all()
    top_cars = sorted(tracks, key=lambda car: car.get_files_number(), reverse=True)[-10:]

    tracks = db.session.query(Track).all()
    top_tracks = sorted(tracks, key=lambda track: track.get_files_number(), reverse=True)[-10:]

    number_of_files = db.session.query(File).count()

    number_of_views = db.session.query(func.sum(File.views)).first()[0]

    latest_news = db.session.query(News).first()

    return render_template_extra('main/home.html', top_cars=top_cars, top_tracks=top_tracks,
                                 number_of_files=number_of_files,
                                 number_of_views=number_of_views, news=latest_news)


@main.route('/telemetry')
def telemetry():
    telem_kwargs = telemetry_filtering(request)

    return render_template_extra('main/telemetry.html', **telem_kwargs)


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

    return render_template_extra("main/telemetry_show.html", file=file)


@main.route("/telemetry/download/<id>")
def download_telem(id):
    file = db.session.query(File).filter_by(id=id).first()
    if file is None:
        flash("Sorry, this telemetry doesn't exist (anymore)!", category="danger")
        return redirect(url_for('main.home'))

    try:
        file_path = file.get_path_zip()
        path_only, file_name_with_ext = os.path.split(file_path)
        return send_from_directory(path_only, path=file_name_with_ext, as_attachment=True)
    except FileNotFoundError:
        flash("Sorry, this telemetry doesn't exist (anymore)!", category="danger")
        return redirect(url_for('main.home'))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
