from wtforms import Form, MultipleFileField, SubmitField


class TelemUploadForm(Form):
    files = MultipleFileField('File(s) Upload')
    submit = SubmitField('Upload telemetry')
