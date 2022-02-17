from wtforms import Form, BooleanField, StringField, PasswordField, validators, EmailField, SubmitField
from wtforms_validators import AlphaNumeric

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


class PasswordForm(Form):
    email = EmailField('Email address', [validators.DataRequired(), validators.Email()])
    submit = SubmitField('Update email')

    def __init__(self, *args, **kwargs):
        super(PasswordForm, self).__init__(*args, **kwargs)

    def validate(self, extra_validators=None):
        print("current data:")
        print(self.email.data)
        initial_validation = super(PasswordForm, self).validate()
        if not initial_validation:
            print("inital validation failed")
            return False

        user = User.query.filter_by(email=self.email.data).first()
        if user:
            print("failed")
            self.email.errors.append("Email already registered")
            return False
        return True
