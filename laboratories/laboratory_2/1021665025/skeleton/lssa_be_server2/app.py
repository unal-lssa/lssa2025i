
from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

@app.route('/create', methods=['POST'])
def create():
    data = request.json
    conn = mysql.connector.connect(
        host='lssa_db',
        user='root',
        password='root',
        database='lssa_db'
    )
    cursor = conn.cursor()
    cursor.execute("INSERT INTO systems (name) VALUES (%s)", (data['name'],))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify(status="created")

@app.route('/systems')
def get_systems():
    conn = mysql.connector.connect(
        host='lssa_db',
        user='root',
        password='root',
        database='lssa_db'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM systems")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(systems=rows)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
