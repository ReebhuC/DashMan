from flask import Blueprint, request, jsonify, render_template, current_app
from . import db
from .models import Incident

api_bp = Blueprint("api", __name__)

# --- EXISTING ROUTES ---
@api_bp.route("/events", methods=["POST"])
def create_event():
    data = request.get_json() or {}
    incident = Incident(trip_id=data.get("trip_id"), timestamp=data.get("timestamp"))
    db.session.add(incident)
    db.session.commit()
    return jsonify({"id": incident.id}), 201

@api_bp.route("/incidents", methods=["GET"])
def list_incidents():
    incidents = Incident.query.order_by(Incident.timestamp.desc()).all()
    result = [{"id": i.id, "time": i.timestamp} for i in incidents]
    return jsonify(result), 200

# --- FRONTEND ROUTES ---
@api_bp.route("/")
def home():
    return render_template("index.html")

@api_bp.route("/incidents-page")
def incidents_page():
    incidents_data = Incident.query.order_by(Incident.timestamp.desc()).all()
    formatted = [{"time": i.timestamp, "type": "incident", "location": "Recorded"} for i in incidents_data]
    return render_template("incidents.html", incidents=formatted)

# --- THE MISSING LINK: AI TRIGGER ---
@api_bp.route('/trigger_incident', methods=['GET', 'POST'])
def trigger_incident():
    # Access the AI engine we attached in run.py
    ai = current_app.config.get('AI_ENGINE')
    if ai:
        # Call the new "Lightweight" server function
        result = ai.fake_camera_enhance()
        return jsonify(result)
    
    return jsonify({"error": "AI Engine not loaded"}), 500
