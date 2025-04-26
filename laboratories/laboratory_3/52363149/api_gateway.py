from flask import Flask, request, jsonify
import jwt
from functools import wraps
from datetime import datetime, timedelta

app = Flask(__name__)
SECRET_KEY = "secret"
AUTHORIZED_IP = "127.0.0.1"  # Only allow local access for simplicity

# Mock users with roles
USERS = {
    "user2": {"password": "password123", "role": "user"},
    "admin1": {"password": "adminpass", "role": "admin"},
}


# Function to check if the request comes from an authorized IP address
def limit_exposure(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        if client_ip != AUTHORIZED_IP:
            return jsonify({"message": "Forbidden: Unauthorized IP"}), 403
        return f(*args, **kwargs)

    return decorated_function


# Function to check JWT token and role
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"message": "Token is missing!"}), 403
        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_role = decoded_token.get("role")
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Token is invalid!"}), 403

        # Store role in request context
        request.user_role = user_role

        return f(*args, **kwargs)

    return decorated_function


# Function to check role for specific routes
def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            app.logger.debug(
                f"User role: {request.user_role}"
            )  # Debugging: check user role
            app.logger.debug(
                f"Required role: {required_role}"
            )  # Debugging: check required role

            # Verificar que el rol del usuario sea el rol requerido
            if request.user_role != required_role:
                return (
                    jsonify(
                        {
                            "message": "You do not have permission to access this resource!"
                        }
                    ),
                    403,
                )
            return f(*args, **kwargs)

        return decorated_function

    return decorator


# Route for user login (returns JWT token)
@app.route("/login", methods=["POST"])
def login():
    auth = request.get_json()
    username = auth.get("username")
    password = auth.get("password")

    user = USERS.get(username)
    if user and user["password"] == password:
        expiration_time = datetime.utcnow() + timedelta(minutes=10)
        token = jwt.encode(
            {"username": username, "role": user["role"], "exp": expiration_time},
            SECRET_KEY,
            algorithm="HS256",
        )
        return jsonify({"token": token})
    return jsonify({"message": "Invalid credentials"}), 401


# Protected route that only 'user' role can access
@app.route("/data", methods=["GET"])
@token_required
@limit_exposure  # Apply the limit exposure tactic to this route
def get_data():
    return jsonify({"message": "Data accessed successfully!"}), 200


# Protected route that only 'admin' role can access
@app.route("/admin", methods=["GET"])
@token_required
@role_required("admin")
@limit_exposure
def admin_data():
    return jsonify({"message": "Admin data accessed!"}), 200


if __name__ == "__main__":
    app.run(debug=True)
