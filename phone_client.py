import requests
import cv2
from cv2 import dnn_superres
import os
import time

SERVER_URL = "http://127.0.0.1:5000"
# --- CHANGED: Use the Fastest Model (ESPCN) ---
MODEL_PATH = "app/models/ESPCN_x4.pb"
DOWNLOAD_DIR = "phone_gallery/downloads"
ENHANCED_DIR = "phone_gallery/enhanced"

# --- SPEED HACK: Process every Nth frame (1 = all frames, 2 = half frames) ---
FRAME_SKIP = 2 

def init_models():
    if not os.path.exists(MODEL_PATH):
        print(f"⚠️ Model missing at {MODEL_PATH}")
        return None
    
    # --- SPEED HACK: Turn on Hardware Acceleration for CV2 ---
    cv2.ocl.setUseOpenCL(True)
    
    sr = dnn_superres.DnnSuperResImpl_create()
    sr.readModel(MODEL_PATH)
    # --- CHANGED: Model name is 'espcn' ---
    sr.setModel("espcn", 4)
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

    output_path = os.path.join(ENHANCED_DIR, f"ENHANCED_{filename}")
    
    cap = cv2.VideoCapture(local_raw_path)
    if not cap.isOpened(): return

    # Reduce output FPS if we are skipping frames
    original_fps = cap.get(cv2.CAP_PROP_FPS) or 30
    target_fps = original_fps / FRAME_SKIP
    
    ret, frame = cap.read()
    h, w = frame.shape[:2]
    
    cap.release()
    cap = cv2.VideoCapture(local_raw_path)
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    
    print(f"   📉 Input: {w}x{h}")
    print(f"   📈 Target: {w*4}x{h*4} (Model: ESPCN | Speed: {FRAME_SKIP}x)")
    
    out = cv2.VideoWriter(output_path, fourcc, target_fps, (w*4, h*4))
    
    count = 0
    start_time = time.time()
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        # --- SPEED HACK: Skip frames ---
        if count % FRAME_SKIP == 0:
            enhanced = ai_processor.upsample(frame)
            out.write(enhanced)
            print(f"   ... Processed Frame {count} (Skipped {FRAME_SKIP-1})", end='\r')
        
        count += 1
        
    cap.release()
    out.release()
    
    elapsed = time.time() - start_time
    print(f"\n   ✅ DONE in {elapsed:.1f}s!")
    print(f"   📂 Evidence saved: {output_path}")

if __name__ == "__main__":
    simulate_incident_response()