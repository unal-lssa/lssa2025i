from flask import Flask, jsonify
import time
import os

app = Flask(__name__)

# Environment variables
PORT = int(os.environ.get("FLASK_PORT", 5002))
RESPONSE_DELAY = float(os.environ.get("RESPONSE_DELAY", 0.5))  # Simulated DB delay in seconds

# Mock database
db_data = {
    "1": "First item from DB",
    "2": "Second item from DB",
    "3": "Third item from DB",
    "default": "Default data from DB"
}

@app.route("/db", methods=["GET"])
def db_data_default():
    # Simulate database query delay
    time.sleep(RESPONSE_DELAY)
    return jsonify({'message': db_data["default"]})

@app.route("/db/<id>", methods=["GET"])
def db_data_by_id(id):
    # Simulate database query delay
    time.sleep(RESPONSE_DELAY)
    data = db_data.get(id, db_data["default"])
    return jsonify({'message': data})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({'status': 'up'})

if __name__ == "__main__":
    print(f"Database service starting on port {PORT}, delay={RESPONSE_DELAY}s")
    app.run(host="0.0.0.0", port=PORT, debug=True)
