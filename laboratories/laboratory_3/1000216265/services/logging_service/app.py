from flask import Flask, request, jsonify
import os
import time
import json
from functools import wraps
from datetime import datetime

app = Flask(__name__)

# Configuration
API_KEY = os.environ.get('LOGGING_SERVICE_KEY', 'logging_secret_key')
LOG_FILE = os.environ.get('LOG_FILE', 'security_logs.json')
MAX_LOG_SIZE_MB = int(os.environ.get('MAX_LOG_SIZE_MB', '10'))  # 10MB default

# In-memory log buffer for performance
log_buffer = []
last_flush_time = time.time()
FLUSH_INTERVAL = 10  # seconds

# API key validation decorator
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        provided_key = request.headers.get('X-API-Key')
        if provided_key != API_KEY:
            return jsonify({'message': 'Invalid API key'}), 403
        return f(*args, **kwargs)
    return decorated_function

def flush_logs():
    """Flush logs from memory to disk"""
    global log_buffer, last_flush_time
    
    if not log_buffer:
        return
        
    try:
        # Load existing logs if file exists
        logs = []
        if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 0:
            with open(LOG_FILE, 'r') as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []
        
        # Append new logs
        logs.extend(log_buffer)
        
        # Check file size limit
        if len(json.dumps(logs)) > MAX_LOG_SIZE_MB * 1024 * 1024:
            # Rotate logs - keep only most recent entries
            logs = logs[-1000:]  # Keep last 1000 entries
            
        # Write logs back to file
        with open(LOG_FILE, 'w') as f:
            json.dump(logs, f)
            
        log_buffer = []
        last_flush_time = time.time()
    except Exception as e:
        print(f"Error flushing logs: {e}")

@app.route('/log', methods=['POST'])
@require_api_key
def log_event():
    if not request.is_json:
        return jsonify({'message': 'Missing JSON data'}), 400
        
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['event_type', 'details']
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'Missing required field: {field}'}), 400
            
    # Add timestamp if not provided
    if 'timestamp' not in data:
        data['timestamp'] = datetime.now().isoformat()
        
    # Add client IP
    data['client_ip'] = request.remote_addr
    
    # Add to log buffer
    log_buffer.append(data)
    
    # Flush logs if it's been a while
    if time.time() - last_flush_time > FLUSH_INTERVAL:
        flush_logs()
    
    return jsonify({'message': 'Event logged successfully'}), 201

@app.route('/logs', methods=['GET'])
@require_api_key
def get_logs():
    # First flush any pending logs
    flush_logs()
    
    try:
        if not os.path.exists(LOG_FILE):
            return jsonify([]), 200
            
        with open(LOG_FILE, 'r') as f:
            try:
                logs = json.load(f)
                
                # Get query parameters for filtering
                event_type = request.args.get('event_type')
                start_time = request.args.get('start_time')
                end_time = request.args.get('end_time')
                client_ip = request.args.get('client_ip')
                
                # Apply filters
                if event_type:
                    logs = [log for log in logs if log.get('event_type') == event_type]
                if start_time:
                    logs = [log for log in logs if log.get('timestamp', '') >= start_time]
                if end_time:
                    logs = [log for log in logs if log.get('timestamp', '') <= end_time]
                if client_ip:
                    logs = [log for log in logs if log.get('client_ip') == client_ip]
                    
                return jsonify(logs), 200
            except json.JSONDecodeError:
                return jsonify({'message': 'Error reading logs'}), 500
    except Exception as e:
        return jsonify({'message': f'Error retrieving logs: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

# Flush logs when shutting down
@app.teardown_appcontext
def shutdown(exception=None):
    flush_logs()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5004)
