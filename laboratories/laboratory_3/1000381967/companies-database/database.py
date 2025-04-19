from flask import Flask, jsonify, request
import socket
from functools import wraps

try: 
    AUTHORIZED_IP = socket.gethostbyname('companies-microservice')
except socket.gaierror:
    AUTHORIZED_IP = None
    print("Error: Unable to resolve 'companies-microservice' to an IP address")

COMPANIES = {
    "Sony": "Playstation 5",
    "Microsoft": "Xbox Series X",
    "Nintendo": "Nintendo Switch",
    "Dell": "Gaming PC",
}

app = Flask(__name__)

def limit_exposure(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        if client_ip != AUTHORIZED_IP:  
            return jsonify({'message': 'Forbidden: Unauthorized IP'}), 403
        return f(*args, **kwargs)
    return decorated_function


@app.route('/companies', methods=['GET'])
@limit_exposure
def product_db():
    try:
        if not COMPANIES:
            return jsonify({'message': 'No companies available'}), 404
        return jsonify(COMPANIES), 200 
    except Exception as e:
        return jsonify({'message': 'Error at companies-database', 'Details: ': str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5006)