from flask import Flask, request, jsonify
from functools import wraps
import requests
import jwt

app = Flask(__name__)
SECRET_KEY = "your_secret_key"

# Mock users for the sake of the example
USERS = {
    "user1": "password123"
}

# Function to check JWT token
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except:
            return jsonify({'message': 'Token is invalid!'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Route for user login (returns JWT token)
@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()
    username = auth.get('username')
    password = auth.get('password')
    if USERS.get(username) == password:
        token = jwt.encode({'username': username}, SECRET_KEY, algorithm="HS256")
        return jsonify({'token': token})
    return jsonify({'message': 'Invalid credentials'}), 401

# Protected route
@app.route('/data', methods=['GET'])
@token_required
def get_data():
    return jsonify({'message': 'Data accessed successfully!'}), 200

# Protected route
@app.route('/task', methods=['GET'])
@token_required
def get_task():
    url = 'http://ms-task:5000/task'
    response = requests.get(url)

    # Procesa la respuesta antes de devolverla
    if response.status_code == 200:
        return jsonify(response.json()), 200  # Devuelve el contenido JSON con el código de estado
    else:
        return jsonify({'error': 'Failed to fetch tasks', 'details': response.text}), response.status_code


# Protected route
@app.route('/project', methods=['GET'])
@token_required
def get_project():
    url = 'http://ms-project:5000/project'
    response = requests.get(url)

    # Procesa la respuesta antes de devolverla
    if response.status_code == 200:
        return jsonify(response.json()), 200  # Devuelve el contenido JSON con el código de estado
    else:
        return jsonify({'error': 'Failed to fetch project', 'details': response.text}), response.status_code

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
