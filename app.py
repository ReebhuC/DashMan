from flask import Flask, render_template  # import both

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

# ⬇️ paste your incidents route here
@app.route("/incidents")
def incidents():
    sample_incidents = [
        {
            "time": "2025-12-11 10:00",
            "type": "harsh_brake",
            "speed": 65,
            "location": "12.97, 77.59"
        },
        {
            "time": "2025-12-11 10:15",
            "type": "harsh_accel",
            "speed": 50,
            "location": "12.98, 77.60"
        },
    ]
    return render_template("incidents.html", incidents=sample_incidents)

# keep this at the bottom
if __name__ == "__main__":
    app.run(debug=True)
