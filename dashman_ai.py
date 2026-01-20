import cv2
import sqlite3
import threading
import time
import os
import random
import numpy as np
from flask import Flask, Response
from datetime import datetime
import shutil

# --- CONFIGURATION ---
CONFIG = {
    'live_scale': 2,    
    'db_path': 'app.db',
    'video_dir': 'app/static',
    'model_dir': 'app/models',
    'stream_port': 5001,
    'stream_host': '0.0.0.0',
    'cam_width': 640,
    'cam_height': 480,
    'jpeg_quality': 70
}

class DashManAI:
    def __init__(self):
        print("--- 🚀 Initializing DashMan AI ---")

        self.stream_app = Flask(__name__)
        self.streaming = False
        self.camera_source = 0

        # Enable OpenCL if available
        cv2.ocl.setUseOpenCL(True)

        # ---- Super Resolution Safe Init ----
        self.sr_live = None
        try:
            if hasattr(cv2, "dnn_superres"):
                if hasattr(cv2.dnn_superres, "DnnSuperResImpl_create"):
                    self.sr_live = cv2.dnn_superres.DnnSuperResImpl_create()
                elif hasattr(cv2.dnn_superres, "createSuperResolution"):
                    self.sr_live = cv2.dnn_superres.createSuperResolution()
        except Exception as e:
            print(f"⚠️ Super-resolution unavailable: {e}")

        if self.sr_live is None:
            print("⚠️ Running WITHOUT AI super-resolution (fallback mode)")

        # Continue normal init
        self._load_models()
        self.stream_app.add_url_rule('/', 'index', self._index)
        self.stream_app.add_url_rule('/stream/legacy', 'stream_legacy', self._stream_legacy)
        self.stream_app.add_url_rule('/stream/ai', 'stream_ai', self._stream_ai)
        self._init_system()


    def _load_models(self):
        # --- CHANGED: Use ESPCN x2 for Fastest Live Streaming ---
        live_path = os.path.join(CONFIG['model_dir'], 'ESPCN_x2.pb')
        
        if os.path.exists(live_path):
            try:
                print(f"⚡ Loading Live Model: {live_path}")
                if self.sr_live is None:
                    return

                self.sr_live.readModel(live_path)
                self.sr_live.setModel("espcn", 2)

            except Exception as e:
                print(f"❌ Model Load Error: {e}")
        else:
            print(f"⚠️ Warning: Model not found at {live_path}")

    def _init_system(self):
        if not os.path.exists(CONFIG['video_dir']): os.makedirs(CONFIG['video_dir'])
        conn = sqlite3.connect(CONFIG['db_path'], check_same_thread=False)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS incident (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT, 
                trip_id INTEGER,
                directory TEXT,
                video_path TEXT,
                max_speed FLOAT,
                start_lat FLOAT,
                start_lng FLOAT,
                acceleration FLOAT,
                sensor_count INTEGER,
                gps_count INTEGER,
                processed BOOLEAN,
                incident_type TEXT,
                status TEXT,
                raw_video_path TEXT
        )''')
        conn.commit()
        conn.close()

    def _index(self):
        return "<h1>DashMan Server Active 🟢</h1>"

    def fake_camera_enhance(self):
        event_type = random.choice(['COLLISION', 'LANE_DEPARTURE'])
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        real_test_file = os.path.join(CONFIG['video_dir'], "test_clip.mp4")
        filename = f"incident_real_{int(time.time())}.mp4"
        target_path = os.path.join(CONFIG['video_dir'], filename)
        
        if os.path.exists(real_test_file):
            shutil.copy(real_test_file, target_path)
            print(f"🎬 USING REAL VIDEO: {filename}")
        else:
            out = cv2.VideoWriter(target_path, cv2.VideoWriter_fourcc(*'mp4v'), 10, (640, 480))
            for _ in range(30): out.write(np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8))
            out.release()

        rel_path = f"static/{filename}"
        
        conn = sqlite3.connect(CONFIG['db_path'])
        c = conn.cursor()
        c.execute("""
            INSERT INTO incident 
            (timestamp, incident_type, raw_video_path, status, trip_id, speed, acceleration, lat, lng) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp, 
            event_type, 
            rel_path, 
            'PENDING_DOWNLOAD',
            101,            # Dummy Trip ID
            random.uniform(40, 70),  # Random Speed
            random.uniform(-1, -3),  # Random G-Force
            37.7749,        # SF Lat
            -122.4194       # SF Lng
        ))
        conn.commit()
        conn.close()
        
        return {
            "status": "ready_for_download", 
            "type": event_type, 
            "download_url": f"http://127.0.0.1:5000/{rel_path}",
            "filename": filename
        }

    # Stream functions
    def live_2x(self):
        if self.streaming: return
        self.streaming = True
        t = threading.Thread(target=self._run_flask)
        t.daemon = True
        t.start()
    def _run_flask(self):
        self.stream_app.run(host=CONFIG['stream_host'], port=CONFIG['stream_port'], debug=False, use_reloader=False)
    def _get_camera(self):
        cap = cv2.VideoCapture(self.camera_source)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, CONFIG['cam_width'])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CONFIG['cam_height'])
        return cap
    def _gen_legacy(self):
        cap = self._get_camera()
        while self.streaming:
            success, frame = cap.read()
            if not success: time.sleep(0.1); continue
            enhanced = cv2.resize(frame, (frame.shape[1]*2, frame.shape[0]*2))
            ret, buffer = cv2.imencode('.jpg', enhanced, [int(cv2.IMWRITE_JPEG_QUALITY), CONFIG['jpeg_quality']])
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    def _gen_ai(self):
        cap = self._get_camera()
        while self.streaming:
            success, frame = cap.read()
            if not success: time.sleep(0.1); continue
            try: enhanced = self.sr_live.upsample(frame)
            except: enhanced = frame
            ret, buffer = cv2.imencode('.jpg', enhanced, [int(cv2.IMWRITE_JPEG_QUALITY), CONFIG['jpeg_quality']])
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    def _stream_legacy(self): return Response(self._gen_legacy(), mimetype='multipart/x-mixed-replace; boundary=frame')
    def _stream_ai(self): return Response(self._gen_ai(), mimetype='multipart/x-mixed-replace; boundary=frame')