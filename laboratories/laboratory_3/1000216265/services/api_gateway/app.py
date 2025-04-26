from flask import Flask, request, jsonify
import jwt
import requests
import time
import re
import os
from functools import wraps
from datetime import datetime, timedelta

app = Flask(__name__)
SECRET_KEY = os.environ.get('SECRET_KEY', "your_secret_key")

# Service URLs from environment variables or default to localhost in development
AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL', 'http://localhost:5001')
USER_SERVICE_URL = os.environ.get('USER_SERVICE_URL', 'http://localhost:5002')
PRODUCT_SERVICE_URL = os.environ.get('PRODUCT_SERVICE_URL', 'http://localhost:5003')
LOGGING_SERVICE_URL = os.environ.get('LOGGING_SERVICE_URL', 'http://localhost:5004')

# More complex IP rules - support for IP ranges
AUTHORIZED_IPS = os.environ.get('AUTHORIZED_IPS', '127.0.0.1,192.168.0.0/24').split(',')
# Internal service API keys
SERVICE_API_KEYS = {
    'auth_service': os.environ.get('AUTH_SERVICE_KEY', 'auth_secret_key'),
    'user_service': os.environ.get('USER_SERVICE_KEY', 'user_secret_key'),
    'product_service': os.environ.get('PRODUCT_SERVICE_KEY', 'product_secret_key'),
    'logging_service': os.environ.get('LOGGING_SERVICE_KEY', 'logging_secret_key'),
}

# Rate limiting configuration
RATE_LIMIT = {
    'DEFAULT': {'limit': 10, 'window': 60},  # 10 requests per minute
    'ADMIN': {'limit': 100, 'window': 60},   # 100 requests per minute
}

# Store for rate limiting
rate_limit_store = {}

# Circuit breaker configuration
CIRCUIT_BREAKER = {
    'fail_threshold': 5,
    'reset_timeout': 30,
    'services': {}
}

def is_ip_authorized(ip):
    """Check if an IP is in the authorized list, including CIDR notation."""
    for allowed in AUTHORIZED_IPS:
        if '/' in allowed:  # CIDR notation
            network = allowed.strip()
            # Basic CIDR check (simplified)
            net_ip, bits = network.split('/')
            net_ip_int = int(''.join([bin(int(x)+256)[3:] for x in net_ip.split('.')]), 2)
            ip_int = int(''.join([bin(int(x)+256)[3:] for x in ip.split('.')]), 2)
            mask = (0xffffffff << (32 - int(bits))) & 0xffffffff
            if net_ip_int & mask == ip_int & mask:
                return True
        elif ip == allowed.strip():
            return True
    return False

