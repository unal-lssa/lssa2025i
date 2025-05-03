from flask import Flask, request, jsonify
import time
import threading

app = Flask(__name__)

class CacheLevel:
    def __init__(self, name, max_size, default_ttl=None):
        self.name = name
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache = {}
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "evictions": 0,
            "expirations": 0
        }
    
    def get(self, key):
        if key not in self.cache:
            self.stats["misses"] += 1
            return None
        
        entry = self.cache[key]
        current_time = time.time()
        
        # Check expiration
        if entry["expiry"] and entry["expiry"] < current_time:
            del self.cache[key]
            self.stats["expirations"] += 1
            return None
        
        # Update access metadata
        entry["last_accessed"] = current_time
        entry["access_count"] += 1
        
        self.stats["hits"] += 1
        return entry["value"]
    
    def set(self, key, value, ttl=None):
        self.stats["sets"] += 1
        
        # Apply default TTL if none specified
        if ttl is None:
            ttl = self.default_ttl
        
        current_time = time.time()
        expiry = None if ttl is None else current_time + ttl
        
        # Eviction if necessary
        if key not in self.cache and len(self.cache) >= self.max_size:
            self._evict()
        
        # Store the value
        self.cache[key] = {
            "value": value,
            "created": current_time,
            "last_accessed": current_time,
            "access_count": 0,
            "expiry": expiry
        }
    
    def _evict(self):
        """Evict based on LRU (Least Recently Used)"""
        if not self.cache:
            return
        
        lru_key = min(self.cache.keys(), 
                     key=lambda k: self.cache[k]["last_accessed"])
        del self.cache[lru_key]
        self.stats["evictions"] += 1

class MultiLevelCache:
    def __init__(self):
        # L1: Small, fast cache with short TTL
        self.l1 = CacheLevel("L1", max_size=10, default_ttl=60)  # 1 minute TTL
        
        # L2: Medium cache with longer TTL
        self.l2 = CacheLevel("L2", max_size=50, default_ttl=300)  # 5 minutes TTL
        
        # L3: Large, slower cache with long TTL
        self.l3 = CacheLevel("L3", max_size=200, default_ttl=3600)  # 1 hour TTL
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_expired, daemon=True)
        self.cleanup_thread.start()
    
    def get(self, key):
        # Try L1 first
        value = self.l1.get(key)
        if value is not None:
            return {"value": value, "level": "L1", "hit": True}
        
        # Try L2
        value = self.l2.get(key)
        if value is not None:
            # Promote to L1
            self.l1.set(key, value)
            return {"value": value, "level": "L2", "hit": True}
        
        # Try L3
        value = self.l3.get(key)
        if value is not None:
            # Promote to L2
            self.l2.set(key, value)
            return {"value": value, "level": "L3", "hit": True}
        
        # Not in any cache
        return {"value": None, "hit": False}
    
    def set(self, key, value, ttl=None, level="all"):
        if level == "all" or level == "L1":
            self.l1.set(key, value, ttl)
        
        if level == "all" or level == "L2":
            self.l2.set(key, value, ttl)
        
        if level == "all" or level == "L3":
            self.l3.set(key, value, ttl)
    
    def _cleanup_expired(self):
        """Periodically clean up expired entries"""
        while True:
            time.sleep(30)  # Run every 30 seconds
            current_time = time.time()
            
            for cache_level in [self.l1, self.l2, self.l3]:
                expired_keys = [
                    k for k, v in cache_level.cache.items()
                    if v["expiry"] and v["expiry"] < current_time
                ]
                
                for key in expired_keys:
                    del cache_level.cache[key]
                    cache_level.stats["expirations"] += 1
    
    def get_stats(self):
        return {
            "L1": self.l1.stats,
            "L2": self.l2.stats,
            "L3": self.l3.stats,
            "total_items": {
                "L1": len(self.l1.cache),
                "L2": len(self.l2.cache),
                "L3": len(self.l3.cache)
            }
        }

# Initialize the multi-level cache
cache = MultiLevelCache()

@app.route("/cache/<key>", methods=["GET"])
def get_cache(key):
    result = cache.get(key)
    return jsonify(result)

@app.route("/cache/<key>", methods=["POST"])
def set_cache(key):
    data = request.json
    ttl = data.get("ttl")
    level = data.get("level", "all")
    cache.set(key, data.get("value"), ttl, level)
    return jsonify({"status": "ok"})

@app.route("/cache/stats", methods=["GET"])
def get_stats():
    return jsonify(cache.get_stats())

if __name__ == "__main__":
    app.run(port=5004, debug=True)
