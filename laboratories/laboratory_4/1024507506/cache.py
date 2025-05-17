from flask import Flask, request, jsonify

app = Flask(__name__)
cache = {}

cache_hits = 0
cache_misses = 0

@app.route("/cache/<key>", methods=["GET"])
def get_cache(key):
    global cache_hits, cache_misses
    value = cache.get(key)
    if value:
        cache_hits += 1
    else:
        cache_misses += 1
    return jsonify({'value': cache.get(key)})

@app.route("/cache/<key>", methods=["POST"])
def set_cache(key):
    data = request.json
    cache[key] = data.get("value")
    return jsonify({'status': 'ok'})


@app.route("/metrics", methods=["GET"])
def metrics():
    total = cache_hits + cache_misses
    hit_rate = (cache_hits / total * 100) if total > 0 else 0
    return jsonify({
        "cache_hits": cache_hits,
        "cache_misses": cache_misses,
        "cache_size": len(cache),
        "cache_hit_rate": f"{hit_rate:.2f}%"
    })

if __name__ == "__main__":
    app.run(port=5004, debug=True)