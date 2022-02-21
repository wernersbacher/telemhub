from wtforms import Form, MultipleFileField, SubmitField
from wtforms.validators import DataRequired


class TelemUploadForm(Form):
    files = MultipleFileField('File(s) Upload')

    submit = SubmitField('Upload telemetry')
