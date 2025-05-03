from flask import Flask, request, jsonify
from functools import wraps
import requests
import jwt
import logging

app = Flask(__name__)
SECRET_KEY = "secret"

# Mock users for the sake of the example
USERS = {"user1": "password123"}

# Servicios externos
CACHE_URL = "http://cache:5000/cache"
DB_URL = "http://database:5000/db"
MS_URL = "http://microservice:5000/process"
WORKER_URL = "http://worker:5000/task"

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Funciones utilitarias ---
def get_json_safe(url):
    try:
        resp = requests.get(url, timeout=3)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching {url}: {e}")
        return None


def post_json_safe(url, payload):
    try:
        resp = requests.post(url, json=payload, timeout=3)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        logger.error(f"Error posting to {url}: {e}")
        return None


# --- Decoradores ---
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"message": "Token is missing!"}), 403

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"message": "Invalid authorization header format."}), 403

        token = parts[1]

        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"message": "Token is invalid!"}), 403

        return f(*args, **kwargs)

    return decorated_function


def cache_response(key_func):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = key_func(*args, **kwargs)
            cache_resp = get_json_safe(f"{CACHE_URL}/{cache_key}")
            if cache_resp and cache_resp.get("value") is not None:
                return jsonify({"cached": True, "data": cache_resp["value"]})

            result = f(*args, **kwargs)
            result_json = result.get_json()
            data = result_json.get("data") if result_json else None

            if data is not None:
                post_json_safe(f"{CACHE_URL}/{cache_key}", {"value": data})

            return jsonify({"cached": False, "data": data})

        return decorated_function

    return decorator


#  --- Rutas ---
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/login", methods=["POST"])
def login():
    auth = request.get_json()
    username = auth.get("username")
    password = auth.get("password")
    if USERS.get(username) == password:
        token = jwt.encode({"username": username}, SECRET_KEY, algorithm="HS256")
        return jsonify({"token": token})
    return jsonify({"message": "Invalid credentials"}), 401


@app.route("/data", methods=["GET"])
@token_required
@cache_response(lambda: request.args.get("key", "my_data"))
def get_data():
    db_resp = get_json_safe(DB_URL)
    if not db_resp:
        return jsonify({"error": "Database service unavailable"}), 500
    return jsonify({"data": db_resp.get("message")})


@app.route("/process", methods=["GET"])
@token_required
@cache_response(lambda: request.args.get("key", "ms_1"))
def ms_process():
    db_resp = get_json_safe(MS_URL)
    if not db_resp:
        return jsonify({"error": "Microservice unavailable"}), 500
    return jsonify({"data": db_resp.get("message")})


@app.route("/longtask", methods=["POST"])
@token_required
def long_task():
    payload = request.get_json()
    result = post_json_safe(WORKER_URL, payload)
    if result is None:
        return jsonify({"error": "Failed to queue task"}), 500
    return jsonify({"status": "Task queued"}), 202


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        threaded=True
    )
