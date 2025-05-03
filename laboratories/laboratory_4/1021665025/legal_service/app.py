from flask import Flask, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from models import Base, LegalDocument
import os

app = Flask(__name__)

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost:5432/legal_db')
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

@app.route('/legal/documents', methods=['GET'])
def get_all_legal_documents():
    db = current_db()
    try:
        documents = db.query(LegalDocument).all()
        # Convert SQLAlchemy objects to dictionaries for JSON serialization
        documents_list = [
            {
                "id": doc.id,
                "title": doc.title,
                "file_path": doc.file_path,
                "document_type": doc.document_type,
                "related_unit_id": doc.related_unit_id,
                "created_at": doc.created_at.isoformat() if doc.created_at else None # Format datetime for JSON
            } for doc in documents
        ]
        return jsonify(documents_list)
    except Exception as e:
        return jsonify({'message': 'An error occurred while fetching legal documents', 'error': str(e)}), 500
    finally:
        db.close()

@app.route('/legal/generate_report', methods=['POST'])
def generate_legal_report_request():
    print(f"Received request to generate legal report with data")
    # This endpoint only acknowledges the request; the API Gateway will send the task to the queue
    return jsonify({'status': 'Legal report generation request received'}), 202 # 202 Accepted

if __name__ == '__main__':
    # Use host='0.0.0.0' to make it accessible within the Docker network
    app.run(host='0.0.0.0', port=5003, debug=True)