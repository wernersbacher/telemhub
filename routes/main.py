from flask import Blueprint, g, render_template

from flask_login import current_user, login_required


main = Blueprint("main", __name__)


@main.before_request
def before_request():
    g.user = current_user


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/upload')
@login_required
def home():
    return render_template('upload.html')
