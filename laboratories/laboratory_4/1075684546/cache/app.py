import time
from flask import Flask, request, jsonify

app = Flask(__name__)
cache = {}

cache_expiry = {}

TTL = 30 # seconds

@app.route("/cache/<key>", methods=["GET"])
def get_cache(key):
    now = time.time()
    if key in cache and (now < cache_expiry.get(key, 0)):
        return jsonify({'value': cache[key]})
    cache.pop(key, None)
    cache_expiry.pop(key, None)
    return jsonify({'value': None})

@app.route("/cache/<key>", methods=["POST"])
def set_cache(key):
    data = request.json
    cache[key] = data.get("value")
    cache_expiry[key] = time.time() + TTL
    return jsonify({'status': 'ok', 'ttl': TTL})

@app.route("/cache/<key>", methods=["DELETE"])
def delete_cache(key):
    cache.pop(key, None)
    cache_expiry.pop(key, None)
    return jsonify({'status': 'deleted'})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5004, debug=True)