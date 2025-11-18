from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Onboarding/Chart Calculation
class BirthData(BaseModel):
    name: str
    birth_date: str  # ISO format: YYYY-MM-DD
    birth_time: str  # HH:MM format
    birth_place: str  # City, State format

# Planet Positions
class PlanetPosition(BaseModel):
    planet: str
    sign: str
    house: int
    degree: float
    minutes: int = 0

# Houses
class House(BaseModel):
    number: int
    cusp_sign: str
    cusp_degree: float
    planets_in_house: List[str]

# Aspects
class Aspect(BaseModel):
    planet1: str
    planet2: str
    type: str  # conjunction, opposition, square, trine, sextile
    orb: float
    is_positive: bool

# Big Three
class BigThree(BaseModel):
    sun: str
    moon: str
    ascendant: str

# Elements and Modalities
class ElementData(BaseModel):
    name: str
    percentage: float
    color: str

class ModalityData(BaseModel):
    name: str
    percentage: float
    color: str

# Chart Ruler
class ChartRuler(BaseModel):
    ascendant: str
    ruler: str
    ruler_sign: str
    ruler_house: int

# Complete Birth Chart Response
class BirthChartResponse(BaseModel):
    birth_data: BirthData
    big_three: BigThree
    planets: List[PlanetPosition]
    houses: List[House]
    aspects: List[Aspect]
    elements: List[ElementData]
    modalities: List[ModalityData]
    chart_ruler: ChartRuler

# Planet Interpretation
class PlanetInterpretation(BaseModel):
    planet: str
    sign: str
    house: int
    in_sign: str
    in_house: str

# House Interpretation
class HouseInterpretation(BaseModel):
    house_number: int
    theme: str
    interpretation: str

# Aspect Interpretation
class AspectInterpretation(BaseModel):
    aspect: Aspect
    interpretation: str
    tags: List[str]

# Daily Transits
class DailyTransit(BaseModel):
    moon_sign: str
    moon_house: int
    moon_advice: str
    is_mercury_retrograde: bool
    is_moon_void_of_course: bool
    void_ends_at: Optional[str] = None

# Future Transit
class FutureTransit(BaseModel):
    type: str  # jupiter, saturn-return, uranus, neptune, pluto
    title: str
    planet: str
    timeframe: str
    description: str
    is_active: bool

# Interpretation Request
class InterpretationRequest(BaseModel):
    chart: BirthChartResponse
    topic: str  # planet, house, aspect, or specific ID

# Interpretation Response
class InterpretationResponse(BaseModel):
    title: str
    content: List[dict]  # List of sections with heading and content

# User Update
class UserUpdate(BaseModel):
    name: Optional[str] = None

# User Registration
class UserRegister(BaseModel):
    name: str
    email: str
    birth_data: BirthData

