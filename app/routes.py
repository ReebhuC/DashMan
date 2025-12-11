from flask import Blueprint, request, jsonify
from . import db
from .models import Incident

api_bp = Blueprint("api", __name__)

@api_bp.route("/events", methods=["POST"])
def create_event():
    data = request.get_json() or {}

    required_fields = ["trip_id", "timestamp"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    incident = Incident(
        trip_id=data["trip_id"],
        timestamp=data.get("timestamp"),
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
        result.append(
            {
                "id": inc.id,
                "trip_id": inc.trip_id,
                "timestamp": inc.timestamp,
                "speed": inc.speed,
                "acceleration": inc.acceleration,
                "lat": inc.lat,
                "lng": inc.lng,
            }
        )
    return jsonify(result), 200
