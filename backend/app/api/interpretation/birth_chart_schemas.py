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


def merge_calculated_data(calculated_chart, request):
    """Cópia do pedido com os dados calculados pela biblioteca no lugar dos enviados pelo cliente."""
    return FullBirthChartRequest(
            name=request.name,
            birthDate=request.birthDate,
            birthTime=request.birthTime,
            birthPlace=request.birthPlace,
            sunSign=calculated_chart.get('sun_sign', request.sunSign),
            moonSign=calculated_chart.get('moon_sign', request.moonSign),
            ascendant=calculated_chart.get('ascendant_sign', request.ascendant),
            sunHouse=calculated_chart.get('sun_house', request.sunHouse),
            moonHouse=calculated_chart.get('moon_house', request.moonHouse),
            section=request.section,
            language=request.language,
            mercurySign=calculated_chart.get('mercury_sign', request.mercurySign),
            mercuryHouse=calculated_chart.get('mercury_house', request.mercuryHouse),
            venusSign=calculated_chart.get('venus_sign', request.venusSign),
            venusHouse=calculated_chart.get('venus_house', request.venusHouse),
            marsSign=calculated_chart.get('mars_sign', request.marsSign),
            marsHouse=calculated_chart.get('mars_house', request.marsHouse),
            jupiterSign=calculated_chart.get('jupiter_sign', request.jupiterSign),
            jupiterHouse=calculated_chart.get('jupiter_house', request.jupiterHouse),
            saturnSign=calculated_chart.get('saturn_sign', request.saturnSign),
            saturnHouse=calculated_chart.get('saturn_house', request.saturnHouse),
            uranusSign=calculated_chart.get('uranus_sign', request.uranusSign),
            uranusHouse=calculated_chart.get('uranus_house', request.uranusHouse),
            neptuneSign=calculated_chart.get('neptune_sign', request.neptuneSign),
            neptuneHouse=calculated_chart.get('neptune_house', request.neptuneHouse),
            plutoSign=calculated_chart.get('pluto_sign', request.plutoSign),
            plutoHouse=calculated_chart.get('pluto_house', request.plutoHouse),
            northNodeSign=calculated_chart.get('north_node_sign', request.northNodeSign),
            northNodeHouse=calculated_chart.get('north_node_house', request.northNodeHouse),
            southNodeSign=calculated_chart.get('south_node_sign', request.southNodeSign),
            southNodeHouse=calculated_chart.get('south_node_house', request.southNodeHouse),
            chironSign=calculated_chart.get('chiron_sign', request.chironSign),
            chironHouse=calculated_chart.get('chiron_house', request.chironHouse),
            midheavenSign=calculated_chart.get('midheaven_sign', request.midheavenSign),
            icSign=calculated_chart.get('ic_sign', request.icSign),
        )
