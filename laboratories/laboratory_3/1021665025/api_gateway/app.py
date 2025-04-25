from flask import Flask, request, jsonify, g # Import g for storing user data
import jwt
from functools import wraps
import os
import requests # To make requests to other services
import time
from collections import defaultdict # For basic rate limiting

app = Flask(__name__)

# Configuration
AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL', 'http://auth_service:5001')
FINANCES_SERVICE_URL = os.environ.get('FINANCES_SERVICE_URL', 'http://finances_service:5002')
LEGAL_SERVICE_URL = os.environ.get('LEGAL_SERVICE_URL', 'http://legal_service:5003')
UNITS_SERVICE_URL = os.environ.get('UNITS_SERVICE_URL', 'http://units_service:5004')

SECRET_KEY = os.environ.get('SECRET_KEY', 'b36e068c3e28c07a152766ebddfbb6a882a767d29edce9068c79c90038f2b516d2401fa96110a316843f00bc1cf3cac2be0f590514d8043dfe5919531a1754f2cde9714a68468674a887bed68ca7c2595b4d1c30a37134e056d0628d2eb417ae3e4af702bd9b1d8db675d62e744bc74f7a847094384f62e8f629dfb06d36f815b1d699389e0064cb41f45c85551e9c268d8437c7b6cdd6a750f13899173b85e8ca25fc242be57d0fea69f06819ae99be9483fedda47ea8a7831f920f0d98ec1a1a7f3057ec639683a4330fff85248a3704c6f176f92873774fc81dd14ea4808cec94714c392197000b84351a2198972efc492e92b898c68cbc48b747ec584ecf')

# Limit Exposure: Authorized IP (still using this for local testing as per original lab)
AUTHORIZED_IP = os.environ.get('AUTHORIZED_IP', '172.20.0.1') # I am using thunder client to test I had to change this ip for testing purposes

# Rate Limiting Configuration
RATE_LIMIT_PER_MINUTE = int(os.environ.get('RATE_LIMIT_PER_MINUTE', 5)) # I will use 5 requests per minute for testing 
RATE_LIMIT_WINDOW_SECONDS = 60 # Window size in seconds (1 minute)
request_counts = defaultdict(lambda: []) 

# --- Security Decorators ---

# Limit Exposure: IP Restriction
def limit_exposure(f):
    """Decorator to limit access to authorized IP addresses."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        if client_ip != AUTHORIZED_IP:
            return jsonify({'message': 'Forbidden: Unauthorized IP'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Denial of Service Detection: Rate Limiting
def rate_limited(f):
    """Decorator to limit the rate of requests from a single IP address."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        current_time = time.time()

        # Clean up old timestamps outside the window
        request_counts[client_ip] = [
            timestamp for timestamp in request_counts[client_ip]
            if timestamp > current_time - RATE_LIMIT_WINDOW_SECONDS
        ]

        # Check if the number of requests exceeds the limit
        if len(request_counts[client_ip]) >= RATE_LIMIT_PER_MINUTE:
            return jsonify({'message': 'Too Many Requests'}), 429

        # Record the current request timestamp
        request_counts[client_ip].append(current_time)

        return f(*args, **kwargs)
    return decorated_function

