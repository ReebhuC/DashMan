import requests
import cv2
from cv2 import dnn_superres
import os
import time

SERVER_URL = "http://127.0.0.1:5000"
# --- FIX: Use Fast Model ---
MODEL_PATH = "app/models/FSRCNN_x4.pb"
DOWNLOAD_DIR = "phone_gallery/downloads"
ENHANCED_DIR = "phone_gallery/enhanced"

def init_models():
    if not os.path.exists(MODEL_PATH):
        print(f"⚠️ Model missing at {MODEL_PATH}")
        return None
    sr = dnn_superres.DnnSuperResImpl_create()
    sr.readModel(MODEL_PATH)
    # --- FIX: Set model to FSRCNN ---
    sr.setModel("fsrcnn", 4)
    return sr

def simulate_incident_response():
    if not os.path.exists(DOWNLOAD_DIR): os.makedirs(DOWNLOAD_DIR)
    if not os.path.exists(ENHANCED_DIR): os.makedirs(ENHANCED_DIR)

    print("\n--- 1. INCIDENT DETECTED ---")
    try:
        response = requests.get(f"{SERVER_URL}/trigger_incident")
        data = response.json()
        video_url = data['download_url']
        filename = data['filename']
        print(f"   ✅ Dashcam says: {data['type']}")
    except Exception as e:
        print(f"   ❌ Connection Failed: {e}"); return

    print("\n--- 2. TRANSFERRING FILE ---")
    local_raw_path = os.path.join(DOWNLOAD_DIR, filename)
    with requests.get(video_url, stream=True) as r:
        with open(local_raw_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): f.write(chunk)
    print(f"   ✅ Download Complete.")

    print("\n--- 3. ENHANCING ON PHONE (AI) ---")
    ai_processor = init_models()
    if ai_processor is None: return

    # --- KEEP MP4 EXTENSION ---
    output_path = os.path.join(ENHANCED_DIR, f"ENHANCED_{filename}")
    
    cap = cv2.VideoCapture(local_raw_path)
    if not cap.isOpened(): return

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    ret, frame = cap.read()
    h, w = frame.shape[:2]
    
    cap.release()
    cap = cv2.VideoCapture(local_raw_path)
    
    # --- USE 'mp4v' (SAFE FOR MAC) ---
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    
    print(f"   📉 Input: {w}x{h}")
    print(f"   📈 Target: {w*4}x{h*4} (Using Fast FSRCNN)")
    
    out = cv2.VideoWriter(output_path, fourcc, fps, (w*4, h*4))
    
    count = 0
    start_time = time.time()
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        enhanced = ai_processor.upsample(frame)
        out.write(enhanced)
        
        count += 1
        print(f"   ... Processed Frame {count}", end='\r')
        
    cap.release()
    out.release()
    
    elapsed = time.time() - start_time
    print(f"\n   ✅ DONE in {elapsed:.1f}s!")
    print(f"   📂 Evidence saved: {output_path}")

if __name__ == "__main__":
    simulate_incident_response()