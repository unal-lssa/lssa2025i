from flask import Flask, jsonify, request
import socket
from functools import wraps

app = Flask(__name__)

users_data = [
    {'username': 'user1', 'first_name': 'John', 'last_name': 'Doe', 'email': 'john.doe@mail.com' },
	{'username' : 'user2', 'first_name': 'Jane', 'last_name': 'Smith', 'email': 'jane.smith@mail.com'}
]

def limit_exposure(f):
	"""
	Decorator to restrict access to requests coming only from the API Gateway service.
	Uses socket to resolve the hostname of the gateway and compares it to the client IP.
	"""
	@wraps(f)
	def decorated_function(*args, **kwargs):
		# Get allowed hostname or IP from environment
		allowed_host = "users_ms"
		allowed_ip = socket.gethostbyname(allowed_host)
		client_ip = request.remote_addr
		if client_ip != allowed_ip:
			return jsonify({'message': 'Forbidden: Unauthorized service'}), 403
		return f(*args, **kwargs)
	return decorated_function

@app.route('/db')
@limit_exposure
def db_access():
    return jsonify({'message': 'Database access granted'}), 200

@app.route('/getAllUsers')
@limit_exposure
def get_all_users():
	return jsonify(users_data), 200

@app.route('/getUserByUsername/<username>')
@limit_exposure
def get_user_by_username(username):
	for user in users_data:
		if user['username'] == username:
			return jsonify(user), 200
	return jsonify({'message': f'User not found - {username}'}), 404

@app.route('/createUser', methods=['POST'])
@limit_exposure
def create_user():
	username = request.json.get('username')
	first_name = request.json.get('first_name')
	last_name = request.json.get('last_name')
	email = request.json.get('email')
	if username and first_name and last_name and email:
		users_data.append({'username': username, 'first_name': first_name, 'last_name': last_name, 'email': email})
		return jsonify({'message': 'User added successfully'}), 201
	return jsonify({'message': 'Invalid data'}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True, port=80)