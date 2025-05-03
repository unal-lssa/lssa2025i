from flask import Flask, request, jsonify
import time
import threading

app = Flask(__name__)

# Cache data structure with TTL support
class CacheWithTTL:
    def __init__(self):
        self.cache = {}
        self.stats = {
            "hits": 0,
            "misses": 0,
            "expired": 0,
            "size": 0,
            "evictions": 0
        }
        self.max_size = 100  # Maximum number of items
        self.cleanup_thread = threading.Thread(target=self._cleanup_expired_keys, daemon=True)
        self.cleanup_thread.start()
    
    def get(self, key):
        """Get a value from cache, respecting TTL"""
        if key not in self.cache:
            self.stats["misses"] += 1
            return None
        
        item = self.cache[key]
        current_time = time.time()
        
        # Check if the item has expired
        if item["expiry"] and item["expiry"] < current_time:
            del self.cache[key]
            self.stats["expired"] += 1
            self.stats["size"] -= 1
            return None
        
        # Update last accessed time for LRU implementation
        item["last_accessed"] = current_time
        self.stats["hits"] += 1
        return item["value"]
    
    def set(self, key, value, ttl=None):
        """Set a value in cache with optional TTL in seconds"""
        current_time = time.time()
        expiry = None if ttl is None else current_time + ttl
        
        # Check if we need to evict something
        if key not in self.cache and len(self.cache) >= self.max_size:
            self._evict_lru()
        
        # Update or insert the item
        self.cache[key] = {
            "value": value,
            "created": current_time,
            "last_accessed": current_time,
            "expiry": expiry
        }
        
        if key not in self.cache:
            self.stats["size"] += 1
    
    def _evict_lru(self):
        """Evict the least recently used item"""
        if not self.cache:
            return
        
        lru_key = min(self.cache.keys(), key=lambda k: self.cache[k]["last_accessed"])
        del self.cache[lru_key]
        self.stats["evictions"] += 1
        self.stats["size"] -= 1
    
    def _cleanup_expired_keys(self):
        """Background thread to clean up expired keys"""
        while True:
            time.sleep(10)  # Check every 10 seconds
            current_time = time.time()
            expired_keys = [
                k for k, v in self.cache.items() 
                if v["expiry"] and v["expiry"] < current_time
            ]
            
            for key in expired_keys:
                del self.cache[key]
                self.stats["expired"] += 1
                self.stats["size"] -= 1
    
    def get_stats(self):
        """Return cache statistics"""
        return self.stats

# Initialize cache
cache_service = CacheWithTTL()

@app.route("/cache/<key>", methods=["GET"])
def get_cache(key):
    value = cache_service.get(key)
    if value is None:
        return jsonify({'value': None, 'hit': False})
    return jsonify({'value': value, 'hit': True})

@app.route("/cache/<key>", methods=["POST"])
def set_cache(key):
    data = request.json
    ttl = data.get("ttl")  # Optional TTL in seconds
    cache_service.set(key, data.get("value"), ttl)
    return jsonify({'status': 'ok'})

@app.route("/cache/stats", methods=["GET"])
def get_stats():
    stats = cache_service.get_stats()
    hit_rate = 0
    if stats["hits"] + stats["misses"] > 0:
        hit_rate = stats["hits"] / (stats["hits"] + stats["misses"]) * 100
    
    return jsonify({
        "stats": stats,
        "hit_rate": f"{hit_rate:.2f}%",
        "items": len(cache_service.cache)
    })

@app.route("/cache/flush", methods=["POST"])
def flush_cache():
    cache_service.cache.clear()
    cache_service.stats["size"] = 0
    return jsonify({'status': 'Cache flushed'})

if __name__ == "__main__":
    app.run(port=5004, debug=True)
