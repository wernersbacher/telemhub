from datetime import datetime

from database import db


class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text())
    message = db.Column(db.Text())
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def get_date(self):
        return self.timestamp.strftime("%m/%d/%Y, %H:%M")
