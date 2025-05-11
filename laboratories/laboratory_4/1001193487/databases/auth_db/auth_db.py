from flask import Flask, jsonify, request
import socket
from functools import wraps

app = Flask(__name__)

auth_data = [
    # {'id': '9d53f610b17204ef3ae3fa472effeb25', 'username': 'user1', 'password': 'pass1', 'role': 'admin'},
	# {'id': '16cd07fe50c01c7e684e7447f67e97e7', 'username' : 'user2', 'password': 'pass2', 'role': 'user'}
]

def limit_exposure(f):
	"""
	Decorator to restrict access to requests coming only from the API Gateway service.
	Uses socket to resolve the hostname of the gateway and compares it to the client IP.
	"""
	@wraps(f)
	def decorated_function(*args, **kwargs):
		# Get allowed hostname or IP from environment
		allowed_host = "auth_ms"
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
	return jsonify(auth_data), 200

@app.route('/getUser/<username>')
@limit_exposure
def get_user(username):
	for user in auth_data:
		if user['username'] == username:
			return jsonify(user), 200
	return jsonify({'message': f'User not found - {username}'}), 404

@app.route('/getUserById/<id>')
@limit_exposure
def get_user_by_id(id):
	for user in auth_data:
		if user['id'] == id:
			return jsonify(user), 200
	return jsonify({'message': f'User not found - {id}'}), 404

@app.route('/addUser', methods=['POST'])
@limit_exposure
def add_user():
	id = request.json.get('id') 
	username = request.json.get('username')
	password = request.json.get('password')
	role = request.json.get('role')
	if username and password:
		auth_data.append({'id': id, 'username': username, 'password': password, 'role': role})
		return jsonify({'message': 'User added successfully'}), 201
	return jsonify({'message': 'Invalid data'}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True, port=80)