from flask import Flask, jsonify, request
from functools import wraps
import mysql.connector

app = Flask(__name__)

# Lista blanca de IPs permitidas
ALLOWED_IPS = ["172.18.0.1"]  # IPs específicas
ALLOWED_SERVICES = ["ms-project"]  # Servicios internos de Docker

# Function to check if the request comes from an authorized IP address
def limit_exposure(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        client_host = request.host.split(':')[0]  # Extraer el nombre del host
        print(f"Request received from IP: {client_ip}, Host: {client_host}")

        if client_host not in ALLOWED_SERVICES:
            print(f"Unauthorized access attempt from Host: {client_host}, IP: {client_ip}")
            return jsonify({'message': 'Forbidden: Unauthorized Host', 'host': client_host, 'ip': client_ip}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/project', methods=['GET'])
@limit_exposure # Apply the limit exposure tactic to this route
def get_tasks():
    conn = mysql.connector.connect(
        host='projects_db',
        user='root',
        password='root',
        database='projects_db'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(tasks=rows)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
