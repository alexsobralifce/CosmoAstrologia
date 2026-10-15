from pydantic import BaseModel
from typing import Optional


# ============================================================================
# MAPA ASTRAL COMPLETO - Endpoints
# ============================================================================

class FullBirthChartRequest(BaseModel):
    """Request para geração do Mapa Astral Completo."""
    name: str
    birthDate: str  # DD/MM/AAAA
    birthTime: str  # HH:MM
    birthPlace: str
    sunSign: str
    moonSign: str
    ascendant: str
    sunHouse: int
    moonHouse: int
    section: str  # 'power', 'triad', 'personal', 'houses', 'karma', 'synthesis'
    language: Optional[str] = 'pt'
    # Coordenadas do local (opcionais - se não fornecidas, tentará obter do nome do local)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    # Planetas opcionais
    mercurySign: Optional[str] = None
    mercuryHouse: Optional[int] = None
    venusSign: Optional[str] = None
    venusHouse: Optional[int] = None
    marsSign: Optional[str] = None
    marsHouse: Optional[int] = None
    jupiterSign: Optional[str] = None
    jupiterHouse: Optional[int] = None
    saturnSign: Optional[str] = None
    saturnHouse: Optional[int] = None
    uranusSign: Optional[str] = None
    uranusHouse: Optional[int] = None
    neptuneSign: Optional[str] = None
    neptuneHouse: Optional[int] = None
    plutoSign: Optional[str] = None
    plutoHouse: Optional[int] = None
    northNodeSign: Optional[str] = None
    northNodeHouse: Optional[int] = None
    southNodeSign: Optional[str] = None
    southNodeHouse: Optional[int] = None
    chironSign: Optional[str] = None
    chironHouse: Optional[int] = None
    midheavenSign: Optional[str] = None
    icSign: Optional[str] = None



class FullBirthChartResponse(BaseModel):
    """Response com seção do Mapa Astral Completo."""
    section: str
    title: str
    content: str
    generated_by: str
