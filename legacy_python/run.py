from app import create_app
from dashman_ai import DashManAI

# 1. Create the Flask App using your existing factory
app = create_app()

# 2. Initialize the AI Engine
print("--- 🚀 Initializing DashMan AI ---")
ai = DashManAI()

# 3. Start the Live Stream (Runs in background on Port 5001)
ai.live_2x()

# 4. Attach AI to the App Config so your routes can access it
#    (This allows you to call ai.fake_camera_enhance() from your web routes)
app.config['AI_ENGINE'] = ai

if __name__ == "__main__":
    # IMPORTANT: use_reloader=False prevents the code from running twice 
    # and crashing the AI stream port (5001).
    app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)