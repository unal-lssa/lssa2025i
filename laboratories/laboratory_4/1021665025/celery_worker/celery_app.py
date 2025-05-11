from celery import Celery
import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DECIMAL, TIMESTAMP, BOOLEAN, TEXT
from sqlalchemy.sql import func

Base = declarative_base()

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    amount = Column(Float)
    type = Column(String)

class LegalDocument(Base):
     __tablename__ = 'legal_documents'

     id = Column(Integer, primary_key=True, index=True)
     title = Column(String(255), nullable=False)
     file_path = Column(String(255), unique=True, nullable=False)
     document_type = Column(String(50), nullable=False)
     related_unit_id = Column(Integer, nullable=True)
     created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

     def __repr__(self):
        return f"<LegalDocument(title='{self.title}', type='{self.document_type}')>"


# Configure Celery
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'amqp://guest:guest@localhost:5672//')
CELERY_BACKEND_URL = os.environ.get('CELERY_BACKEND_URL', 'redis://localhost:6379/1')

celery_app = Celery(
    'celery_app',
    broker=CELERY_BROKER_URL,
    backend=CELERY_BACKEND_URL
)

# Configure task queues and priorities
celery_app.conf.update(
    task_queues = {
        'high_priority': {'exchange': 'high_priority', 'routing_key': 'high_priority'},
        'low_priority': {'exchange': 'low_priority', 'routing_key': 'low_priority'},
        'celery': {'exchange': 'celery', 'routing_key': 'celery'},
    },
    task_default_queue = 'low_priority',
    task_create_missing_queues = True,
    task_queue_max_priority = 9,
    task_default_priority = 5
)

# Database Connections for the Worker
FINANCES_DATABASE_URL = os.environ.get('FINANCES_DATABASE_URL', 'postgresql://user:password@localhost:5432/finances_db')
LEGAL_DATABASE_URL = os.environ.get('LEGAL_DATABASE_URL', 'postgresql://user:password@localhost:5432/legal_db')

finances_engine = create_engine(FINANCES_DATABASE_URL)
FinancesSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=finances_engine)

legal_engine = create_engine(LEGAL_DATABASE_URL)
LegalSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=legal_engine)

# Helper to get DB session for tasks
def get_finances_db():
    db = FinancesSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_legal_db():
    db = LegalSessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Define Celery Tasks (Actual Implementation) ---

@celery_app.task(queue='high_priority', priority=0)
def generate_finances_report_task():
    print(f"Worker: Starting Finances Report generation...")
    start_time = time.time()
    db = next(get_finances_db())

    try:
        transactions = db.query(Transaction).all()
        report_data = [{"id": t.id, "description": t.description, "amount": float(t.amount), "type": t.type} for t in transactions]
        print(f"Worker: Fetched {len(report_data)} transactions.")
        time.sleep(5)
        end_time = time.time()
        print(f"Worker: Finances Report generation complete in {end_time - start_time:.2f} seconds.")
        return {"status": "completed", "report_name": "Finances Report", "data_count": len(report_data)}

    except Exception as e:
        print(f"Worker: Error generating finances report: {e}")
        raise


@celery_app.task(queue='low_priority', priority=5)
def generate_legal_report_task():
    print(f"Worker: Starting Legal Report generation...")
    start_time = time.time()
    db = next(get_legal_db())

    try:
        documents = db.query(LegalDocument).all()
        report_data = [
             {
                "id": doc.id,
                "title": doc.title,
                "file_path": doc.file_path,
                "document_type": doc.document_type,
                "related_unit_id": doc.related_unit_id,
                "created_at": doc.created_at.isoformat() if doc.created_at else None
             } for doc in documents
         ]
        print(f"Worker: Fetched {len(report_data)} legal documents.")
        time.sleep(8)
        end_time = time.time()
        print(f"Worker: Legal Report generation complete in {end_time - start_time:.2f} seconds.")
        return {"status": "completed", "report_name": "Legal Report", "data_count": len(report_data)}

    except Exception as e:
        print(f"Worker: Error generating legal report: {e}")
        raise