from flask import Blueprint
from flask import render_template

from models.models import User

main = Blueprint("main", __name__)


@main.route('/')
def index():
    #user = User()
    return render_template('index.html')
