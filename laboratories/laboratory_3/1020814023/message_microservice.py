from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/message', methods=['GET'])
def message():
    return jsonify({'message': 'Este microservicio únicamente devuelve este mensaje si tienes el rol "user". Consulta satisfactoria!'}), 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5003)
