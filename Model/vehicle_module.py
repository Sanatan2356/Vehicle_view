from sqlalchemy import Column, String, Integer, DateTime, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
from database import Base
from datetime import datetime

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), unique=True, nullable=False)
    country = Column(String(30), nullable=False)

    brands = relationship("Brand", back_populates="company")
    vehicles = relationship("Vehicle", back_populates="company")


class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), unique=True, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)

    company = relationship("Company", back_populates="brands")
    models = relationship("VehicleModel", back_populates="brand")
    vehicles = relationship("Vehicle", back_populates="brand")


class VehicleModel(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), unique=True, nullable=False)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)

    brand = relationship("Brand", back_populates="models")
    vehicles = relationship("Vehicle", back_populates="model")

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_number = Column(String(30), unique=True, nullable=False)
    
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=False)
    
    manufacturing_year = Column(Integer, nullable=False)
    fuel_type = Column(String(20), nullable=False)
    color = Column(String(20), nullable=False)
    vehicle_reg_date = Column(Date)
    last_service_date = Column(Date)
    mileage = Column(Float)
    vehicle_photos=Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="vehicles")
    brand = relationship("Brand", back_populates="vehicles")
    model = relationship("VehicleModel", back_populates="vehicles")


# Optional Bookmark Example
class Bookmark(Base):
    __tablename__ = "bookmarks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="bookmarks")
    vehicle = relationship("Vehicle", back_populates="bookmarked_by")
