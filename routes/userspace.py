from flask import render_template, session, url_for, redirect, request, Blueprint, current_app
#from auth.checks import is_logged_in
from database import db

from forms.auth import RegistrationForm
from models.models import User

import os

userspace = Blueprint("userspace", __name__)


@userspace.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':  # only show form
        return render_template('login.html')

    username = request.form.get('usrname', False)
    if not username:
        return "Please fill username!"
    password = request.form.get('psswd', False)
    if not password:
        return "Please fill password!"
    user = User.query.filter_by(username=username).first()
    if user is None:
        return "Invalid Username!"
    if not user.check_pass(password):
        return "Invalid Password!"
    session['userID'] = user.id
    return "1"


@userspace.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)

    if request.method == 'GET':  # only show form

        return render_template('register.html', form=form)

    if request.method == 'POST' and form.validate():
        user = User(username=form.username.data, email=form.email.data)
        user.set_pass(form.password.data)

        db.session.add(user)
        os.makedirs(current_app.config.get.config['UPLOADS'] + "/" + form.username.data)
        db.session.commit()
        return redirect(url_for('userspace.login'))

    return render_template('register.html', form=form)
