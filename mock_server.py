from flask import Flask, jsonify, send_file, Response
import os

app = Flask(__name__)
DUMMY_MP4 = "dummy_incident.mp4"

# Create a dummy payload if it doesn't exist
if not os.path.exists(DUMMY_MP4):
    with open(DUMMY_MP4, "wb") as f:
        f.write(b"dummy video data")

@app.route('/locked_incidents', methods=['GET'])
def get_locked_incidents():
    return jsonify(["incident_1.mp4"])

@app.route('/download/<path:filename>', methods=['GET'])
def download_incident(filename):
    return send_file(DUMMY_MP4, mimetype="video/mp4", as_attachment=True, download_name=filename)

@app.route('/incidents/<path:filename>', methods=['DELETE'])
def delete_incident(filename):
    return Response(status=200)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)