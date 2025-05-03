from flask import Flask, jsonify, request
import psycopg2
import json


app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        dbname="lssadb",
        user="lssauser",
        password="password",
        host="users-db",
        port="5432"
    )

@app.route('/user', methods=['POST'])
def check_user():
    data = json.loads(request.data)
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = "SELECT COUNT(*) FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()

        if result[0] > 0:
            return jsonify({"exists": True}), 200
        else:
            return jsonify({"exists": False}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
