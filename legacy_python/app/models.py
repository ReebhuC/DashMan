from datetime import datetime
from . import db

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicle.id"), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)

class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trip.id"), nullable=False)

    timestamp = db.Column(db.DateTime, nullable=False)
    anomaly_type = db.Column(db.String(32), nullable=False)

    speed = db.Column(db.Float)
    acceleration = db.Column(db.Float)
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)


