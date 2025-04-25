from flask import Flask, request, jsonify
import jwt
from functools import wraps
import requests

app = Flask(__name__)
SECRET_KEY = "your_secret_key"
# Mock users for the sake of the example
USERS = {"user1": "password123"}


# Function to check JWT token
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"message": "Token is missing!"}), 403
        try:
            print(token)
            # Remove "Bearer " if present
            if token.startswith("Bearer "):
                token = token[7:]

            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except Exception as e:
            print(e)
            return jsonify({"message": "Token is invalid!"}), 403
        return f(*args, **kwargs)

    return decorated_function


# Route for user login (returns JWT token)
@app.route("/login", methods=["POST"])
def login():
    auth = request.get_json()
    username = auth.get("username")
    password = auth.get("password")
    if USERS.get(username) == password:
        token = jwt.encode({"username": username}, SECRET_KEY, algorithm="HS256")
        return jsonify({"token": token})
    return jsonify({"message": "Invalid credentials"}), 401


# Route for accesing microservice
@app.route("/service1", methods=["GET"])
@token_required
def service_1():
    response = requests.get("http://microservice:5001/microservice")
    if response.status_code != 200:
        return (
            jsonify({"message": "Internal Service Error. Contact the administrator."}),
            500,
        )
    return response.content


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
