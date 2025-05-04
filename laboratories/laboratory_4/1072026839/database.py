from flask import Flask, jsonify
import time

app = Flask(__name__)

@app.route("/db", methods=["GET"])
def db_data():
    # Simular retraso de DB
    time.sleep(0.5)
    timestamp = time.strftime("%H:%M:%S")
    return jsonify({
        'message': f'Fetched fresh data from DB at {timestamp}'
    })

if __name__ == "__main__":
    app.run(port=5002, debug=True)