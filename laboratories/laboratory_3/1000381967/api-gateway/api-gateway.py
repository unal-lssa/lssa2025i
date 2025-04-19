from flask import Flask, request, jsonify
import jwt
import os
import requests
from functools import wraps
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
)

SECRET_KEY = os.getenv("SECRET_KEY")

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
@limiter.limit("5 per minute")
def login():
    try: 
        auth = request.get_json()
        if not auth or not auth.get('username') or not auth.get('password'):
            return jsonify({'message': 'Missing credentials'}), 404
        
        username = auth.get('username')
        password = auth.get('password')

        response = requests.post(
            'http://login-microservice:5001/login',
            json={'username': username, 'password': password},  
            headers={'Content-Type': 'application/json'}
        )
       
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify(response.json()), 401
    except requests.exceptions.RequestException as e:
        return jsonify({'Message': 'Error at api-gateway', 'Details': str(e)}), 500

@app.route('/products', methods=['GET'])
@token_required
@limiter.limit("100 per minute")
def query_products():
    try:
        response = requests.get(
            'http://products-microservice:5003/products'
        )
        
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify(response.json()), 404
    except requests.exceptions.RequestException as e:
        return jsonify({'message': 'Error at api-gateway', 'Details: ': str(e)}), 500
    
@app.route('/companies', methods=['GET'])
@token_required
@limiter.limit("100 per minute")
def query_companies():
    try:
        response = requests.get(
            'http://companies-microservice:5005/companies'
        )
        
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify(response.json()), 404
    except requests.exceptions.RequestException as e:
        return jsonify({'message': 'Error at api-gateway', 'Details: ': str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)