from flask import Flask, jsonify, request, redirect
import jwt, requests
from functools import wraps

SECRET_KEY = "secret"
AUTH_LB = "http://127.0.0.1:5013"
SERVICE_LB = "http://127.0.0.1:5002"
WORKER_LB = "http://127.0.0.1:5007"
CACHE_URL = "http://127.0.0.1:5006/cache/my_data"


# Decorator for token auth
def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        if not token:
            return jsonify({"error": "Missing token"}), 403
        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except Exception:
            return jsonify({"error": "Invalid or expired token"}), 403
        return f(*args, **kwargs)

    return wrapper


app = Flask(__name__)


# Authentication route
@app.route("/auth/login", methods=["POST"])
def auth_login():
    # Forward to auth load balancer
    resp = requests.post(f"{AUTH_LB}/login", json=request.json)
    return (resp.content, resp.status_code, resp.headers.items())


@app.route("/data", methods=["GET"])
@token_required
def get_data():
    # Try cache
    cache_resp = requests.get(CACHE_URL).json()
    if cache_resp.get("value"):
        return jsonify({"cached": True, "data": cache_resp["value"]})
    # Fetch from service via service load balancer
    svc_resp = requests.get(f"{SERVICE_LB}/data").json()
    # Update cache
    requests.post(CACHE_URL, json={"value": svc_resp.get("data")})
    return jsonify({"cached": False, "data": svc_resp.get("data")})


@app.route("/longtask", methods=["POST"])
@token_required
def long_task():
    payload = request.json
    # Enqueue on worker load balancer
    requests.post(f"{WORKER_LB}/task", json=payload)
    return jsonify({"status": "Task queued"}), 202


if __name__ == "__main__":
    import sys

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    app.run(port=port, debug=True)
