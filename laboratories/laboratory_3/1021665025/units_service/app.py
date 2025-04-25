from flask import Flask, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from models import Base, RentalUnit # Import models
import os

app = Flask(__name__)

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost:5432/units_db')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper function to get a database session
def current_db():
    return next(get_db())

@app.route('/units/available', methods=['GET'])
def get_available_units():
    """Endpoint to get all available rental units."""
    db = current_db()
    try:
        # Query for units where is_available is TRUE
        available_units = db.query(RentalUnit).filter(RentalUnit.is_available == True).all()

        # Convert SQLAlchemy objects to dictionaries for JSON serialization
        units_list = [
            {
                "id": unit.id,
                "unit_number": unit.unit_number,
                "address": unit.address,
                "city": unit.city,
                "state": unit.state,
                "zip_code": unit.zip_code,
                "bedrooms": unit.bedrooms,
                "bathrooms": float(unit.bathrooms), # Convert Decimal to float for JSON
                "rent_amount": float(unit.rent_amount), # Convert Decimal to float
                "is_available": unit.is_available,
                "description": unit.description,
                "created_at": unit.created_at.isoformat() if unit.created_at else None
            } for unit in available_units
        ]
        return jsonify(units_list)
    except Exception as e:
        return jsonify({'message': 'An error occurred while fetching available units', 'error': str(e)}), 500
    finally:
        db.close()

if __name__ == '__main__':
    # Use host='0.0.0.0' to make it accessible within the Docker network
    app.run(host='0.0.0.0', port=5004, debug=True)