from flask import Flask, jsonify, request
import jwt
from mock_data import CLIENTS

app = Flask(__name__)

SECRET_KEY = "your_secret_key"

@app.route('/clients', methods=['GET'])
def get_clients():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"message": "Missing token"}), 403

    try:
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload.get("username")
        role = payload.get("role", "user")

        if role == "admin":
            return jsonify(CLIENTS)
        else:
            user_clients = [c for c in CLIENTS if c["owner"] == username]
            return jsonify(user_clients)
    except Exception as e:
        return jsonify({"message": f"Invalid token: {str(e)}"}), 403

if __name__ == "__main__":
    app.run(debug=True, port=5003)