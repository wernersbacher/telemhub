from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from database import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    pass_hash = db.Column(db.String(128))

    myFiles = db.relationship('File', backref='owner', lazy='dynamic')

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
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'))


    fastest_lap_time = db.Column(db.Float)
    likes = db.Column(db.Integer)

    def __repr__(self):
        return '<File {}>'.format(self.filename)

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    internal_name = db.Column(db.String(50), nullable=False)
