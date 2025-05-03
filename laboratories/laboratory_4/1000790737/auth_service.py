from flask import Flask, request, jsonify
import jwt, datetime

app = Flask(__name__)
SECRET_KEY = "secret"


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username == "admin" and password == "password":
        token = jwt.encode(
            {
                "sub": username,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            },
            SECRET_KEY,
            algorithm="HS256",
        )
        return jsonify({"token": token})
    return jsonify({"error": "Invalid credentials"}), 401


if __name__ == "__main__":
    import sys

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5011
    app.run(host="0.0.0.0", port=port, debug=True)
