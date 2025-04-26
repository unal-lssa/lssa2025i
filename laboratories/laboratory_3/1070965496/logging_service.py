from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/log', methods=['POST'])
def log():
    log_data = request.get_json()
    print(f"LOG: {log_data}")
    return jsonify({'message': 'Log entry recorded'}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5004)