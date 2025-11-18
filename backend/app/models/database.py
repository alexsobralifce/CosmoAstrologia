"""
SQLAlchemy database models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    google_id = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    picture = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship to birth charts
    birth_charts = relationship("BirthChart", back_populates="user", cascade="all, delete-orphan")

class BirthChart(Base):
    """Birth chart model"""
    __tablename__ = "birth_charts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Birth data
    name = Column(String, nullable=False)
    birth_date = Column(String, nullable=False)  # ISO format: YYYY-MM-DD
    birth_time = Column(String, nullable=False)  # HH:MM format
    birth_place = Column(String, nullable=False)  # City, State format
    
    # Big Three
    sun_sign = Column(String, nullable=False)
    moon_sign = Column(String, nullable=False)
    ascendant_sign = Column(String, nullable=False)
    
    # Chart data stored as JSON for flexibility
    chart_data = Column(JSON, nullable=False)  # Full chart data (planets, houses, aspects, etc.)
    
    # Metadata
    is_primary = Column(Boolean, default=False)  # Primary chart for user
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship to user
    user = relationship("User", back_populates="birth_charts")

