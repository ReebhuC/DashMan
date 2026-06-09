import cv2
import sys
import os

input_file = "test_clip.mp4"
output_file = "low_res_640x480.mp4"
target_size = (640, 480)

if not os.path.exists(input_file):
    print(f"❌ Error: Cannot find '{input_file}' in {os.getcwd()}")
    sys.exit()

cap = cv2.VideoCapture(input_file)
fps = cap.get(cv2.CAP_PROP_FPS) or 30
out = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*'mp4v'), fps, target_size)

print(f"⚡ DOWNSCALING: {input_file} -> {target_size}")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break
    out.write(cv2.resize(frame, target_size, interpolation=cv2.INTER_AREA))

cap.release()
out.release()
print(f"✅ DONE! Created: {output_file}")
