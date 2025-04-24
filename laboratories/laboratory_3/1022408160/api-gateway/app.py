import logging
import os
from flask import Flask, Response, request, jsonify
import jwt
from functools import wraps
from flask_cors import CORS
import requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

allowed_origins = os.environ.get('CORS_ALLOWED_ORIGINS').split(',')
logging.info(f"Configuring CORS for origins: {allowed_origins}")
CORS(app, resources={r"/*": {"origins": allowed_origins}}, supports_credentials=True)


SECRET_KEY = "your_secret_key"
AUTHORIZED_IP = os.environ.get('AUTHORIZED_IP')
AGENDA_API_URL = os.environ.get('AGENDA_API_URL')
SECRET_AGENDA_API_URL = os.environ.get('SECRET_AGENDA_API_URL')


# Mock users for the sake of the example
# Now includes a role for each user to limit 
USERS = {
    "Pam": {"password": "Jim1234",
              "role": "secretary"},
    "Dwight": {"password": "Beet1234",
              "role": "master"}
}


def _forward_request(method, api_url, path, incoming_request):
    """
    Forwards the incoming request to the target service (Agenda API).
    Raises requests exceptions on failure.
    Returns the requests.Response object on success.
    """
    target_url = f"{api_url}{path}"
    logging.info(f"Gateway forwarding {method} request to: {target_url}")

    # Prepare headers: Forward most headers, excluding 'Host' as it should be the target host
    headers = {key: value for (key, value) in incoming_request.headers if key.lower() != 'host'}
    headers['Host'] = AGENDA_API_URL.split('//')[-1].split('/')[0] # Set correct host for target

    # Prepare params and data/json
    params = incoming_request.args
    data = incoming_request.get_data() # Raw data
    json_payload = incoming_request.get_json(silent=True) # Parsed JSON if content-type is correct

    try:
        # Use requests.request to handle various methods
        resp = requests.request(
            method=method,
            url=target_url,
            headers=headers,
            params=params,
            data=data if json_payload is None else None, # Send raw data if no json
            json=json_payload, # Send parsed json if available
            timeout=10, # Set a reasonable timeout (e.g., 10 seconds)
            stream=True # Efficient for potentially large responses
        )
        # Raise exceptions for bad status codes (4xx or 5xx) from the target service
        resp.raise_for_status()
        return resp

    # Let specific exceptions be caught by the error handlers below
    except requests.exceptions.RequestException as e:
        logging.error(f"RequestException during forward to {target_url}: {e}")
        raise # Re-raise the exception to be caught by Flask's error handlers

