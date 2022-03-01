from flask import render_template, url_for, redirect, request, Blueprint, flash
from database import db
from flask_login import login_user, logout_user, current_user, login_required
from forms.auth import RegistrationForm, LoginForm, UpdateEmailForm, UpdatePasswordForm
from models.models import User
import config as cfg
from routes.helpers.extensions import render_template_extra

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

    return render_template('userspace/login.html', form=form)


@userspace.route('/logout')
def logout():
    logout_user()
    flash("Logged out, see you soon.", category="success")
    return redirect(url_for('main.home'))


@userspace.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)

    if not cfg.get(cfg.Setting.REGISTRATION_ENABLED):
        flash("Registration is currently disabled.", category="danger")
        return render_template('userspace/register.html', form=form)

    if request.method == 'POST' and form.validate():
        user = User(username=form.username.data, email=form.email.data)
        user.set_pass(form.password.data)

        db.session.add(user)
        db.session.commit()
        flash('Registration completed, you can now log in!')
        return redirect(url_for('userspace.login'))

    return render_template('userspace/register.html', form=form)


@userspace.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def profile_edit():
    """ TODO: Schreiben der Adresse mit race conditions
            both validators are getting triggered even when on same page?
    """

    emailForm = UpdateEmailForm(request.form)
    passwordForm = UpdatePasswordForm(request.form)

    if emailForm.validate_on_submit():
        current_user.email = emailForm.email.data
        db.session.commit()
        flash("Email set successfully.", category="success")

    elif passwordForm.validate_on_submit():
        current_user.set_pass(passwordForm.new_password.data)
        db.session.commit()
        flash("New Password set successfully.", category="success")
    else:
        emailForm.email.data = current_user.email

    return render_template_extra('userspace/edit_profile.html', passwordForm=passwordForm, emailForm=emailForm)
