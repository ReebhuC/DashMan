from flask import Blueprint, request, jsonify, render_template
from . import db
from .models import Incident

api_bp = Blueprint("api", __name__)

# Existing API routes
@api_bp.route("/events", methods=["POST"])
def create_event():
    data = request.get_json() or {}
    required_fields = ["trip_id", "timestamp", "anomaly_type"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    from datetime import datetime

    incident = Incident(
        trip_id=data["trip_id"],
        timestamp=datetime.fromisoformat(data["timestamp"]),
        anomaly_type=data["anomaly_type"],
        speed=data.get("speed"),
        acceleration=data.get("acceleration"),
        lat=data.get("lat"),
        lng=data.get("lng"),
    )

    db.session.add(incident)
    db.session.commit()
    return jsonify({"id": incident.id}), 201

@api_bp.route("/incidents", methods=["GET"])
def list_incidents():
    incidents = Incident.query.order_by(Incident.timestamp.desc()).all()
    result = []
    for inc in incidents:
        result.append({
            "id": inc.id,
            "trip_id": inc.trip_id,
            "timestamp": inc.timestamp,
            "speed": inc.speed,
            "acceleration": inc.acceleration,
            "lat": inc.lat,
            "lng": inc.lng,
        })
    return jsonify(result), 200

# NEW: Frontend routes (added to existing file)
@api_bp.route("/")
def home():
    return render_template("index.html")

@api_bp.route("/incidents-page")
def incidents_page():
    # Fetch real incidents from database
    incidents_data = Incident.query.order_by(Incident.timestamp.desc()).all()
    
    # Format for template
    formatted_incidents = []
    for inc in incidents_data:
        formatted_incidents.append({
            "time": inc.timestamp,
            "type": "harsh_brake" if inc.acceleration and inc.acceleration < 0 else "harsh_accel",
            "speed": inc.speed or "N/A",
            "location": f"{inc.lat}, {inc.lng}" if inc.lat and inc.lng else "Unknown"
        })
    
    return render_template("incidents.html", incidents=formatted_incidents)