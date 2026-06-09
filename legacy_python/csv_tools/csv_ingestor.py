import csv
import requests

API_URL = "http://127.0.0.1:5000/events"


def process_csv(csv_path: str):
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            payload = {
                "trip_id": int(row["trip_id"]),
                "timestamp": row["timestamp"],
                "anomaly_type": row["anomaly_type"],
                "speed": float(row["speed"]),
                "acceleration": float(row["acceleration"]),
                "lat": float(row["lat"]),
                "lng": float(row["lng"]),
            }

            try:
                resp = requests.post(API_URL, json=payload, timeout=5)
                print("Sent:", payload, "→", resp.status_code)
            except requests.RequestException as e:
                print("Error:", e)



if __name__ == "__main__":
    # When you run this file directly, process sample_events.csv
    process_csv("sample_events.csv")
