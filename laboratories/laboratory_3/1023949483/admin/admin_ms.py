from flask import Flask, jsonify, request
import jwt
from mock_data import USERS, CLIENTS

app = Flask(__name__)
SECRET_KEY = "your_secret_key"

@app.route('/admin/users', methods=['GET'])
def get_users_summary():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"message": "Missing token"}), 403

    try:
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        if payload.get("role") != "admin":
            return jsonify({"message": "Admin access required"}), 403

        summary = []
        for username, user_info in USERS.items():
            client_count = sum(1 for client in CLIENTS if client["owner"] == username)
            summary.append({
                "username": username,
                "role": user_info["role"],
                "clients_owned": client_count
            })

        return jsonify(summary), 200

    except Exception as e:
        return jsonify({"message": f"Invalid token: {str(e)}"}), 403

if __name__ == "__main__":
    app.run(debug=True, port=5004)