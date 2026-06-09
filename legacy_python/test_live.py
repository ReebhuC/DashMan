from dashman_ai import DashManAI
import time
import sys

try:
    print("\n--- INITIALIZING AI STREAMING ENGINE ---")
    # Initialize the AI System
    bot = DashManAI()
    
    # Start the Flask Streamer on Port 5001
    bot.live_2x() 
    
    print("✅ SERVER ONLINE")
    print("------------------------------------------------")
    print("   📷 Standard View:  http://127.0.0.1:5001/stream/legacy")
    print("   ✨ AI Enhanced:    http://127.0.0.1:5001/stream/ai")
    print("------------------------------------------------")
    print("   (Keep this terminal open to maintain the stream)")
    print("   Press Ctrl+C to stop.\n")

    # Keep the script running so the background thread stays alive
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\n🛑 Stopping Stream...")
    sys.exit()
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("Make sure you are running this from the DashMan folder!")
