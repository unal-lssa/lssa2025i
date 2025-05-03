from flask import Flask, request, jsonify
import time
import os
import threading
from prometheus_client import Counter, Gauge, generate_latest

app = Flask(__name__)

# Environment variables
PORT = int(os.environ.get("FLASK_PORT", 5004))
CACHE_TTL = int(os.environ.get("CACHE_TTL", 60))  # Default TTL: 60 seconds

# Cache storage with timestamps
cache_data = {}
cache_lock = threading.RLock()

# Metrics
CACHE_SIZE = Gauge('cache_size', 'Number of items in cache')
CACHE_OPERATIONS = Counter('cache_operations_total', 'Cache operations', ['operation'])
CACHE_HITS = Counter('cache_hits_total', 'Cache hits')
CACHE_MISSES = Counter('cache_misses_total', 'Cache misses')

# Cleanup expired items periodically
def cleanup_expired():
    while True:
        time.sleep(5)  # Check every 5 seconds
        with cache_lock:
            now = time.time()
            expired_keys = [
                key for key, (_, timestamp) in cache_data.items() 
                if now - timestamp > CACHE_TTL
            ]
            for key in expired_keys:
                del cache_data[key]
                CACHE_OPERATIONS.labels(operation='expire').inc()
            CACHE_SIZE.set(len(cache_data))

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_expired, daemon=True)
cleanup_thread.start()

# Metrics endpoint
@app.route("/metrics")
def metrics():
    return generate_latest()

# Health check
@app.route("/health")
def health():
    return jsonify({'status': 'up', 'cache_size': len(cache_data)})

# Get item from cache
@app.route("/cache/<key>", methods=["GET"])
def get_cache(key):
    with cache_lock:
        if key in cache_data:
            value, _ = cache_data[key]
            CACHE_HITS.inc()
            CACHE_OPERATIONS.labels(operation='get').inc()
            return jsonify({'value': value})
        CACHE_MISSES.inc()
        CACHE_OPERATIONS.labels(operation='get').inc()
        return jsonify({'value': None})

# Set item in cache
@app.route("/cache/<key>", methods=["POST"])
def set_cache(key):
    with cache_lock:
        data = request.json
        if 'value' in data:
            cache_data[key] = (data['value'], time.time())
            CACHE_SIZE.set(len(cache_data))
            CACHE_OPERATIONS.labels(operation='set').inc()
            return jsonify({'status': 'ok'})
        return jsonify({'error': 'No value provided'}), 400

# Delete item from cache
@app.route("/cache/<key>", methods=["DELETE"])
def delete_cache(key):
    with cache_lock:
        if key in cache_data:
            del cache_data[key]
            CACHE_SIZE.set(len(cache_data))
            CACHE_OPERATIONS.labels(operation='delete').inc()
            return jsonify({'status': 'deleted'})
        return jsonify({'error': 'Key not found'}), 404

# Flush entire cache
@app.route("/cache/flush", methods=["POST"])
def flush_cache():
    with cache_lock:
        cache_data.clear()
        CACHE_SIZE.set(0)
        CACHE_OPERATIONS.labels(operation='flush').inc()
        return jsonify({'status': 'flushed'})

# Get cache stats
@app.route("/cache/stats", methods=["GET"])
def cache_stats():
    with cache_lock:
        ttl_remaining = {}
        now = time.time()
        for key, (_, timestamp) in cache_data.items():
            remaining = max(0, CACHE_TTL - (now - timestamp))
            ttl_remaining[key] = remaining
            
        return jsonify({
            'size': len(cache_data),
            'ttl': CACHE_TTL,
            'items': list(cache_data.keys()),
            'ttl_remaining': ttl_remaining
        })

if __name__ == "__main__":
    print(f"Cache service starting on port {PORT}, TTL={CACHE_TTL}s")
    app.run(host="0.0.0.0", port=PORT, debug=True)
