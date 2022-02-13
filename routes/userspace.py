from flask import render_template, url_for, redirect, request, Blueprint, current_app, flash
from database import db
from flask_login import login_user, logout_user
from forms.auth import RegistrationForm, LoginForm
from models.models import User
import os

userspace = Blueprint("userspace", __name__)


@userspace.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_pass(form.password.data):
            login_user(user)
            redirect_url = request.args.get('next') or url_for('main.home')
            flash('You were successfully logged in.')
            return redirect(redirect_url)

    return render_template('login.html', form=form)


@userspace.route('/logout')
def logout():
    logout_user()
    flash("Logged out, see you soon.")
    return redirect(url_for('main.home'))


@userspace.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)

    if request.method == 'POST' and form.validate():
        user = User(username=form.username.data, email=form.email.data)
        user.set_pass(form.password.data)

        db.session.add(user)
        db.session.commit()
        os.makedirs(user.get_telemetry_path())  # create user dir
        flash('Registration completed, you can now log in!')
        return redirect(url_for('userspace.login'))

    return render_template('register.html', form=form)
