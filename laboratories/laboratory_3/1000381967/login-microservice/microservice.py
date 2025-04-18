from flask import Flask, jsonify, request
from functools import wraps
import socket
import requests

app = Flask(__name__)

try:
    AUTHORIZED_IP = socket.gethostbyname('api-gateway')
except socket.gaierror:
    AUTHORIZED_IP = None
    print("Error: Unable to resolve 'api-gateway' to an IP address")

def limit_exposure(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        if client_ip != AUTHORIZED_IP:  
            return jsonify({'message': 'Forbidden: Unauthorized IP'}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['POST'])
@limit_exposure 
def login():
    try: 
        auth = request.get_json()
        username = auth.get('username')
        password = auth.get('password')
    
        response = requests.post(
                'http://login-database:5002/login', 
                json={'username': username, 'password': password},
                headers={'Content-Type': 'application/json'}
        )
    
        if response.status_code == 200:
            return jsonify(response.json()), 200
        return jsonify(response.json()), 401
    except requests.exceptions.RequestException as e:
        return jsonify({'message': 'Error at microservice', 'Details: ': str(e)}), 500
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5001)