from flask import Flask, jsonify, request
import requests
import jwt
from dotenv import load_dotenv
import os
from functools import wraps
import socket

load_dotenv()

app = Flask(__name__)

db_url = 'http://auth_db:80/'
SECRET_KEY = "your_secret_key"

def limit_exposure(f):
	"""
	Decorator to restrict access to requests coming only from the API Gateway service.
	Uses socket to resolve the hostname of the gateway and compares it to the client IP.
	"""
	@wraps(f)
	def decorated_function(*args, **kwargs):
		# Get allowed hostname or IP from environment
		allowed_host = "api_gateway"
		allowed_ip = socket.gethostbyname(allowed_host)
		client_ip = request.remote_addr
		if client_ip != allowed_ip:
			return jsonify({'message': 'Forbidden: Unauthorized service'}), 403
		return f(*args, **kwargs)
	return decorated_function

@app.route('/login', methods=['POST'])
@limit_exposure
def login():
	# Query the database for user credentials
	username = request.json.get('username')
	password = request.json.get('password')
	if username and password:
		response = requests.get(f'{db_url}/getUser/{username}', timeout=5)
		if response.status_code == 200:
			user_data = response.json()
			print(user_data)
			if user_data['password'] == password:
				# Generate JWT token
				token = jwt.encode({'username': username}, SECRET_KEY, algorithm='HS256')
				return jsonify({'message': 'Login successful', 'token': token}), 200
			else:
				return jsonify({'message': 'Invalid credentials'}), 401
		else:
			return jsonify({'message': 'User not found'}), 404
	return jsonify({'message': 'Invalid data'}), 400


@app.route('/register', methods=['POST'])
@limit_exposure
def register():
	# Register a new user
	username = request.json.get('username')
	password = request.json.get('password')
	if username and password:
		response = requests.post(f'{db_url}/addUser', json={'username': username, 'password': password}, timeout=5)
		if response.status_code == 201:
			return jsonify({'message': 'User registered successfully'}), 201
		else:
			return jsonify({'message': 'User registration failed'}), 400
	return jsonify({'message': 'Invalid data'}), 400

@app.route('/is_admin/', methods=['GET'])
@limit_exposure
def is_admin():
	# Check if the user is an admin
	token = request.headers.get('Authorization')
	if not token:
		return jsonify({'message': 'Token is missing!'}), 403
	
	try:
		data = jwt.decode(token.split(' ')[1], SECRET_KEY, algorithms=['HS256'])
		print(data)
		username = data['username']
		response = requests.get(f'{db_url}/getUser/{username}', timeout=5)
		if response.status_code == 200:
			user_data = response.json()
			if user_data['role'] == 'admin':
				return jsonify({'message': 'User is an admin'}), 200
			else:
				return jsonify({'message': 'User is not an admin'}), 403
		else:
			return jsonify({'message': 'User not found'}), 404
	except jwt.ExpiredSignatureError:
		return jsonify({'message': 'Token has expired'}), 401
	except jwt.InvalidTokenError:
		return jsonify({'message': 'Invalid token'}), 401

@app.route('/getUser', methods=['GET'])
@limit_exposure
def get_user():
	# Get user data using the JWT token
	token = request.headers.get('Authorization')
	if not token:
		return jsonify({'message': 'Token is missing!'}), 403
	
	try:
		data = jwt.decode(token.split(' ')[1], SECRET_KEY, algorithms=['HS256'])
		username = data['username']
		response = requests.get(f'{db_url}/getUser/{username}', timeout=5)
		if response.status_code == 200:
			return jsonify(response.json()), 200
		else:
			return jsonify({'message': 'User not found'}), 404
	except jwt.ExpiredSignatureError:
		return jsonify({'message': 'Token has expired'}), 401
	except jwt.InvalidTokenError:
		return jsonify({'message': 'Invalid token'}), 401


@app.route('/validate_token', methods=['POST'])
@limit_exposure
def validate_token():
	token = request.json.get('token')
	if token:
		try:
			jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
			return jsonify({'message': 'Token is valid'}), 200
		except jwt.ExpiredSignatureError:
			return jsonify({'message': 'Token has expired'}), 401
		except jwt.InvalidTokenError:
			return jsonify({'message': 'Invalid token'}), 401
	return jsonify({'message': 'No token provided'}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True, port=80)