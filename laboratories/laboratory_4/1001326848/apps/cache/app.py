from flask import Flask, request, jsonify
import threading
import time

app = Flask(__name__)
cache = {}
CACHE_TTL = 20  # seconds


@app.route("/cache/<key>", methods=["GET"])
def get_cache(key):
    entry = cache.get(key)

    if entry:
        if time.time() - entry["timestamp"] <= CACHE_TTL:
            return jsonify({"value": entry["value"]})
        else:  # Expired
            del cache[key]
            return jsonify({"value": None})

    return jsonify({"value": None})


@app.route("/cache/<key>", methods=["POST"])
def set_cache(key):
    data = request.json
    cache[key] = {"value": data.get("value"), "timestamp": time.time()}
    return jsonify({"status": "ok"})


@app.route("/cache/<key>", methods=["DELETE"])
def delete_cache_key(key):
    if key in cache:
        del cache[key]
        return jsonify({"status": f"Key '{key}' deleted"})
    return jsonify({"error": f"Key '{key}' not found"}), 404


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        threaded=True
    )
