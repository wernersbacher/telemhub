from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, validators


class ContactForm(FlaskForm):
    name = StringField("Name", [validators.DataRequired()])
    email = StringField("Email", [validators.DataRequired(), validators.Email()])
    subject = StringField("Subject", [validators.DataRequired()])
    message = TextAreaField("Message", [validators.DataRequired()])
    submit = SubmitField("Send")
