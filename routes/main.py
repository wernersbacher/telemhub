import os

from flask import Blueprint, render_template, current_app, request, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

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
    print()

    if request.method == 'POST' and form.validate() and files:
        print("verarbeite daten..")
        # get file names for ld and ldx files
        files_ld = [os.path.splitext(secure_filename(file.filename))[0]
                    for file in files
                    if secure_filename(file.filename).endswith("ld")]

        files_ldx = [os.path.splitext(secure_filename(file.filename))[0]
                     for file in files
                     if secure_filename(file.filename).endswith("ldx")]

        print(files_ld)
        print(files_ldx)

        # check all files again
        for file in files:
            file_name = secure_filename(file.filename)
            file_name_base = os.path.splitext(file_name)[0]

            # only save file if corresponding file (ld/ldx) exists
            if file_name_base in files_ldx and files_ld:
                uploaded_files.append(file_name)
                print(f"trying to save file to ")
                file.save(current_user.get_telemetry_path())

        if uploaded_files:
            flash("Files were uploaded! Check your telemetry dashboard.")
        else:
            flash("No files were uploaded, please don't forget to upload both ld and ldx!", category="error")

    return render_template('upload.html', form=form, uploaded_files=uploaded_files)
