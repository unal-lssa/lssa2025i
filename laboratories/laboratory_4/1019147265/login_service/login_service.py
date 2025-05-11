from flask import Flask, jsonify
import jwt

app = Flask(__name__)
SECRET_KEY = "secret"

@app.route("/login", methods=["GET"])
def login():
    token = jwt.encode({"user": "test"}, SECRET_KEY, algorithm="HS256")
    return jsonify({"token": token})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006, debug=True)