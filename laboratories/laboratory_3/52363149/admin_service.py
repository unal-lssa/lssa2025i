from flask import Flask, request, jsonify
import jwt
from functools import wraps

app = Flask(__name__)
SECRET_KEY = "secret"  # Debe coincidir con el servicio principal


# Middleware para validar token
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"message": "Token is missing!"}), 403
        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user_role = decoded.get("role")
            request.username = decoded.get("username")
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"message": "Token is invalid!"}), 403
        return f(*args, **kwargs)

    return decorated_function


# Middleware para validar rol admin
def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.user_role != required_role:
                return jsonify({"message": "Unauthorized: Admins only"}), 403
            return f(*args, **kwargs)

        return decorated_function

    return decorator


@app.route("/admin-tools", methods=["GET"])
@token_required
@role_required("admin")
def admin_tools():
    return (
        jsonify(
            {
                "message": f"Welcome admin {request.username}. You can access admin tools here."
            }
        ),
        200,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5003)