def limit_exposure(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check IP authorization
        client_ip = request.remote_addr
        if not is_ip_authorized(client_ip):
            log_security_event('IP_BLOCKED', client_ip)
            return jsonify({'message': 'Forbidden: Unauthorized IP'}), 403
        
        # Apply rate limiting
        token_data = get_token_data()
        role = token_data.get('role', 'DEFAULT') if token_data else 'DEFAULT'
        
        rate_config = RATE_LIMIT.get(role, RATE_LIMIT['DEFAULT'])
        
        current_time = time.time()
        user_id = token_data.get('sub', client_ip) if token_data else client_ip
        
        # Initialize or clean up old requests
        if user_id not in rate_limit_store:
            rate_limit_store[user_id] = []
        else:
            # Remove requests outside the current window
            rate_limit_store[user_id] = [t for t in rate_limit_store[user_id] 
                                       if current_time - t < rate_config['window']]
        
        # Check if the rate limit is exceeded
        if len(rate_limit_store[user_id]) >= rate_config['limit']:
            log_security_event('RATE_LIMIT_EXCEEDED', user_id)
            return jsonify({'message': 'Rate limit exceeded'}), 429
        
        # Add this request to the store
        rate_limit_store[user_id].append(current_time)
        
        return f(*args, **kwargs)
    return decorated_function

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            # Decode and validate the token
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            
            # Check if token is expired
            if 'exp' in data and datetime.fromtimestamp(data['exp']) < datetime.now():
                return jsonify({'message': 'Token has expired!'}), 401
                
            # Store token data for the route handler
            request.token_data = data
        except Exception as e:
            print(f"Token validation error: {e}")
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # This decorator expects token_required to run first
            if not hasattr(request, 'token_data'):
                return jsonify({'message': 'Authorization required'}), 401
            
            user_role = request.token_data.get('role')
            if user_role not in roles:
                log_security_event('UNAUTHORIZED_ROLE_ACCESS', 
                                  f"User {request.token_data.get('sub')} with role {user_role} tried to access {request.path}")
                return jsonify({'message': 'Permission denied'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_request(schema):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.is_json:
                data = request.get_json()
                errors = []
                
                # Validate required fields
                for field, field_schema in schema.items():
                    if field_schema.get('required', False) and field not in data:
                        errors.append(f"Field '{field}' is required")
                    elif field in data:
                        # Validate field type
                        if field_schema.get('type') == 'string' and not isinstance(data[field], str):
                            errors.append(f"Field '{field}' must be a string")
                        elif field_schema.get('type') == 'number' and not isinstance(data[field], (int, float)):
                            errors.append(f"Field '{field}' must be a number")
                        
                        # Validate pattern
                        if field_schema.get('pattern') and isinstance(data[field], str):
                            pattern = re.compile(field_schema['pattern'])
                            if not pattern.match(data[field]):
                                errors.append(f"Field '{field}' has invalid format")
                
                if errors:
                    return jsonify({'message': 'Validation error', 'errors': errors}), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def circuit_breaker(service_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Initialize service in circuit breaker if not exists
            if service_name not in CIRCUIT_BREAKER['services']:
                CIRCUIT_BREAKER['services'][service_name] = {
                    'fails': 0,
                    'status': 'CLOSED',
                    'last_failure': 0
                }
            
            circuit = CIRCUIT_BREAKER['services'][service_name]
            
            # If circuit is open, check if reset timeout has passed
            if circuit['status'] == 'OPEN':
                if time.time() - circuit['last_failure'] > CIRCUIT_BREAKER['reset_timeout']:
                    circuit['status'] = 'HALF_OPEN'
                else:
                    return jsonify({'message': f'Service {service_name} is unavailable'}), 503
            
            try:
                result = f(*args, **kwargs)
                
                # If successful and half-open, close the circuit
                if circuit['status'] == 'HALF_OPEN':
                    circuit['status'] = 'CLOSED'
                    circuit['fails'] = 0
                
                return result
            except Exception as e:
                # Record the failure
                circuit['fails'] += 1
                circuit['last_failure'] = time.time()
                
                # If failed too many times, open the circuit
                if circuit['fails'] >= CIRCUIT_BREAKER['fail_threshold']:
                    circuit['status'] = 'OPEN'
                    log_security_event('CIRCUIT_BREAKER_OPEN', f"Service {service_name} circuit opened")
                
                return jsonify({'message': f'Service error: {str(e)}'}), 500
        return decorated_function
    return decorator

def log_security_event(event_type, details):
    """Send security events to logging service"""
    try:
        headers = {'X-API-Key': SERVICE_API_KEYS['logging_service']}
        requests.post(
            f"{LOGGING_SERVICE_URL}/log",
            json={
                'event_type': event_type,
                'details': details,
                'timestamp': datetime.now().isoformat()
            },
            headers=headers
        )
    except Exception as e:
        print(f"Error logging security event: {e}")

def get_token_data():
    token = request.headers.get('Authorization')
    if not token:
        return None
    
    try:
        if token.startswith('Bearer '):
            token = token[7:]
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except:
        return None

# Authentication route - proxies to auth service
@app.route('/auth/login', methods=['POST'])
@limit_exposure
@validate_request({
    'username': {'required': True, 'type': 'string'},
    'password': {'required': True, 'type': 'string'}
})
@circuit_breaker('auth_service')
def login():
    # Forward the request to the auth service
    response = requests.post(
        f"{AUTH_SERVICE_URL}/login",
        json=request.get_json(),
        headers={'X-API-Key': SERVICE_API_KEYS['auth_service']}
    )
    return response.json(), response.status_code

# User service endpoints
@app.route('/users', methods=['GET'])
@limit_exposure
@token_required
@role_required(['ADMIN', 'USER'])
@circuit_breaker('user_service')
def get_users():
    response = requests.get(
        f"{USER_SERVICE_URL}/users",
        headers={
            'X-API-Key': SERVICE_API_KEYS['user_service'],
            'Authorization': request.headers.get('Authorization')
        }
    )
    return response.json(), response.status_code

@app.route('/users/<user_id>', methods=['GET'])
@limit_exposure
@token_required
@role_required(['ADMIN', 'USER'])
@circuit_breaker('user_service')
def get_user(user_id):
    # Validate user_id format to prevent injection
    if not re.match(r'^[a-zA-Z0-9_-]+$', user_id):
        return jsonify({'message': 'Invalid user ID format'}), 400
        
    response = requests.get(
        f"{USER_SERVICE_URL}/users/{user_id}",
        headers={
            'X-API-Key': SERVICE_API_KEYS['user_service'],
            'Authorization': request.headers.get('Authorization')
        }
    )
    return response.json(), response.status_code

@app.route('/users', methods=['POST'])
@limit_exposure
@token_required
@role_required(['ADMIN'])
@validate_request({
    'username': {'required': True, 'type': 'string', 'pattern': r'^[a-zA-Z0-9_]{3,50}$'},
    'email': {'required': True, 'type': 'string', 'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'},
    'role': {'required': True, 'type': 'string', 'pattern': r'^(ADMIN|USER)$'}
})
@circuit_breaker('user_service')
def create_user():
    response = requests.post(
        f"{USER_SERVICE_URL}/users",
        json=request.get_json(),
        headers={
            'X-API-Key': SERVICE_API_KEYS['user_service'],
            'Authorization': request.headers.get('Authorization')
        }
    )
    return response.json(), response.status_code

# Product service endpoints
@app.route('/products', methods=['GET'])
@limit_exposure
@token_required
@role_required(['ADMIN', 'USER'])
@circuit_breaker('product_service')
def get_products():
    response = requests.get(
        f"{PRODUCT_SERVICE_URL}/products",
        headers={
            'X-API-Key': SERVICE_API_KEYS['product_service'],
            'Authorization': request.headers.get('Authorization')
        }
    )
    return response.json(), response.status_code

@app.route('/products/<product_id>', methods=['GET'])
@limit_exposure
@token_required
@role_required(['ADMIN', 'USER'])
@circuit_breaker('product_service')
def get_product(product_id):
    # Validate product_id format to prevent injection
    if not re.match(r'^[a-zA-Z0-9_-]+$', product_id):
        return jsonify({'message': 'Invalid product ID format'}), 400
        
    response = requests.get(
        f"{PRODUCT_SERVICE_URL}/products/{product_id}",
        headers={
            'X-API-Key': SERVICE_API_KEYS['product_service'],
            'Authorization': request.headers.get('Authorization')
        }
    )
    return response.json(), response.status_code

@app.route('/products', methods=['POST'])
@limit_exposure
@token_required
@role_required(['ADMIN'])
@validate_request({
    'name': {'required': True, 'type': 'string'},
    'price': {'required': True, 'type': 'number'},
    'description': {'required': False, 'type': 'string'}
})
@circuit_breaker('product_service')
def create_product():
    response = requests.post(
        f"{PRODUCT_SERVICE_URL}/products",
        json=request.get_json(),
        headers={
            'X-API-Key': SERVICE_API_KEYS['product_service'],
            'Authorization': request.headers.get('Authorization')
        }
    )
    return response.json(), response.status_code

# Logging service endpoints
@app.route('/logs', methods=['GET'])
@limit_exposure
@token_required
@role_required(['ADMIN'])  # Only admins should access logs
@circuit_breaker('logging_service')
def get_logs():
    # Get all query parameters to forward them
    params = {}
    for key in ['event_type', 'start_time', 'end_time', 'client_ip']:
        if key in request.args:
            params[key] = request.args.get(key)
    
    # Forward the request to the logging service with query parameters
    response = requests.get(
        f"{LOGGING_SERVICE_URL}/logs",
        params=params,
        headers={
            'X-API-Key': SERVICE_API_KEYS['logging_service']
        }
    )
    return response.json(), response.status_code

@app.route('/logs/<log_id>', methods=['GET'])
@limit_exposure
@token_required
@role_required(['ADMIN'])
@circuit_breaker('logging_service')
def get_log_by_id(log_id):
    # Validate log_id format to prevent injection
    if not re.match(r'^[a-zA-Z0-9_-]+$', log_id):
        return jsonify({'message': 'Invalid log ID format'}), 400
        
    response = requests.get(
        f"{LOGGING_SERVICE_URL}/logs/{log_id}",
        headers={
            'X-API-Key': SERVICE_API_KEYS['logging_service']
        }
    )
    return response.json(), response.status_code

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
