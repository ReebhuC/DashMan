import cv2
import sys

# 1. SETUP
input_file = "test_clip.mp4"   # CHANGE THIS to your actual filename
output_file = "low_res_640x480.mp4"
target_size = (640, 480)

cap = cv2.VideoCapture(input_file)

if not cap.isOpened():
    print(f"❌ Error: Could not open {input_file}")
    sys.exit()

# Get original FPS to keep speed correct
fps = cap.get(cv2.CAP_PROP_FPS) or 30
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_file, fourcc, fps, target_size)

print(f"⚡ DOWNSCALING: {input_file} -> {target_size}")

count = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break
    
    # THE CRUSHER
    resized = cv2.resize(frame, target_size, interpolation=cv2.INTER_AREA)
    out.write(resized)
    
    count += 1
    if count % 30 == 0: print(f"   Processed {count} frames...", end='\r')

cap.release()
out.release()
print(f"\n✅ DONE! Saved to: {output_file}")