from flask import Flask, request, jsonify
import jwt
import requests
import time
from functools import wraps
from threading import Thread
import random

app = Flask(__name__)
SECRET_KEY = "secret"

# Configuration
service_port = 5000  # This instance's port 
cache_service = "http://127.0.0.1:5004"
database_service = "http://127.0.0.1:5002"
microservice = "http://127.0.0.1:5001"
worker_service = "http://127.0.0.1:5005"

# Decorators
def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({'error': 'Missing token'}), 403
        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except:
            return jsonify({'error': 'Invalid token'}), 403
        return f(*args, **kwargs)
    return wrapper

def with_metrics(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        elapsed = time.time() - start_time
        
        # Log metrics about this request
        endpoint = request.path
        print(f"[METRICS] Endpoint: {endpoint}, Time: {elapsed:.4f}s")
        
        # Add metrics to response headers if result is a tuple with response
        if isinstance(result, tuple) and len(result) >= 2:
            response, status_code = result[0], result[1]
            headers = {"X-Processing-Time": str(elapsed)}
            return response, status_code, headers
        return result
    
    return wrapper

# Cache strategies
def cache_data(key, ttl=None, level=None):
    """Try to get data from cache"""
    params = {}
    if level:
        params["level"] = level
    
    cache_resp = requests.get(f"{cache_service}/cache/{key}", params=params).json()
    return cache_resp

def update_cache(key, value, ttl=None, level="all"):
    """Update the cache with new data"""
    payload = {"value": value}
    if ttl:
        payload["ttl"] = ttl
    if level:
        payload["level"] = level
    
    requests.post(f"{cache_service}/cache/{key}", json=payload)

# Routes
@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    # Add some randomized latency to simulate varying response times
    time.sleep(random.uniform(0.01, 0.05))
    return jsonify({"status": "ok", "instance": f"gateway-{service_port}"})

@app.route("/data", methods=["GET"])
@token_required
@with_metrics
def get_data():
    # Get cache control parameters from request
    bypass_cache = request.args.get("bypass_cache", "false").lower() == "true"
    cache_ttl = request.args.get("cache_ttl", type=int, default=300)  # Default 5 minutes
    cache_level = request.args.get("cache_level")
    
    # Check cache unless bypassed
    if not bypass_cache:
        cache_result = cache_data("my_data", level=cache_level)
        if cache_result.get("hit", False):
            level = cache_result.get("level", "unknown")
            return jsonify({
                'cached': True, 
                'cache_level': level, 
                'data': cache_result['value']
            })
    
    # Cache miss or bypass, fetch from DB with simulated latency
    print("Cache miss or bypass, fetching from DB")
    time.sleep(random.uniform(0.1, 0.3))  # Simulate DB access latency
    
    db_resp = requests.get(f"{database_service}/db").json()
    
    # Update cache with new value
    update_cache("my_data", db_resp['message'], ttl=cache_ttl, level=cache_level or "all")
    
    return jsonify({
        'cached': False,
        'data': db_resp['message'],
        'cache_ttl': cache_ttl
    })

@app.route("/data/complex", methods=["GET"])
@token_required
@with_metrics
def get_complex_data():
    """Endpoint that demonstrates cache invalidation patterns"""
    cache_key = f"complex_data_{request.args.get('id', 'default')}"
    
    # Check if we have it in cache
    cache_result = cache_data(cache_key)
    if cache_result.get("hit", False):
        return jsonify({
            'cached': True,
            'data': cache_result['value']
        })
    
    # Cache miss - fetch from multiple sources and combine
    # This demonstrates why caching is important for complex operations
    print("Complex data cache miss, fetching from multiple services")
    
    # Simulate multiple backend calls
    db_resp = requests.get(f"{database_service}/db").json()
    time.sleep(0.2)  # Simulate additional processing time
    
    service_resp = requests.get(f"{microservice}/process").json()
    
    # Combine results
    combined_data = {
        "db_data": db_resp['message'],
        "service_data": service_resp['message'],
        "timestamp": time.time()
    }
    
    # Cache the combined result - shorter TTL for complex data
    update_cache(cache_key, combined_data, ttl=60)
    
    return jsonify({
        'cached': False,
        'data': combined_data
    })

@app.route("/cache/invalidate", methods=["POST"])
@token_required
def invalidate_cache():
    """Endpoint to explicitly invalidate cache entries"""
    data = request.json
    key = data.get("key")
    
    if not key:
        return jsonify({"error": "Key required for cache invalidation"}), 400
    
    # Set cache with null value and 0 TTL to effectively invalidate
    update_cache(key, None, ttl=0)
    
    return jsonify({
        'status': 'Cache invalidated',
        'key': key
    })

@app.route("/longtask", methods=["POST"])
@token_required
@with_metrics
def long_task():
    """Endpoint to queue long-running tasks"""
    payload = request.json
    priority = request.args.get("priority", "normal")
    
    # Add metadata to the payload
    payload["_meta"] = {
        "timestamp": time.time(),
        "gateway": f"gateway-{service_port}",
        "priority": priority
    }
    
    # Send to worker service
    worker_resp = requests.post(f"{worker_service}/task", json=payload)
    
    if worker_resp.status_code != 202:
        return jsonify({'error': 'Failed to queue task'}), 500
    
    return jsonify({
        'status': 'Task queued',
        'priority': priority,
        'task_id': f"task_{int(time.time())}"
    }), 202

if __name__ == "__main__":
    app.run(port=service_port, debug=True)
