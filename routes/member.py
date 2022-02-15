from flask import render_template, url_for, redirect, request, Blueprint, current_app, flash
from sqlalchemy import and_
from werkzeug.utils import secure_filename
from database import db
from flask_login import login_required, current_user
from executor import executor
from forms.uploads import TelemUploadForm
from jobs.telem import process_upload
from models.models import User, File, Car, Track
import os

member = Blueprint("member", __name__)

ROWS_PER_PAGE = 10


@member.route('/member/telemetry')
@login_required
def telemetry():
    page = request.args.get('page', 1, type=int)
    car_id = request.args.get('car', 0, type=int)
    track_id = request.args.get('track', 0, type=int)
    print(car_id, track_id)

    filters = [File.owner == current_user]
    if car_id > 0:
        filters.append(File.car_id == car_id)
    if track_id > 0:
        filters.append(File.track_id == track_id)

    files = db.session.query(File). \
        filter(and_(*filters)). \
        order_by(File.fastest_lap_time). \
        paginate(page=page, per_page=ROWS_PER_PAGE)

    cars = db.session.query(Car).all()
    tracks = db.session.query(Track).all()

    return render_template('member/telemetry.html', files=files, cars=cars, tracks=tracks,
                           selected_track=track_id, selected_car=car_id)


@member.route('/member/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = TelemUploadForm()
    readme_path = os.path.join(current_app.config.get("UPLOADS"), "readme.txt")
    uploaded_files = []  # actual saved on db
    task_list = []

    files = request.files.getlist("files")

    if request.method == 'POST' and form.validate() and files:
        # get file names for ld and ldx files
        files_ld = [os.path.splitext(secure_filename(file.filename))[0]
                    for file in files
                    if secure_filename(file.filename).endswith("ld")]

        files_ldx = [os.path.splitext(secure_filename(file.filename))[0]
                     for file in files
                     if secure_filename(file.filename).endswith("ldx")]

        # check all files again
        for file in files:
            file_name = secure_filename(file.filename)
            file_name_base = os.path.splitext(file_name)[0]

            # only save file if corresponding file (ld/ldx) exists
            if file_name_base in files_ldx and files_ld:
                full_file_path = os.path.join(
                    *(current_user.get_telemetry_path(), file_name))  # super weird tuple workaround
                zip_file_path = os.path.splitext(full_file_path)[0] + ".zip"

                if os.path.isfile(zip_file_path):
                    flash(f"You have uploaded the file {file_name} already!", category="warning")
                else:
                    uploaded_files.append(file_name)
                    print(f"saved file to {full_file_path}")
                    file.save(full_file_path)

                    if file_name.endswith(".ld"):
                        task_list.append((process_upload, full_file_path, current_user, readme_path))

        # only process data after upload; otherwise errors may appear?
        if task_list:
            for task in task_list:
                executor.submit(*task)

        if uploaded_files:
            flash(f"{len(uploaded_files)} files were uploaded! It might take a few moments for them to show up.",
                  category="success")
        else:
            flash("No files were uploaded, please don't forget to upload both ld and ldx!", category="danger")

    return render_template('member/upload.html', form=form)
