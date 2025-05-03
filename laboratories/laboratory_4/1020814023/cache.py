from flask import Flask, request, jsonify
import time
from datetime import datetime

app = Flask(__name__)
cache = {}

@app.route("/cache/<key>", methods=["GET"])
def get_cache(key):
    entry = cache.get(key)
    if not entry:
        return jsonify({'value': None})
    if time.time() > entry['expires_at']:
        del cache[key]
        return jsonify({'value': None})
    readable_expires = datetime.fromtimestamp(entry['expires_at']).strftime('%Y-%m-%d %H:%M:%S')
    return jsonify({
        'value': {
            'value': entry['value'],
            'expires_at': readable_expires
        }
    })

@app.route("/cache/<key>", methods=["POST"])
def set_cache(key):
    data = request.json
    value = data.get("value")
    ttl = data.get("ttl", 120)
    expires_at = time.time() + ttl
    cache[key] = {'value': value, 'expires_at': expires_at}
    return jsonify({'status': 'ok', 'expires_in': ttl})

if __name__ == "__main__":
    app.run(port=5004, debug=True)
