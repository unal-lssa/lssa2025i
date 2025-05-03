from flask import Flask, jsonify, request
import requests
import os
from dotenv import load_dotenv
from functools import wraps
import socket
import json
import redis

# Carga variables de entorno\load_dotenv()
load_dotenv()

app = Flask(__name__)

# Configuración de servicios y caché
db_urls = ['http://users_db-0:80/', 'http://users_db-1:80/', 'http://users_db-2:80/']
SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
redis_host = 'users_cache'  # Cambiado a http para evitar problemas de conexión
redis_port = 6379
redis_db = 0
cache_ttl = 300  # Tiempo de vida de caché en segundos

# Conexión a Redis con respuestas decodificadas como str
r = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)

def limit_exposure(f):
	"""
	Decorator to restrict access only from API Gateway service.
	"""
	@wraps(f)
	def decorated_function(*args, **kwargs):
		allowed_hosts = ["api_gateway", "api_gateway_replica"]
		allowed_ips = [socket.gethostbyname(allowed_host) for allowed_host in allowed_hosts]
		client_ip = request.remote_addr
		if client_ip not in allowed_ips:
			return jsonify({'message': 'Forbidden: Unauthorized service'}), 403
		return f(*args, **kwargs)
	return decorated_function

@app.route('/getUserById/<id>')
@limit_exposure
def get_user_by_id(id):
	cache_key = f"user:{id}"
	# Intentar cache
	cached = r.get(cache_key)
	if cached:
		print(f"Cache hit for {cache_key}")
		return jsonify(json.loads(cached)), 200
	# En caso de miss
	try:
		shard_index = hash(id) % len(db_urls)
		print(f"Shard index for {id}: {shard_index}")
		db_url = db_urls[shard_index]
		response = requests.get(f'{db_url}/getUserById/{id}', timeout=5)
		if response.status_code == 200:
			data = response.json()
			# Almacenar en cache
			r.set(cache_key, json.dumps(data), ex=cache_ttl)
			return jsonify(data), 200
		else:
			return jsonify({'message': f'User not found - {id}'}), 404
	except requests.exceptions.RequestException as e:
		return jsonify({'message': f'Error connecting to database: {str(e)}'}), 500

@app.route('/getAllUsers')
@limit_exposure
def get_all_users():
	cache_key = 'users:all'
	# Intentar cache
	cached = r.get(cache_key)
	if cached:
		print(f"Cache hit for {cache_key}")
		return jsonify(json.loads(cached)), 200
	try:
		all_users = []
		errors = []
		for db_url in db_urls:
			try:
				response = requests.get(f'{db_url}/getAllUsers', timeout=5)
				if response.status_code == 200:
					users = response.json()
					if isinstance(users, list):
						all_users.extend(users)
					else:
						errors.append(f"Invalid data from {db_url}")
				else:
					errors.append(f"Error fetching users from {db_url}")
			except requests.exceptions.RequestException as e:
				errors.append(f"Error connecting to {db_url}: {str(e)}")
		if all_users:
			# Almacenar en cache
			r.set(cache_key, json.dumps(all_users), ex=cache_ttl)
			return jsonify(all_users), 200
		else:
			return jsonify({'message': 'Error fetching users', 'errors': errors}), 500
	except requests.exceptions.RequestException as e:
		return jsonify({'message': f'Error connecting to database: {str(e)}'}), 500

@app.route('/createUser', methods=['POST'])
@limit_exposure
def create_user():
	user_id = request.json.get('id')
	username = request.json.get('username')
	first_name = request.json.get('first_name')
	last_name = request.json.get('last_name')
	email = request.json.get('email')
	if username and first_name and last_name and email:
		try:
			shard_index = hash(user_id) % len(db_urls)
			print(f"Shard index for {user_id}: {shard_index}")
			db_url = db_urls[shard_index]
			response = requests.post(
				f'{db_url}/createUser',
				json={'id': user_id, 'username': username, 'first_name': first_name, 'last_name': last_name, 'email': email},
				timeout=5
			)
			if response.status_code == 201:
				# Invalidar caché relevante
				r.delete(f'user:{username}')
				r.delete('users:all')
				return jsonify({'message': 'User added successfully'}), 201
			else:
				return jsonify({'message': 'Error creating user'}), 500
		except requests.exceptions.RequestException as e:
			return jsonify({'message': f'Error connecting to database: {str(e)}'}), 500
	else:
		return jsonify({'message': 'Invalid data'}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=80)
