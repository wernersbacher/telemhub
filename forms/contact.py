from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, validators


class ContactForm(FlaskForm):
    name = StringField("Name", [validators.DataRequired(), validators.Length(min=2, max=25)])
    email = StringField("Email", [validators.DataRequired(), validators.Length(min=2, max=25), validators.Email()])
    subject = StringField("Subject", [validators.DataRequired(), validators.Length(min=2, max=25)])
    message = TextAreaField("Message", [validators.DataRequired(), validators.Length(min=5, max=2000)])
    submit = SubmitField("Send")
