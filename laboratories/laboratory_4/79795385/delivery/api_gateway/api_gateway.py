from flask import Flask, request, jsonify
import jwt, requests
from functools import wraps
from threading import Thread
import time
import os

app = Flask(__name__)
SECRET_KEY = "secret"

# To know what instance is answering
INSTANCE_NAME = os.environ.get("GATEWAY_ID", "unknown")

# Decorators (reuse token auth if desired)
def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token: return jsonify({'error': 'Missing token'}), 403
        try: jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except: return jsonify({'error': 'Invalid token'}), 403
        return f(*args, **kwargs)
    return wrapper

# To check if the loadbalancer works
@app.route("/getInstanceName", methods=["GET"])
# @token_required
def get_instance_name():
    return jsonify({'InstanceName': INSTANCE_NAME}), 202

# Cached data access with Stale-While-Revalidate and Cache Locking
@app.route("/data", methods=["GET"])
# @token_required
def get_data():
    key = "my_data"
    force_refresh = request.args.get("refresh") == "true"
    
    if not force_refresh:
        cache_resp = requests.get(f"http://cache:5004/cache/{key}").json()
        if cache_resp['value']:
            # Trigger background cache refresh
            Thread(target=refresh_cache_in_background, args=(key,)).start()
            return jsonify({'InstanceName': INSTANCE_NAME, 'cached': True, 'data': cache_resp['value']})

    # If no valid cache, fetch from DB and store
    db_resp = requests.get("http://database:5002/db").json()
    requests.post(f"http://cache:5004/cache/{key}", json={'value': db_resp['message']})
    return jsonify({'InstanceName': INSTANCE_NAME, 'cached': False, 'data': db_resp['message']})

def refresh_cache_in_background(key):
    try:
        db_resp = requests.get("http://database:5002/db").json()
        requests.post(f"http://cache:5004/cache/{key}", json={'value': db_resp['message']})
    except Exception as e:
        print(f"Background cache refresh failed: {e}")


# Trigger async task
@app.route("/longtask", methods=["POST"])
# @token_required
def long_task():
    payload = request.json
    requests.post("http://worker:5005/task", json=payload)
    return jsonify({'status': 'Task queued'}), 202
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
    # app.run(port=5000, debug=True)