from datetime import datetime
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Header
from fastapi import status
from pydantic import BaseModel
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

router = APIRouter()


class CompleteChartRequest(BaseModel):
    """Request para obter mapa astral completo no formato do PDF."""
    birth_date: str  # Formato: "DD/MM/YYYY"
    birth_time: str  # Formato: "HH:MM"
    latitude: float
    longitude: float
    birth_place: str
    name: str


class CompleteChartResponse(BaseModel):
    """Response com mapa astral completo no formato do PDF."""
    birth_data: Dict[str, Any]
    planets_in_signs: List[Dict[str, Any]]
    special_points: List[Dict[str, Any]]
    planets_in_houses: List[Dict[str, Any]]  # Lista de dicts com {house: int, planets: List}


def remove_duplicates_planets_in_signs(planets_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove planetas duplicados de planets_in_signs baseado em planet_key.
    Mantém apenas a primeira ocorrência de cada planeta.
    """
    seen = set()
    filtered = []
    for planet in planets_list:
        planet_key = planet.get("planet_key")
        if planet_key and planet_key not in seen:
            seen.add(planet_key)
            filtered.append(planet)
    return filtered


def remove_duplicates_special_points(points_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove pontos especiais duplicados baseado em point_key.
    Mantém apenas a primeira ocorrência de cada ponto.
    """
    seen = set()
    filtered = []
    for point in points_list:
        point_key = point.get("point_key")
        if point_key and point_key not in seen:
            seen.add(point_key)
            filtered.append(point)
    return filtered


def remove_duplicates_planets_in_houses(houses_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove planetas duplicados dentro de cada casa baseado em planet_key.
    Mantém apenas a primeira ocorrência de cada planeta por casa.
    """
    filtered_houses = []
    for house_data in houses_list:
        house_num = house_data.get("house")
        planets = house_data.get("planets", [])
        
        # Remover duplicados dentro desta casa
        seen = set()
        filtered_planets = []
        for planet in planets:
            # Usar planet_key ou planet como identificador único
            identifier = planet.get("planet_key") or planet.get("planet")
            if identifier and identifier not in seen:
                seen.add(identifier)
                filtered_planets.append(planet)
        
        filtered_houses.append({
            "house": house_num,
            "planets": filtered_planets
        })
    
    return filtered_houses


@router.post("/interpretation/complete-chart", response_model=CompleteChartResponse)
async def get_complete_chart(
    request: CompleteChartRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Retorna o mapa astral completo no formato do PDF.
    Todos os dados são calculados pela biblioteca local (Swiss Ephemeris via kerykeion).
    Nenhum dado é inventado ou alucinado - tudo é validado e calculado.
    
    GARANTIAS:
    - Todos os cálculos passam pelo Swiss Ephemeris (via kerykeion)
    - Dados são filtrados para não haver repetições
    - Cada planeta aparece apenas uma vez em planets_in_signs
    - Cada ponto especial aparece apenas uma vez em special_points
    - Cada planeta aparece apenas uma vez por casa em planets_in_houses
    """
    try:
        # Importação lazy para evitar lentidão na inicialização
        # GARANTIA: Usa apenas Swiss Ephemeris (via kerykeion)
        from app.services.swiss_ephemeris_calculator import calculate_complete_chart_with_houses
    
        # Converter data de nascimento
        birth_date = datetime.strptime(request.birth_date, "%d/%m/%Y")
        
        # Calcular mapa completo com casas usando Swiss Ephemeris
        # GARANTIA: calculate_complete_chart_with_houses usa kerykeion que usa Swiss Ephemeris
        complete_chart = calculate_complete_chart_with_houses(
            birth_date=birth_date,
            birth_time=request.birth_time,
            latitude=request.latitude,
            longitude=request.longitude,
            timezone_name=None  # Será inferido automaticamente
        )
        
        # FILTRO 1: Remover duplicações em planets_in_signs
        planets_in_signs_filtered = remove_duplicates_planets_in_signs(
            complete_chart.get("planets_in_signs", [])
        )
        
        # FILTRO 2: Remover duplicações em special_points
        special_points_filtered = remove_duplicates_special_points(
            complete_chart.get("special_points", [])
        )
        
        # Converter planets_in_houses de lista de tuplas para lista de dicts
        houses_list = []
        for house_num, planets_list in complete_chart.get("planets_in_houses", []):
            houses_list.append({
                "house": house_num,
                "planets": planets_list
            })
        
        # FILTRO 3: Remover duplicações em planets_in_houses
        houses_list_filtered = remove_duplicates_planets_in_houses(houses_list)
        
        # Log para debug (opcional)
        print(f"[COMPLETE CHART] Planetas únicos: {len(planets_in_signs_filtered)}")
        print(f"[COMPLETE CHART] Pontos especiais únicos: {len(special_points_filtered)}")
        print(f"[COMPLETE CHART] Casas processadas: {len(houses_list_filtered)}")
        
        return CompleteChartResponse(
            birth_data=complete_chart["birth_data"],
            planets_in_signs=planets_in_signs_filtered,
            special_points=special_points_filtered,
            planets_in_houses=houses_list_filtered
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato de data inválido. Use DD/MM/YYYY: {str(e)}"
        )
    except Exception as e:
        import traceback
        print(f"[ERROR] Erro ao calcular mapa completo: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao calcular mapa astral completo: {str(e)}"
        )
