from flask import Flask, jsonify
import time

app = Flask(__name__)


@app.route("/db", methods=["GET"])
def db_data():
    # Simulate 50 ms latency
    time.sleep(0.05)
    return jsonify({"message": "Fetched fresh data from DB"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
