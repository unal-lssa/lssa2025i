from flask import Flask, request, jsonify
import jwt
import time
import logging
from functools import wraps
from datetime import datetime, timedelta

app = Flask(__name__)
SECRET_KEY = "your_secret_key"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='api_gateway.log'
)
logger = logging.getLogger(__name__)

# IP whitelist with more granular access controls
IP_WHITELIST = {
    "127.0.0.1": ["admin", "user"],  # Local access for all roles
    "192.168.1.100": ["user"],       # Only user role from this IP
    "10.0.0.5": ["admin"]            # Only admin role from this IP
}

# Mock users with roles for demonstration
USERS = {
    "user1": {"password": "password123", "role": "user"},
    "admin1": {"password": "admin123", "role": "admin"},
    "analyst1": {"password": "analyst123", "role": "analyst"}
}

# Service registry - mapping services to their endpoints
SERVICE_REGISTRY = {
    "user_service": "http://localhost:5003/user",
    "order_service": "http://localhost:5004/order",
    "product_service": "http://localhost:5005/product",
    "database": "http://localhost:5002/db"
}

# Role-based access control - which roles can access which services
RBAC = {
    "user": ["user_service", "order_service", "product_service"],
    "admin": ["user_service", "order_service", "product_service", "database"],
    "analyst": ["analytics_service", "product_service"]
}

# Rate limiting configuration
RATE_LIMITS = {
    "user": 100,      # 100 requests per hour for regular users
    "analyst": 200,   # 200 requests per hour for analysts
    "admin": 500      # 500 requests per hour for admins
}

# Store for rate limiting
rate_limit_store = {}

# Function to check if the request comes from an authorized IP address
def limit_exposure_by_ip(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        
        # Check if IP is in whitelist
        if client_ip not in IP_WHITELIST:
            logger.warning(f"Access attempt from unauthorized IP: {client_ip}")
            return jsonify({'message': 'Forbidden: Unauthorized IP'}), 403
        
        # If we reach here, IP is in whitelist
        return f(*args, **kwargs)
    return decorated_function

# Function to check JWT token and extract user role
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')

        if auth_header:
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        if not token:
            logger.warning("Token missing in request")
            return jsonify({'message': 'Token is missing!'}), 403
        
        try:
            # Decode token to get payload
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user = {
                'username': payload['username'],
                'role': payload['role']
            }
        except jwt.ExpiredSignatureError:
            logger.warning(f"Expired token used by {payload.get('username', 'unknown')}")
            return jsonify({'message': 'Token has expired!'}), 401
        except Exception as e:
            logger.warning(f"Invalid token: {str(e)}")
            return jsonify({'message': 'Token is invalid!'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

# Function to check role-based permissions for services
def check_service_permission(service_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_role = request.user['role']
            username = request.user['username']
            
            # Check if user role can access this service
            if service_name not in RBAC.get(user_role, []):
                logger.warning(f"User {username} with role {user_role} attempted to access unauthorized service: {service_name}")
                return jsonify({'message': f'Access denied to {service_name} for role {user_role}'}), 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Rate limiting implementation
def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = request.user['username']
        role = request.user['role']
        current_time = int(time.time())
        hour_window = current_time - (current_time % 3600)  # Current hour window
        
        # Initialize if needed
        if username not in rate_limit_store:
            rate_limit_store[username] = {hour_window: 0}
        elif hour_window not in rate_limit_store[username]:
            rate_limit_store[username][hour_window] = 0
            
        # Check if rate limit exceeded
        if rate_limit_store[username][hour_window] >= RATE_LIMITS.get(role, 100):
            logger.warning(f"Rate limit exceeded for user {username}")
            return jsonify({'message': 'Rate limit exceeded. Please try again later.'}), 429
            
        # Increment request count
        rate_limit_store[username][hour_window] += 1
        
        return f(*args, **kwargs)
    return decorated_function

# Route for user login (returns JWT token)
@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()
    username = auth.get('username')
    password = auth.get('password')

    user_data = USERS.get(username)

    if not user_data or user_data['password'] != password:
        logger.warning(f"Invalid login attempt for user: {username}")
        return jsonify({'message': 'Invalid credentials'}), 401
        
    # Check if IP is allowed for this user's role
    client_ip = request.remote_addr
    if client_ip in IP_WHITELIST and user_data['role'] in IP_WHITELIST[client_ip]:
        # Create token with expiration time (1 hour)
        token = jwt.encode({
            'username': username,
            'role': user_data['role'],
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, SECRET_KEY, algorithm="HS256")
        
        logger.info(f"Successful login for user: {username} from IP: {client_ip}")
        return jsonify({'token': token})
    else:
        logger.warning(f"IP restriction failed for user {username} with role {user_data['role']} from IP {client_ip}")
        return jsonify({'message': 'IP not authorized for this user role'}), 403

# User service route
@app.route('/user', methods=['GET'])
@limit_exposure_by_ip
@token_required
@check_service_permission('user_service')
@rate_limit
def user_service():
    import requests
    username = request.user['username']
    role = request.user['role']
    logger.info(f"User {username} accessed user service")
    
    # Forward the request to the actual user service
    try:
        user_service_url = SERVICE_REGISTRY.get(user_service)
        response = requests.get(user_service_url)

        if response.status_code == 200:
            return response.json(), 200
        else:
            return jsonify({
                'message': f'Error from user service: {response.status_code}',
                'service': 'user_service'
            }), response.status_code
    except Exception as e:
        logger.error(f"Error forwarding request to user service: {str(e)}")
        return jsonify({
            'message': 'Error communicating with user service',
            'error': str(e),
            'service': 'user_service'
        }), 500
    

# Order service route
@app.route('/order', methods=['GET', 'POST'])
@limit_exposure_by_ip
@token_required
@check_service_permission('order_service')
@rate_limit
def order_service():
    import requests
    username = request.user['username']
    logger.info(f"User {username} accessed order service with method {request.method}")
    
    # Forward the request to the actual order service
    try:
        order_service_url = SERVICE_REGISTRY.get(order_service)
        response = requests.get(order_service_url)
        
        if response.status_code == 200:
            return response.json(), 200
        else:
            return jsonify({
                'message': f'Error from order service: {response.status_code}',
                'service': 'order_service'
            }), response.status_code
    except Exception as e:
        logger.error(f"Error forwarding request to order service: {str(e)}")
        return jsonify({
            'message': 'Error communicating with order service',
            'error': str(e),
            'service': 'order_service'
        }), 500

# Product service route
@app.route('/product', methods=['GET'])
@limit_exposure_by_ip
@token_required
@check_service_permission('product_service')
@rate_limit
def product_service():
    import requests
    username = request.user['username']
    logger.info(f"User {username} accessed product service")
    
    # Forward the request to the actual product service
    try:
        product_service_url = SERVICE_REGISTRY.get(product_service)
        response = requests.get(product_service_url)
        
        if response.status_code == 200:
            return response.json(), 200
        else:
            return jsonify({
                'message': f'Error from product service: {response.status_code}',
                'service': 'product_service'
            }), response.status_code
    except Exception as e:
        logger.error(f"Error forwarding request to product service: {str(e)}")
        return jsonify({
            'message': 'Error communicating with product service',
            'error': str(e),
            'service': 'product_service'
        }), 500
    
if __name__ == "__main__":
    logger.info("API Gateway starting up...")
    app.run(debug=True, host='0.0.0.0', port=5000)