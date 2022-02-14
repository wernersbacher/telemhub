from flask import current_app
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from loginmanager import login_manager
from database import db
from flask_login import UserMixin
import os


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    pass_hash = db.Column(db.String(128))

    myFiles = db.relationship('File', backref='owner', lazy='dynamic')

    def set_pass(self, password):
        self.pass_hash = generate_password_hash(password)

    def check_pass(self, password):
        return check_password_hash(self.pass_hash, password)

    def get_telemetry_path(self):
        return os.path.join(current_app.config.get('UPLOADS'), str(self.username))

    def __repr__(self):
        return '<User {}>'.format(self.username)


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    car_id = db.Column(db.Integer, db.ForeignKey('car.id'))
    track_id = db.Column(db.Integer, db.ForeignKey('track.id'))

    fastest_lap_time = db.Column(db.Float)
    likes = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<File {}>'.format(self.filename)


class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    internal_name = db.Column(db.String(50), nullable=False)
    pretty_name = db.Column(db.String(50))
    files = db.relationship('File', backref='car', lazy='dynamic')


class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    internal_name = db.Column(db.String(50), nullable=False)
    pretty_name = db.Column(db.String(50))
    files = db.relationship('File', backref='track', lazy='dynamic')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
