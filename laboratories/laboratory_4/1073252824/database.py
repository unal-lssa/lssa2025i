from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/db", methods=["GET"])
def db_data():
    return jsonify({'message': 'Fetched fresh data from DB'})

if __name__ == "__main__":
    app.run(port=5002, debug=True)
