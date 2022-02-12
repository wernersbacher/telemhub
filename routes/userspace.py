from flask import render_template, g, url_for, redirect, request, Blueprint, current_app
from database import db
from flask_login import login_user, logout_user
from forms.auth import RegistrationForm, LoginForm
from models.models import User
from flask_login import current_user, login_required

import os

userspace = Blueprint("userspace", __name__)


@userspace.before_request
def before_request():
    g.user = current_user


@userspace.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_pass(form.password.data):
            login_user(user)
            redirect_url = request.args.get('next') or url_for('main.index')
            return redirect(redirect_url)

    return render_template('login.html', form=form)


@userspace.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@userspace.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)

    if request.method == 'POST' and form.validate():
        user = User(username=form.username.data, email=form.email.data)
        user.set_pass(form.password.data)

        db.session.add(user)
        os.makedirs(current_app.config.get('UPLOADS') + "/" + form.username.data)
        db.session.commit()
        return redirect(url_for('userspace.login'))

    return render_template('register.html', form=form)
