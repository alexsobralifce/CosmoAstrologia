from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    password: Optional[str] = None  # Optional for OAuth users


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class BirthData(BaseModel):
    name: str
    birth_date: datetime
    birth_time: str  # Format: "HH:MM"
    birth_place: str
    latitude: float
    longitude: float


class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    birth_data: Optional[BirthData] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class BirthChartCreate(BirthData):
    sun_sign: str
    moon_sign: str
    ascendant_sign: str
    sun_degree: Optional[float] = None
    moon_degree: Optional[float] = None
    ascendant_degree: Optional[float] = None


class BirthChartResponse(BirthChartCreate):
    id: int
    user_id: int
    is_primary: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    # Planetas principais (opcionais, calculados mas não salvos no banco)
    mercury_sign: Optional[str] = None
    mercury_degree: Optional[float] = None
    venus_sign: Optional[str] = None
    venus_degree: Optional[float] = None
    mars_sign: Optional[str] = None
    mars_degree: Optional[float] = None
    jupiter_sign: Optional[str] = None
    jupiter_degree: Optional[float] = None
    saturn_sign: Optional[str] = None
    saturn_degree: Optional[float] = None
    uranus_sign: Optional[str] = None
    uranus_degree: Optional[float] = None
    neptune_sign: Optional[str] = None
    neptune_degree: Optional[float] = None
    pluto_sign: Optional[str] = None
    pluto_degree: Optional[float] = None
    midheaven_sign: Optional[str] = None
    midheaven_degree: Optional[float] = None
    planets_conjunct_midheaven: Optional[List[str]] = None
    uranus_on_midheaven: Optional[bool] = None
    # Nodos Lunares
    north_node_sign: Optional[str] = None
    north_node_degree: Optional[float] = None
    south_node_sign: Optional[str] = None
    south_node_degree: Optional[float] = None
    # Quíron (a ferida do curador)
    chiron_sign: Optional[str] = None
    chiron_degree: Optional[float] = None
    
    class Config:
        from_attributes = True


class UserRegister(BaseModel):
    email: EmailStr
    password: Optional[str] = None  # Opcional para permitir OAuth, mas recomendado para registro normal
    name: str
    birth_data: BirthData


class Token(BaseModel):
    access_token: str
    token_type: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str

