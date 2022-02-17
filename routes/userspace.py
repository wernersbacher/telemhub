from flask import render_template, url_for, redirect, request, Blueprint, flash
from database import db
from flask_login import login_user, logout_user, current_user, login_required
from forms.auth import RegistrationForm, LoginForm, PasswordForm
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
            flash('You were successfully logged in.', category="success")
            return redirect(redirect_url)

    return render_template('login.html', form=form)


@userspace.route('/logout')
def logout():
    logout_user()
    flash("Logged out, see you soon.", category="success")
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


@userspace.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def profile_edit():
    """ TODO: Schreiben der Adresse mit race conditions"""

    form = PasswordForm(request.form)

    if request.method == 'POST' and form.validate():
        current_user.email = form.email.data
        db.session.commit()
        flash("Email set successfully.", category="success")
    else:
        form.email.data = current_user.email

    return render_template('userspace/edit_profile.html', form=form)
