from . import db
from datetime import datetime

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'))
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)

class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
    # Metadata
    directory = db.Column(db.String(500))
    video_path = db.Column(db.String(500))
    
    # Telemetry
    max_speed = db.Column(db.Float, default=0.0)
    start_lat = db.Column(db.Float, default=0.0)
    start_lng = db.Column(db.Float, default=0.0)
    acceleration = db.Column(db.Float, default=0.0) # Added to match README usage
    
    # Counts
    sensor_count = db.Column(db.Integer, default=0)
    gps_count = db.Column(db.Integer, default=0)
    
    processed = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "max_speed": self.max_speed,
            "start_lat": self.start_lat,
            "start_lng": self.start_lng,
            "video_path": self.video_path
        }
