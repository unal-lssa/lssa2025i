from flask import Flask, request, jsonify, Response, abort
import jwt
import requests
import os
from functools import wraps

app = Flask(__name__)
SECRET_KEY = os.environ.get("SECRET_KEY", "default_secret_key")
AUTHORIZED_IPS = os.environ.get("AUTHORIZED_IPS", "127.0.0.1,172.18.0.1").split(",")



# ===== JWT DECORATOR =====
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            parts = request.headers['Authorization'].split()
            if len(parts) == 2 and parts[0] == "Bearer":
                token = parts[1]

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user = data  # attach payload to request
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid'}), 401

        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not hasattr(request, 'user') or request.user.get("role") != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return wrapper


@app.before_request
def limit_remote_addr():
    ip = request.remote_addr
    if ip not in AUTHORIZED_IPS:
        abort(403, description=f"Forbidden: IP {ip} not authorized")


# ===== LOGIN / REGISTER FORWARDING =====
@app.route("/login", methods=["POST"])
def proxy_login():
    try:
        resp = requests.post("http://login_service:5001/login", json=request.get_json())
        return Response(resp.content, status=resp.status_code, content_type=resp.headers.get("Content-Type"))
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Login service unavailable"}), 503


@app.route("/register", methods=["POST"])
def proxy_register():
    try:
        resp = requests.post("http://login_service:5001/register", json=request.get_json())
        return Response(resp.content, status=resp.status_code, content_type=resp.headers.get("Content-Type"))
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Login service unavailable"}), 503


# ===== APPSETTINGS (Admin-only) =====
@app.route("/appsettings", methods=["GET", "POST"])
@token_required
@admin_required
def proxy_appsettings():
    try:
        service_url = "http://appsettings_service:5002/settings"

        if request.method == "GET":
            resp = requests.get(service_url)
        else:
            resp = requests.post(service_url, json=request.get_json())

        return Response(resp.content, status=resp.status_code, content_type=resp.headers.get("Content-Type"))

    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Appsettings service unavailable"}), 503


# ===== BLOGPOSTS (All users) =====
@app.route("/blogposts", methods=["GET", "POST"])
@token_required
def proxy_blogposts():
    try:
        service_url = "http://blogpost_service:5003/posts"

        if request.method == "GET":
            resp = requests.get(service_url)
        else:
            payload = request.user
            data = request.get_json()
            data["owner"] = payload.get("username", "anonymous")
            resp = requests.post(service_url, json=data)

        return Response(resp.content, status=resp.status_code, content_type=resp.headers.get("Content-Type"))

    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Blogpost service unavailable"}), 503


# ===== HEALTH CHECK =====
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API Gateway is running"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
