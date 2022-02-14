import os

from flask import Blueprint, render_template, current_app, request, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from executor import executor
from jobs.telem import process_upload

from forms.uploads import TelemUploadForm

main = Blueprint("main", __name__)


@main.route('/')
def home():
    return render_template('index.html')


@main.route('/telemetry')
def telemetry():


    return render_template('telemetry.html')






ALLOWED_EXTENSIONS = {'ld', "ldx"}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = TelemUploadForm()
    uploaded_files = []  # actual saved on db

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
                full_file_path = os.path.join(*(current_user.get_telemetry_path(), file_name))  # super weird tuple workaround

                if os.path.isfile(full_file_path):
                    flash(f"You have uploaded the file {file_name} already!", category="warning")
                else:
                    uploaded_files.append(file_name)
                    print(f"saving file to {full_file_path}")
                    file.save(full_file_path)

                    if file_name.endswith(".ld"):
                        executor.submit(process_upload, full_file_path, current_user)

        if uploaded_files:
            flash("Files were uploaded! Check your telemetry dashboard.", category="success")
        else:
            flash("No files were uploaded, please don't forget to upload both ld and ldx!", category="error")

    return render_template('upload.html', form=form, uploaded_files=uploaded_files)
