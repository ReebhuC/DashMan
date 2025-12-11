Dashcam Backend (Person A Tasks)
Simple Flask backend + fake dashcam data generator for Person B to build UI on top of.

What this does
Database: SQLite with Vehicle, Trip, Incident tables (managed via migrations).

API:

POST /events - create incident from JSON

GET /incidents - list all incidents as JSON

Fake Camera: csv_tools/csv_ingestor.py reads telemetry CSV and sends incidents to /events

Quick Start
bash
# Clone and setup
git clone https://github.com/ReebhuC/DashMan.git
cd DashMan
python3 -m venv .venv
source .venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
bash
# Start backend server
export FLASK_APP="app:create_app"
flask run
# Server runs at http://127.0.0.1:5000
bash
# Test API (in new terminal)
curl http://127.0.0.1:5000/ping                    # {"status": "ok"}
curl http://127.0.0.1:5000/incidents               # [] (empty list)

curl -X POST http://127.0.0.1:5000/events \
  -H "Content-Type: application/json" \
  -d '{"trip_id":1,"timestamp":"2025-01-01T10:00:00","speed":40.5,"acceleration":3.2,"lat":12.9716,"lng":77.5946}'

curl http://127.0.0.1:5000/incidents               # shows your incident
bash
# Generate fake incidents from CSV (server must be running)
python csv_tools/csv_ingestor.py
curl http://127.0.0.1:5000/incidents               # see new incidents
API Details
POST /events
Input JSON (all fields optional except trip_id):

json
{
  "trip_id": 1,
  "timestamp": "2025-01-01T10:00:00",
  "speed": 40.5,
  "acceleration": 3.2,
  "lat": 12.9716,
  "lng": 77.5946
}
Response: 201 {"id": 1}

GET /incidents
Response: 200 JSON array of incidents:

json
[
  {
    "id": 1,
    "trip_id": 1,
    "timestamp": "2025-01-01T10:00:00",
    "speed": 40.5,
    "acceleration": 3.2,
    "lat": 12.9716,
    "lng": 77.5946
  }
]
CSV Format (sample_events.csv)
text
trip_id,timestamp,speed,acceleration,lat,lng
1,2025-01-01T10:00:00,40.5,3.2,12.9716,77.5946
1,2025-01-01T10:00:01,41.0,1.0,12.9717,77.5947
1,2025-01-01T10:00:02,39.0,-5.5,12.9718,77.5948
How it works: csv_ingestor.py reads each row. If |acceleration| >= 3.0, sends as incident to /events.

Database Models
Vehicle: id, name

Trip: id, vehicle_id, start_time, end_time
Incident: id, trip_id, timestamp, speed, acceleration, lat, lng​



Folder Structure
text
DashMan/
├── app/                 # Flask app + models + routes
│   ├── __init__.py      # app factory
│   ├── models.py        # Vehicle/Trip/Incident
│   └── routes.py        # /events and /incidents
├── csv_tools/           # fake camera simulator
│   └── csv_ingestor.py
├── migrations/          # DB schema changes
├── sample_events.csv    # example telemetry data
├── config.py            # SQLite config
├── app.db               # SQLite database (auto-created)
└── requirements.txt     # pip install -r requirements.txt



Person B: Use this for UI
Call GET /incidents to show incidents in your frontend.

Run python csv_tools/csv_ingestor.py to generate test data.

Person A will expand models/API as needed.
