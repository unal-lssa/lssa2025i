from flask import Flask, request, jsonify
import time

app = Flask(__name__)
cache = {}

@app.route("/cache/<key>", methods=["GET"])
def get_cache(key):
    entry = cache.get(key)
    if not entry:
        return jsonify({'value': None})
    if time.time() > entry['expires_at']:
        del cache[key]  # Eliminar el registro si expiró
        return jsonify({'value': None})
    return jsonify({'value': cache.get(key)})

@app.route("/cache/<key>", methods=["POST"])
def set_cache(key):
    data = request.json
    value = data.get("value")
    ttl = data.get("ttl", 120)  # TTL por defecto: 60 segundos
    expires_at = time.time() + ttl
    cache[key] = {'value': value, 'expires_at': expires_at}
    return jsonify({'status': 'ok', 'expires_in': ttl})

if __name__ == "__main__":
    app.run(port=5004, debug=True)