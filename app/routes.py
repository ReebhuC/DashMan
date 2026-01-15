from flask import Blueprint, request, jsonify, render_template, current_app
import os
from datetime import datetime
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

# --- NEW: UPLOAD ENDPOINT ---
@api_bp.route("/incident/upload", methods=["POST"])
def upload_incident():
    # 1. Create upload directory if not exists
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # 2. Get files
    video = request.files.get('video_file')
    sensor = request.files.get('sensor_log')
    gps = request.files.get('gps_log')

    if not video:
        return jsonify({"error": "No video file provided"}), 400

    # 3. Save files
    # Use a timestamp folder or just prefix
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    incident_dir = os.path.join(upload_folder, f"incident_{timestamp}")
    os.makedirs(incident_dir, exist_ok=True)

    video.save(os.path.join(incident_dir, video.filename or 'video.mp4'))
    
    if sensor:
        sensor.save(os.path.join(incident_dir, sensor.filename or 'sensor.json'))
    
    if gps:
        gps.save(os.path.join(incident_dir, gps.filename or 'gps.json'))

    # 4. (Optional) Create DB entry if you want
    # incident = Incident(timestamp=datetime.now())
    # db.session.add(incident)
    # db.session.commit()

    return jsonify({"status": "success", "path": incident_dir}), 201
