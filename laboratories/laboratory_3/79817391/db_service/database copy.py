from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/db')
def db_access():
    return jsonify({'message': 'Database access granted'}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5002)
    
    from flask import Flask, request, jsonify
from auth_utils import token_required
import os
import ipaddress

app = Flask(__name__)

@app.before_request
def validate_ip():
    client_ip = ipaddress.ip_address(request.remote_addr)
    allowed_ips = [ipaddress.ip_network(ip) for ip in os.getenv('ALLOWED_IPS').split(',')]
    
    if not any(client_ip in net for net in allowed_ips):
        return jsonify({"error": "IP not allowed"}), 403

@app.route('/db')
@token_required
def db_access():
    return jsonify({"message": "Database access granted"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('SERVICE_PORT', 5002))