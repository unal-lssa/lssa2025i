from flask import Flask, jsonify
import time

app = Flask(__name__)


@app.route("/process", methods=["GET"])
def process():
    # Simulate 50 ms latency
    time.sleep(0.05)
    return jsonify({"message": "Business logic executed"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
