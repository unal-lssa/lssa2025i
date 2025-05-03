from flask import Flask, request, jsonify
import time
import threading
import requests

app = Flask(__name__)

# Estructura de caché con TTL (Time-To-Live) y estadísticas
# cache = {key: {"value": value, "created_at": timestamp, "expires_at": timestamp, "hits": count}}
cache = {}

# Configuración
DEFAULT_TTL = 60  # segundos
MAX_CACHE_SIZE = 100  # elementos
CLEANUP_INTERVAL = 30  # segundos
cache_lock = threading.Lock()
cache_stats = {
    "hits": 0,
    "misses": 0,
    "evictions": 0
}

# Función para limpiar el caché periódicamente
def cache_cleanup():
    while True:
        now = time.time()
        keys_to_remove = []
        
        with cache_lock:
            # Identificar elementos expirados
            for key, data in cache.items():
                if data["expires_at"] < now:
                    keys_to_remove.append(key)
            
            # Eliminar elementos expirados
            for key in keys_to_remove:
                del cache[key]
                cache_stats["evictions"] += 1
            
            # Si aún estamos por encima del tamaño máximo, eliminar los menos usados
            if len(cache) > MAX_CACHE_SIZE:
                # Ordenar por número de hits (menos usados primero)
                sorted_keys = sorted(cache.keys(), key=lambda k: cache[k]["hits"])
                # Eliminar hasta que estemos en el tamaño máximo
                for key in sorted_keys[:len(cache) - MAX_CACHE_SIZE]:
                    del cache[key]
                    cache_stats["evictions"] += 1
        
        # Enviar estadísticas al monitor
        try:
            requests.post("http://127.0.0.1:5006/metrics/update", 
                         json={"cache_hit": False, 
                               "evictions": len(keys_to_remove)},
                         timeout=0.5)
        except:
            pass  # No bloquear si el servicio de métricas no está disponible
        
        # Esperar hasta el próximo ciclo de limpieza
        time.sleep(CLEANUP_INTERVAL)

# Iniciar el thread de limpieza
cleanup_thread = threading.Thread(target=cache_cleanup, daemon=True)
cleanup_thread.start()

@app.route("/cache/<key>", methods=["GET"])
def get_cache(key):
    now = time.time()
    hit = False
    
    with cache_lock:
        if key in cache and cache[key]["expires_at"] > now:
            # Incrementar contador de hits
            cache[key]["hits"] += 1
            cache_stats["hits"] += 1
            value = cache[key]["value"]
            hit = True
        else:
            if key in cache:
                # Expirado
                del cache[key]
            value = None
            cache_stats["misses"] += 1
    
    # Enviar estadísticas al monitor
    try:
        requests.post("http://127.0.0.1:5006/metrics/update", 
                     json={"cache_hit": hit},
                     timeout=0.5)
    except:
        pass  # No bloquear si el servicio de métricas no está disponible
    
    return jsonify({'value': value})

@app.route("/cache/<key>", methods=["POST"])
def set_cache(key):
    data = request.json
    ttl = data.get("ttl", DEFAULT_TTL)  # TTL personalizado o predeterminado
    now = time.time()
    
    with cache_lock:
        cache[key] = {
            "value": data.get("value"),
            "created_at": now,
            "expires_at": now + ttl,
            "hits": 0
        }
    
    return jsonify({'status': 'ok'})

@app.route("/cache/<key>", methods=["DELETE"])
def delete_cache(key):
    with cache_lock:
        if key in cache:
            del cache[key]
            status = "deleted"
        else:
            status = "not_found"
    
    return jsonify({'status': status})

@app.route("/cache/stats", methods=["GET"])
def get_stats():
    with cache_lock:
        stats = {
            "size": len(cache),
            "max_size": MAX_CACHE_SIZE,
            "hit_ratio": cache_stats["hits"] / (cache_stats["hits"] + cache_stats["misses"]) if (cache_stats["hits"] + cache_stats["misses"]) > 0 else 0,
            "evictions": cache_stats["evictions"],
            "hits": cache_stats["hits"],
            "misses": cache_stats["misses"]
        }
    
    return jsonify(stats)

@app.route("/cache", methods=["GET"])
def list_cache():
    with cache_lock:
        keys = list(cache.keys())
    
    return jsonify({'keys': keys})

@app.route("/cache/flush", methods=["POST"])
def flush_cache():
    with cache_lock:
        cache.clear()
        cache_stats["evictions"] += len(cache)
        cache_stats["hits"] = 0
        cache_stats["misses"] = 0
    
    return jsonify({'status': 'flushed'})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(port=5004, debug=True)