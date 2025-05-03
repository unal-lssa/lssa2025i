from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class LegalDocument(Base):
    __tablename__ = 'legal_documents'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    file_path = Column(String(255), unique=True, nullable=False)
    document_type = Column(String(50), nullable=False)
    related_unit_id = Column(Integer, nullable=True) # Can be null if not unit-specific
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<LegalDocument(title='{self.title}', type='{self.document_type}')>"