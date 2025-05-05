# microservice_heavy.py

from flask import Flask, jsonify
import time

app = Flask(__name__)

@app.route("/process-heavy", methods=["GET"])
def process_heavy():
    time.sleep(3)  # Simula una operación más costosa
    return jsonify({'message': 'Heavy process executed'}), 200

if __name__ == "__main__":
    app.run(port=5006, debug=True)
