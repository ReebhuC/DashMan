import csv
import requests

API_URL = "http://127.0.0.1:5000/events"
ACCELERATION_THRESHOLD = 3.0  # simple rule: anything >= 3.0 (absolute) is an incident


def process_csv(csv_path: str):
    print("Starting process_csv with:", csv_path)  # debug

    # Open the CSV file
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)

        # Loop over each data row
        for row in reader:
            print("Read row:", row)  # debug: show every row that was read

            # Convert numeric fields from strings to numbers
            trip_id = int(row["trip_id"])
            speed = float(row["speed"])
            acceleration = float(row["acceleration"])
            lat = float(row["lat"])
            lng = float(row["lng"])
            timestamp = row["timestamp"]

            # Only send rows where |acceleration| is high enough
            if abs(acceleration) >= ACCELERATION_THRESHOLD:
                payload = {
                    "trip_id": trip_id,
                    "timestamp": timestamp,
                    "speed": speed,
                    "acceleration": acceleration,
                    "lat": lat,
                    "lng": lng,
                }

                print("Sending incident:", payload)  # debug

                try:
                    resp = requests.post(API_URL, json=payload, timeout=5)
                    print("Response:", resp.status_code, resp.text)  # debug
                except requests.RequestException as e:
                    print("Error sending incident:", e)


if __name__ == "__main__":
    # When you run this file directly, process sample_events.csv
    process_csv("sample_events.csv")
