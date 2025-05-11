from flask import Flask, request, jsonify

app = Flask(__name__)
cache = {}

@app.route("/cache/<key>", methods=["GET"])
def get_cache(key):
    return jsonify({'value': cache.get(key)})

@app.route("/cache/<key>", methods=["POST"])
def set_cache(key):
    data = request.json
    cache[key] = data.get("value")
    return jsonify({'status': 'ok'})

# Added session and authentication caching endpoints
session_cache = {}
auth_cache = {}

@app.route("/session/<session_id>", methods=["GET"])
def get_session(session_id):
    return jsonify({'session_data': session_cache.get(session_id)})

@app.route("/session/<session_id>", methods=["POST"])
def set_session(session_id):
    data = request.json
    session_cache[session_id] = data.get("session_data")
    return jsonify({'status': 'ok'})

@app.route("/auth/<token>", methods=["GET"])
def get_auth(token):
    return jsonify({'auth_data': auth_cache.get(token)})

@app.route("/auth/<token>", methods=["POST"])
def set_auth(token):
    data = request.json
    auth_cache[token] = data.get("auth_data")
    return jsonify({'status': 'ok'})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5004, debug=True)