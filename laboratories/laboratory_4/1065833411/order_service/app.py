from flask import Flask, jsonify
import json

app = Flask(__name__)

@app.route('/')
def get_orders():
    with open("order_db.json") as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)