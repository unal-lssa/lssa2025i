from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/db')
def db_access():
    return jsonify({'message': 'Database access granted'}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5002)