from flask import Flask, request, jsonify
import time
import threading

app = Flask(__name__)
cache = {}  # key: (value, expiry_ts)
TTL = 30  # segundos

@app.route("/cache/<key>", methods=["GET"])
def get_cache(key):
    entry = cache.get(key)
    if not entry or entry[1] < time.time():
        cache.pop(key, None)
        return jsonify({'value': None})
    return jsonify({'value': entry[0]})

@app.route("/cache/<key>", methods=["POST"])
def set_cache(key):
    data = request.json
    expiry = time.time() + TTL
    cache[key] = (data.get("value"), expiry)
    return jsonify({'status': 'ok', 'expires_at': expiry})

# Hilo para limpiar expirados
def cleanup_loop():
    while True:
        now = time.time()
        keys = [k for k,(v,exp) in cache.items() if exp < now]
        for k in keys:
            cache.pop(k, None)
        time.sleep(TTL)

threading.Thread(target=cleanup_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(port=5004, debug=True)