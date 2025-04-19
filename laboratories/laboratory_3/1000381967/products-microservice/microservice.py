from flask import Flask, jsonify, request
import socket
from functools import wraps
import requests

try:
    AUTHORIZED_IP = socket.gethostbyname('api-gateway')
except socket.gaierror:
    AUTHORIZED_IP = None
    print("Error: Unable to resolve 'api-gateway' to an IP address")

app = Flask(__name__)

def limit_exposure(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        if client_ip != AUTHORIZED_IP:  
            return jsonify({'message': 'Forbidden: Unauthorized IP'}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/products', methods=['GET'])
@limit_exposure
def product_db():
    try:
        response = requests.get(
            'http://products-database:5004/products'
        )
        
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify(response.json()), 404
    except requests.exceptions.RequestException as e:
        return jsonify({'message': 'Error at microservice', 'Details: ': str(e)}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)

