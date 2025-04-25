from flask import Flask, jsonify
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from models import Transaction # Import model
import os

app = Flask(__name__)

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost:5432/finances_db')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

@app.route('/finances/transactions', methods=['GET'])
def get_transactions():
    db = SessionLocal()
    transactions = db.query(Transaction).all()
    db.close()
    # Convert SQLAlchemy objects to dictionaries for JSON serialization
    transactions_list = [{"id": t.id, "description": t.description, "amount": t.amount, "type": t.type} for t in transactions]
    return jsonify(transactions_list)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)