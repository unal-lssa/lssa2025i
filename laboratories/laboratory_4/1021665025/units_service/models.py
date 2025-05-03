from sqlalchemy import Column, Integer, String, DECIMAL, BOOLEAN, TEXT, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class RentalUnit(Base):
    __tablename__ = 'rental_units'

    id = Column(Integer, primary_key=True, index=True)
    unit_number = Column(String(50), unique=True, nullable=False)
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False)
    zip_code = Column(String(20), nullable=True)
    bedrooms = Column(Integer, nullable=True)
    bathrooms = Column(DECIMAL(3, 1), nullable=True)
    rent_amount = Column(DECIMAL(10, 2), nullable=False)
    is_available = Column(BOOLEAN, nullable=False, default=True)
    description = Column(TEXT, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<RentalUnit(unit_number='{self.unit_number}', city='{self.city}')>"