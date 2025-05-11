from flask import Flask, request, jsonify, g # Import g for storing user data
import jwt
from functools import wraps
import os
import requests 
import redis 
import json
from celery import Celery

app = Flask(__name__)

# Configuration
AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL', 'http://auth_service:5001')
FINANCES_SERVICE_URL = os.environ.get('FINANCES_SERVICE_URL', 'http://finances_service:5002')
LEGAL_SERVICE_URL = os.environ.get('LEGAL_SERVICE_URL', 'http://legal_service:5003')
UNITS_SERVICE_URL = os.environ.get('UNITS_SERVICE_URL', 'http://units_service:5004')
CACHE_SERVICE_URL = os.environ.get('CACHE_SERVICE_URL', 'redis://localhost:6379/0')
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'amqp://guest:guest@localhost:5672//')
CELERY_BACKEND_URL = os.environ.get('CELERY_BACKEND_URL', 'redis://localhost:6379/1') 

SECRET_KEY = os.environ.get('SECRET_KEY', 'b36e068c3e28c07a152766ebddfbb6a882a767d29edce9068c79c90038f2b516d2401fa96110a316843f00bc1cf3cac2be0f590514d8043dfe5919531a1754f2cde9714a68468674a887bed68ca7c2595b4d1c30a37134e056d0628d2eb417ae3e4af702bd9b1d8db675d62e744bc74f7a847094384f62e8f629dfb06d36f815b1d699389e0064cb41f45c85551e9c268d8437c7b6cdd6a750f13899173b85e8ca25fc242be57d0fea69f06819ae99be9483fedda47ea8a7831f920f0d98ec1a1a7f3057ec639683a4330fff85248a3704c6f176f92873774fc81dd14ea4808cec94714c392197000b84351a2198972efc492e92b898c68cbc48b747ec584ecf')

# Initialize Redis Client
try:
    redis_client = redis.from_url(CACHE_SERVICE_URL)
    # Ping Redis to check connection on startup
    redis_client.ping()
    print("Connected to Redis successfully!")
except redis.exceptions.ConnectionError as e:
    print(f"Could NOT connect to Redis: {e}") 
    redis_client = None 

# Cache TTL (Time To Live) in seconds
CACHE_TTL_SECONDS = int(os.environ.get('CACHE_TTL_SECONDS', 300)) # Default 5 minutes

# Configure celery
celery_app = Celery(
    'celery_app',
    broker=CELERY_BROKER_URL,
    backend=CELERY_BACKEND_URL
)

celery_app.conf.update(
    task_queues = {
        'high_priority': {'exchange': 'high_priority', 'routing_key': 'high_priority'},
        'low_priority': {'exchange': 'low_priority', 'routing_key': 'low_priority'},
        'celery': {'exchange': 'celery', 'routing_key': 'celery'}, # Default queue
    },
    task_default_queue = 'low_priority', # Default tasks go to low priority unless specified
    task_create_missing_queues = True, 
    # Priority ranges from 0 (highest) to 9 (lowest) in RabbitMQ
    task_queue_max_priority = 9,
    task_default_priority = 5 
)

# --- Security Decorators ---

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

# --- Define Celery Tasks ---
# We define them here in the API Gateway module so we can import and call them.
# The worker will also need to import and define them.

@celery_app.task
def generate_finances_report_task():
    """Celery task to generate a finances report."""
    # This function body will be EXECUTED by the Celery Worker, not the API Gateway
    print(f"Task received in API Gateway module (will be sent to worker): Generate Finances Report for user")


@celery_app.task
def generate_legal_report_task():
    """Celery task to generate a legal report."""
    # This function body will be EXECUTED by the Celery Worker
    print(f"Task received in API Gateway module (will be sent to worker): Generate Legal Report for user")

# --- API Gateway Routes ---

# Route for user login - Forward to Auth Service
@app.route('/login', methods=['POST'])
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
@token_required 
@requires_role(['admin', 'super_admin']) # Check if user has admin or super_admin role
def get_data():
    return jsonify({'message': 'Confidential Data accessed successfully!'}), 200


# --- Routes to forward requests to specific microservices ---

#Route to access Finances Service (requires 'finance' or 'finance_assistance' role)
@app.route('/finances/transactions', methods=['GET'])
@token_required
@requires_role(['finance', 'finance_assistance', 'admin', 'super_admin']) # Define which roles can access finances
def get_finances_transactions():
    try:
        # Forward the request to the Finances Service
        headers = {'Authorization': request.headers.get('Authorization')}
        service_response = requests.get(f'{FINANCES_SERVICE_URL}/finances/transactions', headers=headers, params=request.args)
        return jsonify(service_response.json()), service_response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'message': f'Error communicating with finances service: {e}'}), 500

