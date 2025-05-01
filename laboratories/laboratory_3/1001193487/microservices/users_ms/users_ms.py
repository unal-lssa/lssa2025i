from flask import Flask, jsonify, request
import requests
from dotenv import load_dotenv
from functools import wraps
import socket

load_dotenv()

app = Flask(__name__)

db_url = 'http://users_db:80/'
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

@app.route('/getUserByUsername/<username>')
@limit_exposure
def get_user_by_username(username):
	try:
		response = requests.get(f'{db_url}/getUserByUsername/{username}', timeout=5)
		if response.status_code == 200:
			return jsonify(response.json()), 200
		else:
			return jsonify({'message': f'User not found - {username}'}), 404
	except requests.exceptions.RequestException as e:
		return jsonify({'message': f'Error connecting to database: {str(e)}'}), 500
	
@app.route('/getAllUsers')
@limit_exposure
def get_all_users():
	try:
		response = requests.get(f'{db_url}/getAllUsers', timeout=5)
		if response.status_code == 200:
			return jsonify(response.json()), 200
		else:
			return jsonify({'message': 'Error fetching users'}), 500
	except requests.exceptions.RequestException as e:
		return jsonify({'message': f'Error connecting to database: {str(e)}'}), 500
	
@app.route('/createUser', methods=['POST'])
@limit_exposure
def create_user():
	username = request.json.get('username')
	first_name = request.json.get('first_name')
	last_name = request.json.get('last_name')
	email = request.json.get('email')
	if username and first_name and last_name and email:
		try:
			response = requests.post(f'{db_url}/createUser', json={'username': username, 'first_name': first_name, 'last_name': last_name, 'email': email}, timeout=5)
			if response.status_code == 201:
				return jsonify({'message': 'User added successfully'}), 201
			else:
				return jsonify({'message': 'Error creating user'}), 500
		except requests.exceptions.RequestException as e:
			return jsonify({'message': f'Error connecting to database: {str(e)}'}), 500
	else:
		return jsonify({'message': 'Invalid data'}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True, port=80)