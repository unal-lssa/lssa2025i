from flask import Flask, request, jsonify

from utils.logger import setup_logger

# Configurar el logger
logger = setup_logger("Cache", "cache.log")

app = Flask(__name__)
cache = {}

@app.route("/cache/<key>", methods=["GET"])
def get_cache(key):
    logger.info(f"Solicitud recibida cache {key}  >>>>>>> GET")
    logger.info(f"0. Valores en la  cache {cache}  >>>>>>> CACHE") 
    return jsonify({'value': cache.get(key)})

@app.route("/cache/clean", methods=["POST"])
def clean_cache():
    logger.info(f"1. Valores en la  cache {cache}  >>>>>>> CACHE")     
    cache.clear()
    logger.info(f"2. Valores en la  cache despues {cache}  >>>>>>> CACHE")     
    return jsonify({'clean': 'ok', 'data': cache})

@app.route("/cache/<key>", methods=["POST"])
def set_cache(key):    
    logger.info(f"Solicitud recibida cache {key}  >>>>>>> POST") 
    logger.info(f"3. Valores en la  cache {cache}  >>>>>>> CACHE") 
    data = request.json
    cache[key] = data.get("value")
    return jsonify({'status': 'ok'})

@app.route("/cache/stats", methods=["GET"])
def cache_stats():
    hits = cache.get("hits", 0)
    misses = cache.get("misses", 0)
    return jsonify({'hits': hits, 'misses': misses, 'size': len(cache)})

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5004, debug=True)