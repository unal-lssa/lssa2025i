from flask import Flask, request, redirect, jsonify
import random
import time
import requests

app = Flask(__name__)

# Configuration
api_gateways = [
    {"url": "http://127.0.0.1:5000", "weight": 3, "health": True, "load": 0},
    {"url": "http://127.0.0.1:5003", "weight": 2, "health": True, "load": 0},
    {"url": "http://127.0.0.1:5006", "weight": 1, "health": True, "load": 0}
]

# Load balancing strategies
def round_robin():
    """Simple round-robin algorithm"""
    global api_gateways
    gateway = api_gateways[0]
    api_gateways = api_gateways[1:] + [api_gateways[0]]
    return gateway["url"]

def weighted_round_robin():
    """Weighted round-robin based on predefined weights"""
    total_weight = sum(gateway["weight"] for gateway in api_gateways if gateway["health"])
    if total_weight == 0:
        return None
    
    r = random.randint(1, total_weight)
    running_sum = 0
    
    for gateway in api_gateways:
        if not gateway["health"]:
            continue
        running_sum += gateway["weight"]
        if r <= running_sum:
            return gateway["url"]
    
    return api_gateways[0]["url"]  # Fallback

def least_connections():
    """Select the gateway with the least active connections"""
    available = [g for g in api_gateways if g["health"]]
    if not available:
        return None
    return min(available, key=lambda x: x["load"])["url"]

# Health check function
def health_check():
    """Periodically check health of all gateways"""
    while True:
        for gateway in api_gateways:
            try:
                # Simple health check - just see if the server responds
                response = requests.get(f"{gateway['url']}/health", timeout=2)
                gateway["health"] = response.status_code == 200
            except:
                gateway["health"] = False
        time.sleep(10)  # Check every 10 seconds

# Start health check in background
import threading
health_thread = threading.Thread(target=health_check, daemon=True)
health_thread.start()

# Stats endpoint
@app.route("/stats", methods=["GET"])
def get_stats():
    return jsonify({
        "gateways": [
            {
                "url": g["url"], 
                "health": g["health"], 
                "load": g["load"],
                "weight": g["weight"]
            } for g in api_gateways
        ],
        "strategy": request.args.get("strategy", "round_robin")
    })

@app.route("/<path:path>", methods=["GET", "POST"])
def forward(path):
    strategy = request.args.get("strategy", "round_robin")
    
    if strategy == "weighted":
        target = weighted_round_robin()
    elif strategy == "least_connections":
        target = least_connections()
    else:  # Default to round robin
        target = round_robin()
    
    if not target:
        return jsonify({"error": "No healthy gateways available"}), 503
    
    # Increment the load counter for the selected gateway
    for gateway in api_gateways:
        if gateway["url"] == target:
            gateway["load"] += 1
            # Simulate connection released after 5 seconds
            threading.Timer(5, lambda g=gateway: setattr(g, "load", max(0, g["load"]-1))).start()
    
    # Forward the request
    return redirect(f"{target}/{path}", code=307)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(port=8000, debug=True)