@app.route('/finances/generate_report', methods=['POST'])
@token_required 
@requires_role(['finance', 'admin', 'super_admin']) 
def trigger_finances_report():

    print(f"API Gateway received request to trigger finances report")

    try:
        # Send the task to the Celery worker via RabbitMQ
        # Use .apply_async() to send the task asynchronously
        # Specify the queue ('high_priority') and priority (0 is highest)
        task = generate_finances_report_task.apply_async(
            queue='high_priority',
            priority=0
        )
        print(f"Finances report task {task.id} sent to high_priority queue with priority 0")
        return jsonify({'status': 'Finances report generation started', 'task_id': task.id}), 202 
    except Exception as e:
        app.logger.error(f"Error triggering finances report task: {e}", exc_info=True)
        return jsonify({'message': f'Failed to trigger finances report: {e}'}), 500

# Route to access Legal Service (requires 'legal' or 'legal_assitance' role)
@app.route('/legal/documents', methods=['GET'])
@token_required
@requires_role(['legal', 'legal_assitance', 'admin', 'super_admin']) # Define which roles can access legal
def get_legal_documents():
    try:
        headers = {'Authorization': request.headers.get('Authorization')}
        service_response = requests.get(f'{LEGAL_SERVICE_URL}/legal/documents', headers=headers, params=request.args)
        return jsonify(service_response.json()), service_response.status_code
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error forwarding request to legal service: {e}", exc_info=True)
        return jsonify({'message': f'Error communicating with legal service: {e}'}), 500

@app.route('/legal/generate_report', methods=['POST'])
@token_required
@requires_role(['legal', 'admin', 'super_admin'])
def trigger_legal_report():

    print(f"API Gateway received request to trigger legal report")

    try:
        # Send the task to the Celery worker via RabbitMQ
        # Use .apply_async()
        # Specify the queue ('low_priority') and priority (5 is default)
        task = generate_legal_report_task.apply_async(
            queue='low_priority',
            priority=5 # Lower priority than finances
        )
        print(f"Legal report task {task.id} sent to low_priority queue with priority 5")
        return jsonify({'status': 'Legal report generation started', 'task_id': task.id}), 202
    except Exception as e:
        app.logger.error(f"Error triggering legal report task: {e}", exc_info=True)
        return jsonify({'message': f'Failed to trigger legal report: {e}'}), 500
@app.route('/units/available', methods=['GET'])

# Note: No @token_required or @requires_role here as it's a public endpoint
def get_available_units():
    # Using Redis for caching
    # Cache key based on request arguments for different queries
    cache_key = f"units_available_{hash(frozenset(request.args.items()))}"

    try:
        if redis_client:
            # 1. Check Cache (using Redis GET)
            cached_data = redis_client.get(cache_key)

            if cached_data:
                print(f"Cache Hit for key: {cache_key}")
                # Deserialize the data from JSON string to Python object
                return jsonify({'cached': True, 'data': json.loads(cached_data)}), 200

            print(f"Cache Miss for key: {cache_key}")

        # 2. If Cache Miss or no Redis connection, fetch from Units Service
        # No authentication header needed for the public Units service endpoint
        service_response = requests.get(f'{UNITS_SERVICE_URL}/units/available', params=request.args)

        if service_response.status_code != 200:
             return jsonify(service_response.json()), service_response.status_code

        fresh_data = service_response.json()

        # 3. Store in Cache (using Redis SET with TTL)
        if redis_client:
            try:
                # Serialize the data to a JSON string before storing in Redis
                redis_client.set(cache_key, json.dumps(fresh_data), ex=CACHE_TTL_SECONDS)
                print(f"Set cache for key: {cache_key} with TTL: {CACHE_TTL_SECONDS}s")
            except redis.exceptions.RedisError as e:
                 print(f"Warning: Failed to set cache for key {cache_key} in Redis: {e}")

        # 4. Return Fresh Data
        return jsonify({'cached': False, 'data': fresh_data}), 200

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error communicating with units service (with cache): {e}", exc_info=True)
        return jsonify({'message': f'Error communicating with units service: {e}'}), 500
    except Exception as e:
        app.logger.error(f"An unexpected error occurred in get_available_units: {e}", exc_info=True)
        return jsonify({'message': f'An unexpected error occurred: {e}'}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)