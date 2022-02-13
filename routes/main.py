from flask import Blueprint, render_template

from flask_login import login_required


main = Blueprint("main", __name__)


@main.route('/')
def home():
    return render_template('index.html')


@main.route('/telemetry')
def telemetry():
    return render_template('telemetry.html')


@main.route('/upload')
@login_required
def upload():
    return render_template('upload.html')
