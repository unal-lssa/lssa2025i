from flask import Flask, jsonify
import os
import mysql.connector

# Configurar el entorno de Flask
app = Flask(__name__)

# Users microservice port
USERS_BACKEND_PORT = os.getenv("USERS_BACKEND_PORT", 5007)

# Database connection parameters
USERS_DB_HOST = os.getenv("USERS_DB_HOST", "users_db")


# Default route
@app.route('/')
def home():
    return jsonify(message="Hello from the Users Mircroservice!")

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=USERS_BACKEND_PORT)
