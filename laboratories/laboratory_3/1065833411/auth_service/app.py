from flask import Flask, request, jsonify
import jwt

app = Flask(__name__)
SECRET_KEY = "your_secret_key"
USERS = {
    "admin": {"password": "adminpass", "role": "admin"},
    "user1": {"password": "userpass", "role": "user"}
}

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = USERS.get(data.get("username"))
    if user and user["password"] == data.get("password"):
        token = jwt.encode({"username": data["username"], "role": user["role"]}, SECRET_KEY, algorithm="HS256")
        return jsonify({"token": token})
    return jsonify({"message": "Invalid credentials"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)