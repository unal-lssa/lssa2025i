from flask import Flask, jsonify, request
import requests
from functools import wraps

app = Flask(__name__)


@app.route("/microservice")
def microservice():
    response = requests.get("http://database:5002/db")
    if response.status_code != 200:
        return (
            jsonify({"message": "Internal Service Error. Contact the administrator."}),
            500,
        )
    return jsonify(
        {
            "message": "After fetching the db from the microservice.",
            "database response": str(response.content),
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
