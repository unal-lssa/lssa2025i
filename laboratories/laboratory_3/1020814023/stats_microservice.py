from flask import Flask, jsonify

app = Flask(__name__)

visit_count = 0

@app.route('/stats', methods=['GET'])
def stats():
    global visit_count
    visit_count += 1
    return jsonify({'message': f'Stats: Este servicio ha sido visitado {visit_count} vece(s).'}), 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5004)