def roles_required(*allowed_roles):
    """
    Decorator to verify JWT token and check if user role is in allowed_roles.
    Implicitly performs token validation.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                logging.warning("Role check failed: Token is missing!")
                return jsonify({'message': 'Authorization Token is missing!'}), 401

            # Handle 'Bearer ' prefix if present
            if ' ' in token:
                try:
                    token_type, token = token.split(' ', 1)
                    if token_type.lower() != 'bearer':
                        logging.warning("Role check failed: Invalid token type!")
                        return jsonify({'message': 'Invalid token type!'}), 401
                except ValueError:
                    logging.warning("Role check failed: Malformed Authorization header!")
                    return jsonify({'message': 'Malformed Authorization header!'}), 401

            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                user_role = payload.get('role') # Assumes 'role' claim exists in JWT payload
                username = payload.get('username', 'Unknown') # For logging

                if not user_role:
                    logging.error(f"Role check failed: 'role' claim missing in token for user {username}.")
                    return jsonify({'message': 'Forbidden: Role information missing in token.'}), 403

                if user_role in allowed_roles:
                    logging.info(f"Role '{user_role}' for user '{username}' authorized for route requiring {allowed_roles}.")
                    # Role is allowed, proceed to the original route function
                    return f(*args, **kwargs)
                else:
                    logging.warning(f"Role check failed: User '{username}' with role '{user_role}' denied access to route requiring {allowed_roles}.")
                    # Role is not allowed
                    return jsonify({'message': f'Forbidden: Your role ({user_role}) is not authorized for this resource.'}), 403

            except jwt.ExpiredSignatureError:
                logging.warning("Role check failed: Token has expired!")
                return jsonify({'message': 'Token has expired!'}), 401
            except jwt.InvalidTokenError as e:
                logging.warning(f"Role check failed: Token is invalid! Error: {e}")
                return jsonify({'message': 'Token is invalid!'}), 401
            except Exception as e:
                logging.exception(f"Unexpected error during role check: {e}")
                return jsonify({'message': 'Internal server error during authorization.'}), 500

        return decorated_function
    return decorator

# Function to check if the request comes from an authorized IP address
def limit_exposure(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        logging.info(f"Authorized IP: {AUTHORIZED_IP}")
        logging.info(f"Client IP: {client_ip}")
        if AUTHORIZED_IP not in client_ip:
            return jsonify({'message': 'Forbidden: Unauthorized IP'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Function to check JWT token
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except:
            return jsonify({'message': 'Token is invalid!'}), 403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@limit_exposure
def gateway_index():
    """Basic index route for the gateway."""
    return jsonify({"message": "API Gateway is running."})

# Route for user login (returns JWT token)
@app.route('/login', methods=['POST'])
@limit_exposure 
def login():
    """Handles user login and issues JWT with role."""
    auth = request.get_json()
    if not auth or not auth.get('username') or not auth.get('password'):
        return jsonify({'message': 'Username and password required'}), 400

    username = auth.get('username')
    password = auth.get('password')
    user_info = USERS.get(username)

    if user_info and user_info.get('password') == password:
        user_role = user_info.get('role')
        if not user_role:
             logging.error(f"Login failed for {username}: User role not defined in USERS.")
             return jsonify({'message': 'Login failed: Internal configuration error.'}), 500

        try:
            token = jwt.encode(
                {'username': username, 'role': user_role}, # Ensure role is in payload
                SECRET_KEY,
                algorithm="HS256"
            )
            logging.info(f"Login successful for user '{username}', role '{user_role}'.")
            return jsonify({'token': token})
        except Exception as e:
             logging.exception(f"Error encoding JWT for user {username}: {e}")
             return jsonify({'message': 'Login failed: Could not generate token.'}), 500
    else:
        logging.warning(f"Login failed for user '{username}': Invalid credentials.")
        return jsonify({'message': 'Invalid credentials'}), 401



# Protected route
@app.route('/data', methods=['GET'])
@token_required
@limit_exposure # Apply the limit exposure tactic to this route
def get_data():
    return jsonify({'message': 'Data accessed successfully!'}), 200

@app.route('/meetings', methods=['GET'])
@token_required
@roles_required('master', 'secretary')
def forward_meetings():
    """Forwards GET requests to the /meetings endpoint of the agenda API."""
    resp = _forward_request(method='GET', 
                            api_url=AGENDA_API_URL,
                            path='/meetings', 
                            incoming_request=request)
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]
    return Response(resp.content, resp.status_code, headers)

@app.route('/extra-meetings', methods=['GET'])
@token_required
@roles_required('master')
def forward_secret_meetings():
    """Forwards GET requests to the /meetings endpoint of the agenda API."""
    resp = _forward_request(method='GET', 
                            api_url=SECRET_AGENDA_API_URL,
                            path='/meetings', 
                            incoming_request=request)
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]
    return Response(resp.content, resp.status_code, headers)



# --- Centralized Exception Handlers ---
@app.errorhandler(requests.exceptions.ConnectionError)
def handle_connection_error(e):
    logging.error(f"ConnectionError connecting to upstream service: {e}")
    return jsonify({"error": "Upstream service unavailable", "type": "ConnectionError"}), 502 # 502 Bad Gateway

@app.errorhandler(requests.exceptions.Timeout)
def handle_timeout_error(e):
    logging.error(f"Timeout connecting to upstream service: {e}")
    return jsonify({"error": "Upstream service timed out", "type": "Timeout"}), 504 # 504 Gateway Timeout

@app.errorhandler(requests.exceptions.HTTPError)
def handle_http_error(e):
    # Handle 4xx/5xx errors returned *from* the downstream service (agenda_api)
    logging.error(f"HTTPError from upstream service: {e.response.status_code} - {e.response.text}")
    try:
        # Attempt to parse JSON error from downstream
        error_details = e.response.json()
    except ValueError:
        # If downstream response is not JSON, use text
        error_details = e.response.text
    return jsonify({
        "error": "Upstream service returned an error",
        "type": "HTTPError",
        "upstream_status": e.response.status_code,
        "upstream_details": error_details
    }), e.response.status_code # Return the same status code the upstream service gave

@app.errorhandler(requests.exceptions.RequestException)
def handle_generic_request_error(e):
    # Catch other request-related errors (like invalid URL, SSL issues etc.)
    logging.error(f"Generic RequestException: {e}")
    return jsonify({"error": "Failed to process request to upstream service", "type": "RequestException"}), 500

@app.errorhandler(Exception)
def handle_generic_error(e):
    # Catch-all for any other unexpected errors within the gateway itself
    logging.exception(f"An unexpected error occurred in the gateway: {e}") # Use logging.exception to include stack trace
    return jsonify({"error": "An internal gateway error occurred", "type": "InternalError"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
