from app import create_app
from dashman_ai import DashManAI

app = create_app()

print("--- 🚀 Initializing DashMan AI ---")
ai = DashManAI()

ai.live_2x()

app.config['AI_ENGINE'] = ai

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)