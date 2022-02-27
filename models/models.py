import string
from enum import Enum
import random

from flask import current_app
from datetime import datetime, time

from flask_sqlalchemy import xrange
from werkzeug.security import generate_password_hash, check_password_hash

from helpers.helpers import length
from loginmanager import login_manager
from database import db
from flask_login import UserMixin
import os


def random_dir():
    return ''.join(random.choice(string.ascii_lowercase) for i in xrange(5))


class Roles(Enum):
    USER = 0
    ADMIN = 10


class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    pass_hash = db.Column(db.String(128))
    role = db.Column(db.Integer, default=Roles.USER.value)

    myFiles = db.relationship('File', backref='owner', lazy='dynamic')

    def get_role(self):
        try:
            role = Roles(self.role)
        except:
            role = Roles.USER
        return role

    def set_role(self, role: Roles):
        self.role = role.value

    def is_admin(self):
        return self.get_role() == Roles.ADMIN

    def set_pass(self, password):
        self.pass_hash = generate_password_hash(password)

    def check_pass(self, password):
        return check_password_hash(self.pass_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    folder_name = db.Column(db.String(120), nullable=False, default=random_dir)

    public = db.Column(db.Boolean, default=True)

    car_id = db.Column(db.Integer, db.ForeignKey('car.id'))
    track_id = db.Column(db.Integer, db.ForeignKey('track.id'))

    fastest_lap_time = db.Column(db.Float)
    likes = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)

    def get_upload_date(self):
        return self.timestamp.isoformat()

    def get_fastest_lap(self):
        ms = int(1000 * (self.fastest_lap_time % 1))*1000
        seconds = int(self.fastest_lap_time % 60)
        minutes = int(self.fastest_lap_time // 60)
        s = str(time(minute=minutes, second=seconds, microsecond=ms).strftime("%M:%S,%f"))
        return s[:-3]

    def get_path_parquet(self):
        if self.owner is not None:
            return os.path.join(current_app.config.get('PARQUETFILES'), self.folder_name, self.id+".parquet")
        return False

    def get_path_zip(self):
        if self.owner is not None:
            return os.path.join(current_app.config.get('TELEFILES'), self.folder_name, self.id+".zip")
        return False

    def __repr__(self):
        return '<File {}>'.format(self.filename)


class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    internal_name = db.Column(db.String(50), unique=True, nullable=False)
    pretty_name = db.Column(db.String(50))
    files = db.relationship('File', backref='car', lazy='dynamic')

    def get_files_number(self):
        return len(list(self.files))

    def get_pretty_name(self):
        if length(self.pretty_name) > 0:
            return self.pretty_name
        return self.internal_name

    def __repr__(self):
        return f'<Car {self.id}, {self.internal_name}>'


class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    internal_name = db.Column(db.String(50), unique=True, nullable=False)
    pretty_name = db.Column(db.String(50))
    files = db.relationship('File', backref='track', lazy='dynamic')

    def get_files_number(self):
        return len(list(self.files))

    def get_pretty_name(self):
        if length(self.pretty_name) > 0:
            return self.pretty_name
        return self.internal_name

    def __repr__(self):
        return f'<Track {self.id}, {self.internal_name}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
