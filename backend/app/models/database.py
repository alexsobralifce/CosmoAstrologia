from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class PendingRegistration(Base):
    """Tabela temporária para armazenar registros pendentes de verificação de email."""
    __tablename__ = "pending_registrations"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True)
    name = Column(String, nullable=True)
    verification_code = Column(String, nullable=False)
    verification_code_expires = Column(DateTime, nullable=False)
    
    # Dados do mapa astral (armazenados como JSON string)
    birth_chart_data = Column(Text, nullable=False)  # JSON string com todos os dados
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True)  # Nullable for OAuth users
    name = Column(String, nullable=True)
    # google_id será adicionado em uma migração futura
    # google_id = Column(String, nullable=True, unique=True)  # Google OAuth ID
    is_active = Column(Boolean, default=False)  # Mudar para False até verificação
    email_verified = Column(Boolean, default=False)  # Novo campo
    verification_code = Column(String, nullable=True)  # Código de verificação
    verification_code_expires = Column(DateTime, nullable=True)  # Expiração do código
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    birth_charts = relationship("BirthChart", back_populates="user", cascade="all, delete-orphan")


class BirthChart(Base):
    __tablename__ = "birth_charts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Birth data
    name = Column(String, nullable=False)
    birth_date = Column(DateTime, nullable=False)
    birth_time = Column(String, nullable=False)  # Format: "HH:MM"
    birth_place = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Calculated signs
    sun_sign = Column(String, nullable=False)  # e.g., "Libra"
    moon_sign = Column(String, nullable=False)  # e.g., "Aquarius"
    ascendant_sign = Column(String, nullable=False)  # e.g., "Aquarius"
    
    # Additional calculated data (can be extended)
    sun_degree = Column(Float, nullable=True)
    moon_degree = Column(Float, nullable=True)
    ascendant_degree = Column(Float, nullable=True)
    
    is_primary = Column(Boolean, default=True)  # Primary birth chart for the user
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="birth_charts")

