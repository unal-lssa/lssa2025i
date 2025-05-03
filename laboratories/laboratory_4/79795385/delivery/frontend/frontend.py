from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/get-instance-name", methods=["GET"])
def get_instance_name():
    try:
        response = requests.get("http://load_balancer:8000/getInstanceName")
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/get-data", methods=["GET"])
def get_data():
    try:
        refresh = request.args.get("refresh", "false")  # Default to 'false'
        response = requests.get("http://load_balancer:8000/data", params={"refresh": refresh})
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/submit-task", methods=["POST"])
def submit_task():
    try:
        payload = request.json
        response = requests.post("http://load_balancer:8000/longtask", json=payload)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
