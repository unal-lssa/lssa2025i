from flask import Flask, request, jsonify
import time
import threading

app = Flask(__name__)
cache = {}
DEFAULT_TTL = 30 # Tiempo de vida en segundos

@app.route("/cache/<key>", methods=["GET"])
def get_cache(key):
    if key in cache:
        # Verificar si ha expirado
        if time.time() < cache[key]["expires_at"]:
            print(f"Cache HIT: {key}")
            return jsonify({'value': cache[key]["value"], 'cached': True})
        else:
            # Expiró, eliminar entrada
            print(f"Cache EXPIRED: {key}")
            del cache[key]
    
    print(f"Cache MISS: {key}")
    return jsonify({'value': None, 'cached': False})

@app.route("/cache/<key>", methods=["POST"])
def set_cache(key):
    data = request.json
    ttl = data.get("ttl", DEFAULT_TTL)
    
    cache[key] = {
        "value": data.get("value"),
        "expires_at": time.time() + ttl
    }
    
    print(f"Cache SET: {key} (expira en {ttl}s)")
    return jsonify({'status': 'ok', 'ttl': ttl})

@app.route("/cache/status", methods=["GET"])
def cache_status():
    now = time.time()
    status = {}
    for key, value in cache.items():
        remaining = value["expires_at"] - now
        status[key] = {
            "valid": remaining > 0,
            "remaining_seconds": max(0, remaining)
        }
    return jsonify(status)

if __name__ == "__main__":
    app.run(port=5004, debug=True)