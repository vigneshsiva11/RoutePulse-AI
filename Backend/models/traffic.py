from utils.db import db


class Traffic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lane = db.Column(db.String(50))
    vehicles = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
