from flask import Flask, request, jsonify
import jwt, requests
from functools import wraps
import os
import time
import random
from prometheus_client import Counter, Histogram, generate_latest

app = Flask(__name__)
SECRET_KEY = "secret"

# Environment variables with defaults
PORT = int(os.environ.get("FLASK_PORT", 5000))
GATEWAY_ID = os.environ.get("GATEWAY_ID", "1")
CACHE_HOST = os.environ.get("CACHE_HOST", "127.0.0.1")
DATABASE_HOST = os.environ.get("DATABASE_HOST", "127.0.0.1")
WORKER_HOST = os.environ.get("WORKER_HOST", "127.0.0.1")
MICROSERVICE_HOST = os.environ.get("MICROSERVICE_HOST", "127.0.0.1")

# Configure multiple microservice instances with correct Docker service names
MICROSERVICE_INSTANCES = [
    {"host": MICROSERVICE_HOST, "port": 5001},        # Default instance
    {"host": "microservice2", "port": 5006},          # Additional instance 1
    {"host": "microservice3", "port": 5007},          # Additional instance 2
]

# Prometheus metrics
REQUEST_COUNT = Counter('api_requests_total', 'Total API requests', ['endpoint', 'gateway_id'])
REQUEST_LATENCY = Histogram('api_request_latency_seconds', 'API request latency', ['endpoint', 'gateway_id'])
CACHE_HITS = Counter('cache_hits_total', 'Cache hits', ['key', 'gateway_id'])
CACHE_MISSES = Counter('cache_misses_total', 'Cache misses', ['key', 'gateway_id'])

# Decorators (reuse token auth if desired)
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

# Metrics endpoint
@app.route("/metrics")
def metrics():
    return generate_latest()

# Health check endpoint
@app.route("/health")
def health():
    return jsonify({
        'status': 'up', 
        'gateway_id': GATEWAY_ID,
        'timestamp': time.time()
    })

# Generate token endpoint - for testing
@app.route("/token", methods=["GET"])
def get_token():
    token = jwt.encode({'user': 'test'}, SECRET_KEY, algorithm="HS256")
    return jsonify({'token': token})

# Cached data access
@app.route("/data", methods=["GET"])
@token_required
def get_data():
    start_time = time.time()
    REQUEST_COUNT.labels(endpoint='/data', gateway_id=GATEWAY_ID).inc()
    
    try:
        cache_key = request.args.get('key', 'my_data')
        cache_resp = requests.get(f"http://{CACHE_HOST}:5004/cache/{cache_key}").json()
        
        if cache_resp.get('value'):
            # Cache hit
            CACHE_HITS.labels(key=cache_key, gateway_id=GATEWAY_ID).inc()
            result = {'cached': True, 'data': cache_resp['value'], 'gateway_id': GATEWAY_ID}
        else:
            # Cache miss
            CACHE_MISSES.labels(key=cache_key, gateway_id=GATEWAY_ID).inc()
            # Simulate DB fetch
            db_resp = requests.get(f"http://{DATABASE_HOST}:5002/db").json()
            requests.post(f"http://{CACHE_HOST}:5004/cache/{cache_key}", 
                         json={'value': db_resp['message']})
            result = {'cached': False, 'data': db_resp['message'], 'gateway_id': GATEWAY_ID}
        
        REQUEST_LATENCY.labels(endpoint='/data', gateway_id=GATEWAY_ID).observe(time.time() - start_time)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Microservice proxy with load balancing
@app.route("/process", methods=["GET"])
@token_required
def process():
    start_time = time.time()
    REQUEST_COUNT.labels(endpoint='/process', gateway_id=GATEWAY_ID).inc()
    
    try:
        # Select a random microservice instance (simple load balancing)
        instance = random.choice(MICROSERVICE_INSTANCES)
        ms_host = instance["host"]
        ms_port = instance["port"]
        
        print(f"Routing to microservice at {ms_host}:{ms_port}")  # Debug log
        ms_resp = requests.get(f"http://{ms_host}:{ms_port}/process").json()
        
        REQUEST_LATENCY.labels(endpoint='/process', gateway_id=GATEWAY_ID).observe(time.time() - start_time)
        return jsonify({
            'message': ms_resp['message'],
            'service_id': ms_resp.get('service_id', 'unknown'),
            'gateway_id': GATEWAY_ID
        })
    except Exception as e:
        print(f"Error connecting to microservice: {str(e)}")  # Debug log
        return jsonify({'error': str(e)}), 500

# Trigger async task
@app.route("/longtask", methods=["POST"])
@token_required
def long_task():
    start_time = time.time()
    REQUEST_COUNT.labels(endpoint='/longtask', gateway_id=GATEWAY_ID).inc()
    
    try:
        payload = request.json
        worker_resp = requests.post(f"http://{WORKER_HOST}:5005/task", json=payload).json()
        
        REQUEST_LATENCY.labels(endpoint='/longtask', gateway_id=GATEWAY_ID).observe(time.time() - start_time)
        return jsonify({
            'status': worker_resp['status'], 
            'task_id': worker_resp.get('task_id', 'unknown'),
            'gateway_id': GATEWAY_ID
        }), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    print(f"API Gateway {GATEWAY_ID} starting on port {PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=True)
