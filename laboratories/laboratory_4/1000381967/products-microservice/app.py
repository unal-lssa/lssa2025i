from flask import Flask, jsonify
import psycopg2
import redis
import json

app = Flask(__name__)


cache = redis.Redis(host='redis', port=6379, decode_responses=True)

def get_db_connection():
    return psycopg2.connect(
        dbname="lssadb",
        user="lssauser",
        password="password",
        host="postgres-products-db",
        port="5432"
    )

@app.route('/products', methods=['GET'])
def get_items():
    cached = cache.get("products")
    if cached:
        return jsonify({'cached': True, 'products': json.loads(cached)})

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, price FROM products")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    products = [{"id": r[0], "name": r[1], "price": float(r[2])} for r in rows]
    cache.set("products", json.dumps(products), ex=60)
    return jsonify({'cached': False, 'products': products})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
