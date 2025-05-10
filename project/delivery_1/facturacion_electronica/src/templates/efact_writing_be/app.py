from flask import Flask, jsonify
import os
import mysql.connector

# Configurar el entorno de Flask
app = Flask(__name__)

# Escritura de facturas microservice port
EFACT_WRITING_BACKEND_PORT = os.getenv("EFACT_WRITING_BACKEND_PORT", 5009)

# Default route
@app.route('/')
def home():
    return jsonify(message="Hello from the Efact Writing Mircroservice!")

# AJUSTAR
# @app.route('/create', methods=['POST'])
# def create():
#     data = request.json
#     conn = mysql.connector.connect(
#         host='{database}',
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
    app.run(host='0.0.0.0', port=EFACT_WRITING_BACKEND_PORT)
