from flask import Blueprint, request, jsonify, render_template, current_app
import os
import json
from datetime import datetime
from . import mongo

api_bp = Blueprint("api", __name__)

# --- FRONTEND ROUTES ---
@api_bp.route("/")
def home():
    return render_template("index.html")

@api_bp.route("/incidents-page")
def incidents_page():
    # Query MongoDB: sort by timestamp desc
    incidents_data = list(mongo.db.incidents.find().sort("timestamp", -1))
    
    formatted = []
    for i in incidents_data:
        formatted.append({
            "time": i.get("timestamp"),
            "type": "incident",
            "location": f"{i.get('start_lat', 0)}, {i.get('start_lng', 0)}",
            "speed": f"{i.get('max_speed', 0)} km/h"
        })
        
    return render_template("incidents.html", incidents=formatted)

# --- API ROUTES ---

@api_bp.route("/incidents", methods=["GET"])
def list_incidents():
    incidents = list(mongo.db.incidents.find().sort("timestamp", -1))
    # Convert ObjectId to str for JSON
    for i in incidents:
        i["_id"] = str(i["_id"])
    return jsonify(incidents), 200

@api_bp.route("/incident/upload", methods=["POST"])
def upload_incident():
    # 1. Create upload directory
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # 2. Get files
    video = request.files.get('video_file')
    sensor = request.files.get('sensor_log')
    gps = request.files.get('gps_log')

    if not video:
        return jsonify({"error": "No video file provided"}), 400

    # 3. Save files to disk
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    incident_dir = os.path.join(upload_folder, f"incident_{timestamp_str}")
    os.makedirs(incident_dir, exist_ok=True)

    video_path = os.path.join(incident_dir, video.filename or 'video.mp4')
    video.save(video_path)
    
    sensor_data = []
    gps_data = []

    if sensor:
        sensor_path = os.path.join(incident_dir, sensor.filename or 'sensor.json')
        sensor.save(sensor_path)
        # Parse Sensor Data
        try:
            with open(sensor_path, 'r') as f:
                sensor_data = json.load(f)
        except:
            pass
    
    if gps:
        gps_path = os.path.join(incident_dir, gps.filename or 'gps.json')
        gps.save(gps_path)
        # Parse GPS Data
        try:
            with open(gps_path, 'r') as f:
                gps_data = json.load(f)
        except:
            pass

    # 4. Extract Metrics for DB
    max_speed = 0.0
    start_lat = 0.0
    start_lng = 0.0
    
    if gps_data:
        # Assuming GPSData has 'speed', 'latitude', 'longitude'
        # speed is usually m/s in Android, convert to km/h
        speeds = [p.get('speed', 0) * 3.6 for p in gps_data]
        if speeds:
            max_speed = max(speeds)
        
        first_point = gps_data[0]
        start_lat = first_point.get('latitude', 0.0)
        start_lng = first_point.get('longitude', 0.0)

    # 5. Insert into MongoDB
    incident_doc = {
        "timestamp": datetime.now(),
        "directory": incident_dir,
        "video_path": video_path,
        "max_speed": round(max_speed, 2),
        "start_lat": start_lat,
        "start_lng": start_lng,
        "sensor_count": len(sensor_data),
        "gps_count": len(gps_data),
        "processed": False
    }

    result = mongo.db.incidents.insert_one(incident_doc)

    return jsonify({
        "status": "success", 
        "id": str(result.inserted_id),
        "path": incident_dir
    }), 201

# --- AI TRIGGER ( unchanged ) ---
@api_bp.route('/trigger_incident', methods=['GET', 'POST'])
def trigger_incident():
    ai = current_app.config.get('AI_ENGINE')
    if ai:
        result = ai.fake_camera_enhance()
        return jsonify(result)
    
    return jsonify({"error": "AI Engine not loaded"}), 500
