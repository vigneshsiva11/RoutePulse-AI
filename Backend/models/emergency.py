from utils.db import db


class Emergency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    detected = db.Column(db.Boolean, default=False)
    lane = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
