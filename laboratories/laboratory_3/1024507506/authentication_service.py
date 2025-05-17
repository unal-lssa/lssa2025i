from flask import Flask, request, jsonify
import jwt
import datetime

app = Flask(__name__)
SECRET_KEY = "your_secret_key"

# Mock de usuarios
USERS = {
    "admin": {"password": "adminpass", "role": "admin"},
    "user1": {"password": "password123", "role": "user"}
}

@app.route('/auth', methods=['POST'])
def authenticate():
    auth = request.get_json()
    username = auth.get('username')
    password = auth.get('password')

    user = USERS.get(username)
    if user and user['password'] == password:
        payload = {
            'username': username,
            'role': user['role'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return jsonify({'token': token})

    return jsonify({'message': 'Invalid credentials'}), 401

if __name__ == "__main__":
    app.run(port=5003, debug=True)