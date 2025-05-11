from flask import Flask, request, jsonify
from functools import wraps
import jwt
import requests
import pika
import json
import datetime

app = Flask(__name__)
SECRET_KEY = "secret"

# Auth decorator
def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "Missing token"}), 403
        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except:
            return jsonify({"error": "Invalid token"}), 403
        return f(*args, **kwargs)
    return wrapper

@app.route("/auth", methods=["POST"])
def check_user_exists():
    auth_response = requests.post("http://users-loadbalancer/user", json=request.json)

    if auth_response.status_code == 200 and auth_response.json().get("exists"):
        username = request.json.get("username")
        token = jwt.encode({
            "username": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, SECRET_KEY, algorithm="HS256")

        return jsonify({"token": token}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route("/data", methods=["GET"])
@token_required
def get_data():
    resp = requests.get("http://products-microservice:5000/products")
    return jsonify(resp.json())

@app.route("/longtask", methods=["POST"])
@token_required
def queue_task():
    try:
        # Validate the request payload
        if not request.json or "task" not in request.json:
            return jsonify({"error": "Invalid payload"}), 400
        
        payload = request.json
        connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq-queue", port=5672, credentials=pika.PlainCredentials("user", "password")))
        channel = connection.channel()
        channel.queue_declare(queue="tasks")
        channel.basic_publish(exchange="", routing_key="tasks", body=json.dumps(payload))
        connection.close()
        return jsonify({"status": "Task queued"}), 202
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