# Authorized Actors & RBAC: Token Validation and Role Fetching
def token_required(f):
    """Decorator to validate JWT token and fetch user roles from Auth Service."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        # Remove "Bearer " prefix if present
        if token.startswith('Bearer '):
            token = token[7:]

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get('user_id')
            username = payload.get('username')

            # We could trust the roles in the token payload, but calling the auth service
            # is more secure as roles might change after token issuance.

            if not user_id:
                 return jsonify({'message': 'Token is invalid or missing user_id'}), 401


            # --- Call Auth Service to get the latest roles ---
            try:
                auth_response = requests.get(f'{AUTH_SERVICE_URL}/auth/user/{user_id}/roles')
                if auth_response.status_code == 200:
                    user_data = auth_response.json()
                    user_roles = user_data.get('roles', [])
                    # Store user info and roles in Flask's global context (g)
                    g.user = {'user_id': user_id, 'username': username, 'roles': user_roles}
                else:
                    # Handle cases where user is not found in auth service or other errors
                     return jsonify({'message': 'Could not retrieve user roles from auth service'}), auth_response.status_code
            except requests.exceptions.RequestException as e:
                 # Handle network errors or auth service being down
                 return jsonify({'message': f'Error communicating with authentication service: {e}'}), 500
            # --- End Call Auth Service ---


        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401 # Use 401 for expired token
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid'}), 401 # Use 401 for invalid token
        except Exception as e:
            return jsonify({'message': f'An unexpected error occurred during token validation: {e}'}), 500

        return f(*args, **kwargs)
    return decorated_function

# Authorized Actors & RBAC: Role Checking
def requires_role(required_roles):
    """Decorator to check if the authenticated user has one of the required roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # This decorator must be applied *after* @token_required,
            # so g.user and g.user['roles'] are available.
            user = g.user # Get user data from the token_required decorator

            if not user:
                 return jsonify({'message': 'Authentication required'}), 401

            user_roles = set(user.get('roles', []))
            # Check if the user has *any* of the required roles
            if not user_roles.intersection(set(required_roles)):
                return jsonify({'message': 'Forbidden: Insufficient permissions'}), 403

            # If user has at least one required role, proceed
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- API Gateway Routes ---

# Route for user login - Forward to Auth Service
@app.route('/login', methods=['POST'])
@rate_limited # Apply rate limiting to the login route
@limit_exposure 
def login():
    # Forward the login request (username and password) to the Auth Service
    try:
        auth_response = requests.post(f'{AUTH_SERVICE_URL}/auth/login', json=request.get_json())
        # Return the response from the Auth Service (should contain the JWT token)
        return jsonify(auth_response.json()), auth_response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'message': f'Error communicating with authentication service: {e}'}), 500


# Example Protected Route (this is from original lab, now with RBAC and Rate Limiting)
# Only users with 'admin' or 'super_admin' roles can access this example data
@app.route('/data', methods=['GET'])
@rate_limited # Apply rate limiting to this route
@token_required 
@requires_role(['admin', 'super_admin']) # Check if user has admin or super_admin role
@limit_exposure 
def get_data():
    return jsonify({'message': 'Confidential Data accessed successfully!'}), 200


# --- Routes to forward requests to specific microservices ---

#Route to access Finances Service (requires 'finance' or 'finance_assistance' role)
@app.route('/finances/transactions', methods=['GET'])
@rate_limited
@token_required
@requires_role(['finance', 'finance_assistance', 'admin', 'super_admin']) # Define which roles can access finances
@limit_exposure
def get_finances_transactions():
    try:
        # Forward the request to the Finances Service
        headers = {'Authorization': request.headers.get('Authorization')}
        service_response = requests.get(f'{FINANCES_SERVICE_URL}/finances/transactions', headers=headers, params=request.args)
        return jsonify(service_response.json()), service_response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'message': f'Error communicating with finances service: {e}'}), 500

# Route to access Legal Service (requires 'legal' or 'legal_assitance' role)
@app.route('/legal/documents', methods=['GET'])
@rate_limited
@token_required
@requires_role(['legal', 'legal_assitance', 'admin', 'super_admin']) # Define which roles can access legal
@limit_exposure 
def get_legal_documents():
    try:
        headers = {'Authorization': request.headers.get('Authorization')}
        service_response = requests.get(f'{LEGAL_SERVICE_URL}/legal/documents', headers=headers, params=request.args)
        return jsonify(service_response.json()), service_response.status_code
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error forwarding request to legal service: {e}", exc_info=True)
        return jsonify({'message': f'Error communicating with legal service: {e}'}), 500

# Route to access Units Service (publicly accessible, but rate-limited)
@app.route('/units/available', methods=['GET'])
@rate_limited # Still apply rate limiting for public endpoints
# No @token_required, @requires_role and @limit_exposure here as it's a public endpoint
def get_available_units():
    try:
        # Forward the request to the Units Service. No auth header needed for public endpoint.
        service_response = requests.get(f'{UNITS_SERVICE_URL}/units/available', params=request.args)
        return jsonify(service_response.json()), service_response.status_code
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error forwarding request to units service: {e}", exc_info=True)
        return jsonify({'message': f'Error communicating with units service: {e}'}), 500

if __name__ == "__main__":
    # Use host='0.0.0.0' to make it accessible from outside the container
    app.run(host='0.0.0.0', port=5000, debug=True)