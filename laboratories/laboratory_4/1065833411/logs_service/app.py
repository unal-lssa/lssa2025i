from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/log', methods=['POST'])
def log():
    data = request.get_json()
    with open("log_db.txt", "a") as f:
        f.write(f"{data}\n")
    return jsonify({"status": "log saved"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)