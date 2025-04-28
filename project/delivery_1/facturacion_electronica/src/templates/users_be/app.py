from flask import Flask, jsonify, request
import os
import mysql.connector

# Configurar el entorno de Flask
app = Flask(__name__)

# Users microservice port
USERS_BACKEND_PORT = os.getenv("USERS_BACKEND_PORT", 5007)

# Database connection parameters
USERS_DB_HOST = os.getenv("USERS_DB_HOST", "users_db")


# Default route
@app.route('/', methods=['GET', 'POST'])
def handleRequest():
    if request.method == 'GET':
        return get_users()
    elif request.method == 'POST':
        return create_user()

def get_users():
    try:
        conn = mysql.connector.connect(
            host=USERS_DB_HOST,
            user='root',
            password='root',
            database='users_db'
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(users=users)
    except mysql.connector.Error as err:
        return jsonify(error=str(err)), 500
    

def create_user():
    try:
        data = request.json
        name = data.get('name')
        role_name = data.get('role_name')
        doc_id = data.get('doc_id')

        if not name or not role_name or not doc_id:
            return jsonify(error="Name, role name and doc id are required"), 400

        conn = mysql.connector.connect(
            host=USERS_DB_HOST,
            user='root',
            password='root',
            database='users_db'
        )
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, role_name, doc_id) VALUES (%s, %s, %s)", (name, role_name, doc_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify(message="User created successfully"), 201
    except mysql.connector.Error as err:
        return jsonify(error=str(err)), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=USERS_BACKEND_PORT)
