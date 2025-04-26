import re
import ipaddress
from functools import wraps
from flask import request, jsonify
import time
import jwt
import requests
import os

# IP validation helpers
def is_ip_in_cidr(ip, cidr):
    """Check if an IP is in a CIDR range"""
    try:
        return ipaddress.ip_address(ip) in ipaddress.ip_network(cidr)
    except ValueError:
        return False

def is_ip_authorized(ip, authorized_ips):
    """Check if an IP is authorized, supporting CIDR notation"""
    for allowed in authorized_ips:
        allowed = allowed.strip()
        if '/' in allowed:  # CIDR notation
            if is_ip_in_cidr(ip, allowed):
                return True
        elif ip == allowed:
            return True
    return False

# Rate limiting helpers
class RateLimiter:
    def __init__(self):
        self.request_counts = {}
    
    def is_rate_limited(self, key, limit, window):
        """
        Check if a key is rate limited
        key: unique identifier (IP, user_id, etc.)
        limit: max requests allowed
        window: time window in seconds
        """
        current_time = time.time()
        
        # Initialize or clean up old requests
        if key not in self.request_counts:
            self.request_counts[key] = []
        else:
            # Keep only recent requests within the window
            self.request_counts[key] = [t for t in self.request_counts[key] 
                                     if current_time - t < window]
        
        # Check if rate limit exceeded
        if len(self.request_counts[key]) >= limit:
            return True
        
        # Add this request
        self.request_counts[key].append(current_time)
        return False

# Circuit breaker helpers
class CircuitBreaker:
    def __init__(self, fail_threshold=5, reset_timeout=30):
        self.fail_threshold = fail_threshold
        self.reset_timeout = reset_timeout
        self.services = {}
    
    def is_open(self, service_name):
        """Check if circuit for service is open"""
        if service_name not in self.services:
            self.services[service_name] = {
                'fails': 0,
                'status': 'CLOSED',
                'last_failure': 0
            }
            
        circuit = self.services[service_name]
        
        # If circuit is open, check if reset timeout has passed
        if circuit['status'] == 'OPEN':
            if time.time() - circuit['last_failure'] > self.reset_timeout:
                circuit['status'] = 'HALF_OPEN'
                return False  # Allow a test request
            return True  # Circuit still open
            
        return False  # Circuit closed or half-open
    
    def record_success(self, service_name):
        """Record a successful request"""
        if service_name in self.services and self.services[service_name]['status'] == 'HALF_OPEN':
            self.services[service_name]['status'] = 'CLOSED'
            self.services[service_name]['fails'] = 0
    
    def record_failure(self, service_name):
        """Record a failed request"""
        if service_name not in self.services:
            self.services[service_name] = {
                'fails': 0,
                'status': 'CLOSED',
                'last_failure': 0
            }
            
        circuit = self.services[service_name]
        circuit['fails'] += 1
        circuit['last_failure'] = time.time()
        
        if circuit['fails'] >= self.fail_threshold:
            circuit['status'] = 'OPEN'

# Common security decorators
def require_api_key(api_key):
    """Decorator factory to check API key"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            provided_key = request.headers.get('X-API-Key')
            if provided_key != api_key:
                return jsonify({'message': 'Invalid API key'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_jwt(secret_key):
    """Decorator factory to validate JWT token"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({'message': 'Token is missing!'}), 401
                
            try:
                if token.startswith('Bearer '):
                    token = token[7:]
                data = jwt.decode(token, secret_key, algorithms=["HS256"])
                request.token_data = data
            except Exception as e:
                return jsonify({'message': f'Invalid token: {str(e)}'}), 401
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_request_schema(schema):
    """Decorator factory to validate request data against a schema"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.is_json:
                data = request.get_json()
                errors = []
                
                for field, field_schema in schema.items():
                    if field_schema.get('required', False) and field not in data:
                        errors.append(f"Field '{field}' is required")
                    elif field in data:
                        # Type validation
                        if field_schema.get('type') == 'string' and not isinstance(data[field], str):
                            errors.append(f"Field '{field}' must be a string")
                        elif field_schema.get('type') == 'number' and not isinstance(data[field], (int, float)):
                            errors.append(f"Field '{field}' must be a number")
                        
                        # Pattern validation
                        if field_schema.get('pattern') and isinstance(data[field], str):
                            pattern = re.compile(field_schema['pattern'])
                            if not pattern.match(data[field]):
                                errors.append(f"Field '{field}' has invalid format")
                
                if errors:
                    return jsonify({'message': 'Validation error', 'errors': errors}), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def sanitize_input(text):
    """Sanitize input to prevent common injection attacks"""
    if not isinstance(text, str):
        return text
    
    # Escape common HTML entities
    escapes = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    }
    
    # Replace disallowed characters
    for char, escape in escapes.items():
        text = text.replace(char, escape)
    
    # Prevent SQL injection (basic)
    sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'EXEC', 'UNION']
    pattern = '|'.join(sql_keywords)
    cleaned = re.sub(f'(?i)\\b({pattern})\\b', '', text)
    
    return cleaned
