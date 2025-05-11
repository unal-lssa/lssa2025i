from flask import Flask, jsonify, request
import os
import time

app = Flask(__name__)

# Environment variables
PORT = int(os.environ.get("FLASK_PORT", 5001))
SERVICE_ID = os.environ.get("SERVICE_ID", "1")

@app.route("/process", methods=["GET"])
def process():
    # Simulate some processing
    processing_time = 0.1  # seconds
    time.sleep(processing_time)
    
    return jsonify({
        'message': f'Business logic executed by microservice {SERVICE_ID}',
        'service_id': SERVICE_ID
    }), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        'status': 'up',
        'service_id': SERVICE_ID
    })

if __name__ == "__main__":
    print(f"Microservice {SERVICE_ID} starting on port {PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=True)
