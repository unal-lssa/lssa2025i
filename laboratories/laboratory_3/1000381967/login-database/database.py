from flask import Flask, jsonify, request
import jwt
import os
from functools import wraps
import socket

try:
    AUTHORIZED_IP = socket.gethostbyname('login-microservice')
except socket.gaierror:
    AUTHORIZED_IP = None
    print("Error: Unable to resolve 'login-microservice' to an IP address")

USERS = {
    "user1": "password123"
}

SECRET_KEY = os.getenv("SECRET_KEY")

def limit_exposure(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        if client_ip != AUTHORIZED_IP:  
            return jsonify({'message': 'Forbidden: Unauthorized IP'}), 403
        return f(*args, **kwargs)
    return decorated_function

app = Flask(__name__)


@app.route('/login', methods=['POST'])
@limit_exposure
def login():
    auth = request.get_json()
    username = auth.get('username')
    password = auth.get('password')

    if USERS.get(username) == password:
        token = jwt.encode({'username': username}, SECRET_KEY, algorithm="HS256")
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 401

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5002)