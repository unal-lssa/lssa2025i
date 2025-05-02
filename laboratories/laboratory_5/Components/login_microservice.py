from functools import wraps
from flask import Flask, request, jsonify
import jwt, time
import threading
import os
from Components.status_tracker import register_status
app = Flask(__name__)
SECRET_KEY = "secret"
SERVICE_NAME = "LOGIN_MS"
USERS = {
    "user1": "password123"
}

request_timestamps = []
rate_lock = threading.Lock()

# Decorador para rate limiting
def rate_limited(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        global request_timestamps

        MAX_REQUESTS = int(os.getenv("MAX_REQUESTS_PER_TIME", 2))
        RATE_TIME = int(os.getenv("RATE_LIMIT_TIME", 60))

        now = time.time()
        with rate_lock:
            request_timestamps[:] = [t for t in request_timestamps if now - t < RATE_TIME]
            if len(request_timestamps) >= MAX_REQUESTS:
                print("Microservice Login error: 'Too many requests, try again later'")
                register_status(SERVICE_NAME, 429)
                return jsonify({'Microservice Login error': 'Too many login attempts, try again later'}), 429
            request_timestamps.append(now)

        return f(*args, **kwargs)
    return decorated_function

@app.route('/validate_token', methods=['POST'])
def validate_token():
    token = request.json.get('token')
    if not token:
        register_status(SERVICE_NAME, 400)
        return jsonify({'error': 'Token is missing'}), 400

    try:
        jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        register_status(SERVICE_NAME, 200)
        return jsonify({'valid': True}), 200
    except jwt.ExpiredSignatureError:
        register_status(SERVICE_NAME, 403)
        return jsonify({'error': 'Token expired'}), 403
    except jwt.InvalidTokenError:
        register_status(SERVICE_NAME, 403)
        return jsonify({'error': 'Invalid token'}), 403

@app.route('/login', methods=['POST'])
@rate_limited
def login():
    auth = request.get_json()
    username = auth.get('username')
    password = auth.get('password')

    if USERS.get(username) == password:
        token = jwt.encode({'username': username}, SECRET_KEY, algorithm="HS256")
        register_status(SERVICE_NAME, 200)
        return jsonify({'token': token})
    register_status(SERVICE_NAME, 401)
    return jsonify({'message': 'Invalid credentials'}), 401

if __name__ == "__main__":
    app.run(port=5009, debug=True)
