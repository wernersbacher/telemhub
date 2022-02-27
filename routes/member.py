import os

from flask import render_template, request, Blueprint, current_app, flash, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename, redirect

from database import db
from executor import executor

from forms.uploads import TelemUploadForm
from jobs.telem import process_upload
from models.models import User
from routes.helpers.files import delete_telemetry
from routes.helpers.telem import telemetry_filtering

member = Blueprint("member", __name__)

ROWS_PER_PAGE = 10


@member.route('/member/telemetry', methods=('GET', 'POST'))
@login_required
def telemetry():
    """ shows personal uploaded telemetry"""

    if request.method == 'POST':
        # delete file?

        delete_id = request.form.get('file_id', -1, type=int)
        success = delete_telemetry(delete_id)
        if success:
            flash("File was deleted successfully.", category="success")
        else:
            flash("Something went wrong when deleting the file. Are you trying to hack us?", category="danger")

    telem_kwargs = telemetry_filtering(request, filter_by_user=current_user)

    return render_template('member/telemetry.html', **telem_kwargs)


@member.route('/member/profile/<username>')
def profile(username):
    """ shows user profile """
    user = db.session.query(User).filter_by(username=username).first()
    if user is None:
        flash("Sorry, this user doesn't exist (anymore)!", category="danger")
        return redirect(url_for('main.home'))

    telem_kwargs = telemetry_filtering(request, filter_by_user=user)

    return render_template("member/profile.html", user=user, **telem_kwargs)


@member.route('/member/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """ TODO: Datein in uploads schieben, dann verarbeiten und dann in telefiles schieben"""
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
