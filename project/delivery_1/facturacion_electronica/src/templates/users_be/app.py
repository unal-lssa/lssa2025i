import hashlib
import os
import socket

import mysql.connector
from flask import Flask, jsonify, request

# Configurar el entorno de Flask
app = Flask(__name__)

# Users microservice port
USERS_BACKEND_PORT = os.getenv("USERS_BACKEND_PORT", 8010)

# Database connection parameters
USERS_DB_HOST = os.getenv("USERS_DB_HOST", "users_db")


# Default route
@app.route("/")
def home():
    return jsonify(message="Hello from the Users Mircroservice!")


# Endpoint ping para verificar la comunicacion con el Microservicio
@app.route("/ping", methods=["GET"])
def ping():
    return (
        jsonify(
            {
                "status": 200,
                "data": {
                    "API Gateway IP": request.headers.get('X-Forwarded-For', request.remote_addr),
                    "Users Microservice IP": socket.gethostbyname(socket.gethostname()),
                    "DB Tables": list_tables()[0].get_json(),
                },
                "message": "Pong desde el Microservicio de Users",
            }
        ),
        200,
    )


# Endpoint de autenticación
@app.route("/auth", methods=["POST"])
def authenticate():
    """Endpoint de autenticación"""
    auth_data = request.get_json()
    if not auth_data or "doc_id" not in auth_data or "password" not in auth_data:
        return jsonify({"error": "Credenciales inválidas doc_id and password required"}), 401

    # Obtiene los datos de autenticación del body de la solicitud
    doc_id = auth_data.get("doc_id")
    password = auth_data.get("password")

    # Obtiene el usuario de la base de datos
    conn = mysql.connector.connect(
        host=USERS_DB_HOST,
        user='root',
        password='root',
        database='users_db'
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE doc_id = %s", (doc_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    # validacion de la contraseña con md5
    md5_pwd = hashlib.md5(password.encode()).hexdigest()
    if user["pwd"] != md5_pwd:
        return jsonify({"error": "Credenciales inválidas"}), 401
    # Si la autenticación es exitosa, se devuelve el usuario
    return jsonify({"doc_id": user["doc_id"], "role_name": user["role_name"]}), 200


# Endpoint para listar las tablas de la base de datos
@app.route("/list-tables", methods=["GET"])
def list_tables():
    conn = mysql.connector.connect(
        host=USERS_DB_HOST,
        user='root',
        password='root',
        database='users_db'
    )
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(tables=[table[0] for table in tables]), 200



# AJUSTAR
# @app.route('/create', methods=['POST'])
# def create():
#     data = request.json
#     conn = mysql.connector.connect(
#         host='{USERS_DB_HOST}',
#         user='root',
#         password='root',
#         database='{database}'
#     )
#     cursor = conn.cursor()
#     cursor.execute("INSERT INTO systems (name) VALUES (%s)", (data['name'],))
#     conn.commit()
#     cursor.close()
#     conn.close()
#     return jsonify(status="created")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=USERS_BACKEND_PORT)
