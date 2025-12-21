#!/usr/bin/env python3
import argparse
import yaml
import cv2
import sys
import os
from pathlib import Path

def load_config():
    config_path = 'config/config.yaml'
    if not os.path.exists(config_path):
        print("⚠️  Creating config/config.yaml")
        os.makedirs('config', exist_ok=True)
        return {'video': {'input_res': [1280, 720], 'output_res': [3840, 2160]}}
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def test_video(config):
    sample_path = 'samples/dashcam_sample.mp4'
    if not os.path.exists(sample_path):
        print("❌ MISSING: wget -O samples/dashcam_sample.mp4 https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4")
        return False
    
    cap = cv2.VideoCapture(sample_path)
    ret, frame = cap.read()
    cap.release()
    if ret:
        print(f"✅ LOADED: {frame.shape} -> TARGET {config['video']['output_res']}")
        return True
    print("❌ VIDEO FAIL")
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DashMan: AI Dashcam Upscaler")
    parser.add_argument('--live-2x', action='store_true')
    parser.add_argument('--offline-4x', type=str)
    parser.add_argument('--test', action='store_true')
    parser.add_argument('--phase1', action='store_true')
    args = parser.parse_args()
    
    config = load_config()
    print("🚀 DASHMAN PHASE 1")
    
    if args.phase1 or args.test:
        success = test_video(config)
        sys.exit(0 if success else 1)
    elif args.offline_4x:
        print(f"⏳ OFFLINE 4x: {args.offline_4x}")
    elif args.live_2x:
        print("📹 LIVE 2x")
    else:
        parser.print_help()
