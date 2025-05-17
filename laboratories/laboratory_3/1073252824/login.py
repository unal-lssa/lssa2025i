from flask import Flask, request, jsonify
import jwt
import datetime

app = Flask(__name__)
SECRET_KEY = "your_secret_key"

# Usuarios simulados
USERS = {
    "user1": {"password": "password123", "role": "admin"},
    "user2": {"password": "password456", "role": "user"}
}

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = USERS.get(username)

    if user and user['password'] == password:
        # Establece el tiempo de expiración del token (por ejemplo, 1 hora)
        expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        token = jwt.encode({
            'username': username,
            'role': user['role'],
            'exp': expiration_time
        }, SECRET_KEY, algorithm="HS256")
        
        return jsonify({'token': token})
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

if __name__ == "__main__":
    app.run(port=5003, debug=True)
