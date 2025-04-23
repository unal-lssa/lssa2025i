from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Rutas hacia microservicios simulados
SERVICES = {
    "users": "http://backend:5000",
    "reports": "http://reports:5001"
}

@app.route('/')
def root():
    return jsonify(message="API Gateway running")

@app.route('/users')
def users():
    response = requests.get(f"{SERVICES['users']}/")
    return response.json(), response.status_code

@app.route('/reports')
def reports():
    response = requests.get(f"{SERVICES['reports']}/")
    return response.json(), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
