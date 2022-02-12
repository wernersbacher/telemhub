from flask import session
from models.models import User


def is_logged_in():
    if 'userID' in session:
        user = User.query.get(session['userID'])
        if user:
            return True
    return False
