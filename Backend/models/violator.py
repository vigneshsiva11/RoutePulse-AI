from utils.db import db


class Violator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number_plate = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    fine = db.Column(db.Integer, default=500)
