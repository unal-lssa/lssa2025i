from flask import Flask, request, Response, jsonify
import requests
import itertools
import os
import time
from prometheus_client import Counter, Gauge, generate_latest

app = Flask(__name__)

# Configuration
PORT = int(os.environ.get("FLASK_PORT", 8000))
API_GATEWAYS = ["http://api_gateway1:5000", "http://api_gateway2:5003"]
gateway_cycle = itertools.cycle(API_GATEWAYS)

# Metrics
REQUEST_COUNT = Counter('lb_requests_total', 'Load balancer requests', ['target'])
ACTIVE_GATEWAYS = Gauge('lb_active_gateways', 'Number of active API gateways')
REQUEST_LATENCY = Counter('lb_request_latency_seconds', 'Request latency', ['target'])

# Health of backends
gateway_health = {gateway: True for gateway in API_GATEWAYS}

# Update the health of API gateways
def check_gateway_health():
    while True:
        healthy_count = 0
        for gateway in API_GATEWAYS:
            try:
                response = requests.get(f"{gateway}/health", timeout=2)
                gateway_health[gateway] = response.status_code == 200
                if gateway_health[gateway]:
                    healthy_count += 1
            except:
                gateway_health[gateway] = False
        
        ACTIVE_GATEWAYS.set(healthy_count)
        time.sleep(5)  # Check every 5 seconds

import threading
health_thread = threading.Thread(target=check_gateway_health, daemon=True)
health_thread.start()

# Get next healthy gateway
def get_healthy_gateway():
    for _ in range(len(API_GATEWAYS)):
        gateway = next(gateway_cycle)
        if gateway_health[gateway]:
            return gateway
    return None  # No healthy gateways

# Metrics endpoint
@app.route("/metrics")
def metrics():
    return generate_latest()

# Health check
@app.route("/health")
def health():
    return jsonify({
        'status': 'up',
        'gateways': gateway_health
    })

# Forward all other requests to API gateways
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def forward(path):
    gateway = get_healthy_gateway()
    if not gateway:
        return jsonify({'error': 'No healthy API gateways available'}), 503
    
    REQUEST_COUNT.labels(target=gateway).inc()
    start_time = time.time()
    
    # Forward the request
    target_url = f"{gateway}/{path}"
    
    try:
        # Forward the request with all headers, query params, and body
        response = requests.request(
            method=request.method,
            url=target_url,
            headers={k: v for k, v in request.headers if k != 'Host'},
            params=request.args,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            timeout=10
        )
        
        REQUEST_LATENCY.labels(target=gateway).inc(time.time() - start_time)
        
        # Return the response with original status, headers, and content
        return Response(
            response.content,
            status=response.status_code,
            headers=dict(response.headers)
        )
    except Exception as e:
        # Mark gateway as unhealthy on connection error
        gateway_health[gateway] = False
        return jsonify({'error': f'Error forwarding to API gateway: {str(e)}'}), 500

# Root path
@app.route("/")
def root():
    return jsonify({
        'service': 'Load Balancer',
        'status': 'running',
        'gateways': gateway_health
    })

if __name__ == "__main__":
    print(f"Load balancer starting on port {PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=True)
