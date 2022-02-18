from wtforms import Form, BooleanField, StringField, PasswordField, validators, EmailField, SubmitField
from flask_wtf import FlaskForm
from wtforms_validators import AlphaNumeric
from flask_login import current_user
from models.models import User


class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25), AlphaNumeric()])
    email = EmailField('Email address', [validators.DataRequired(), validators.Email()])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])
    submit = SubmitField('Register!')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

    def validate(self, extra_validators=None):
        initial_validation = super(RegistrationForm, self).validate()
        if not initial_validation:
            print("inital validation failed")
            return False

        if self.password.data != self.confirm.data:
            self.password.errors.append("Passwords do not match!")
            print("pw fail1")
            return False

        if len(self.password.data) < 7:
            self.password.errors.append("Password is shorter than 6 chars!")
            print("pw fail 2")
            return False

        user = User.query.filter_by(username=self.username.data).first()
        if user:
            self.username.errors.append("Username already registered")
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append("Email already registered")
            return False
        return True


class LoginForm(Form):
    email = EmailField('Email address', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', [validators.DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

    def validate(self, extra_validators=None):
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if not user:
            self.email.errors.append('Unknown email')
            return False
        if not user.check_pass(self.password.data):
            self.password.errors.append('Invalid password')
            return False
        return True


class UpdateEmailForm(FlaskForm):
    email = EmailField('Email address', [validators.DataRequired(), validators.Email()])
    submit = SubmitField('Update email')

    def __init__(self, *args, **kwargs):
        super(UpdateEmailForm, self).__init__(*args, **kwargs)

    def validate(self, extra_validators=None):
        print("current data:")
        print(self.email.data)
        initial_validation = super(UpdateEmailForm, self).validate()

        if not initial_validation:
            return False

        if current_user.email == self.email.data:
            self.email.errors.append("It's the same address!")
            return False

        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append("Email already registered")
            return False
        return True


class UpdatePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', [validators.DataRequired()])
    new_password = PasswordField('New Password', [validators.DataRequired()])
    confirm_password = PasswordField('Repeat New Password', [validators.DataRequired()])
    submit = SubmitField('Update password')

    def __init__(self, *args, **kwargs):
        super(UpdatePasswordForm, self).__init__(*args, **kwargs)

    def validate(self, extra_validators=None):
        initial_validation = super(UpdatePasswordForm, self).validate()
        if not initial_validation:
            print("inital validation failed")
            return False

        if not current_user.check_pass(self.old_password.data):
            self.old_password.errors.append('Invalid password')
            return False

        if self.new_password.data != self.confirm_password.data:
            self.new_password.errors.append("Passwords do not match!")
            print("pw fail1")
            return False

        if len(self.new_password.data) < 7:
            self.new_password.errors.append("Password is shorter than 6 chars!")
            print("pw fail 2")
            return False

        return True
