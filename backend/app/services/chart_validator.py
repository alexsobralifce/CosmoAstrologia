"""
Módulo de Validação de Mapas Astrais.
Garante que NADA seja descrito sem cálculos realizados.

TRAVAS DE SEGURANÇA:
1. Valida que todas as posições planetárias foram calculadas
2. Valida que todas as casas foram calculadas
3. Valida que o temperamento foi calculado corretamente
4. Impede geração de relatórios com dados inválidos
"""
from typing import Dict, List, Any, Optional, Tuple
from app.services.swiss_ephemeris_calculator import (
    calculate_birth_chart,
    create_kr_instance,
    get_planet_house,
    get_planet_position
)
from app.services.precomputed_chart_engine import (
    calculate_temperament_from_chart,
    get_chart_ruler,
    SIGN_TO_ELEMENT
)


class ChartValidationError(Exception):
    """Exceção lançada quando validação do mapa falha."""
    pass


def validate_chart_data(chart_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Valida que todos os dados necessários do mapa estão presentes e corretos.
    
    Args:
        chart_data: Dados do mapa astral
    
    Returns:
        Tuple (is_valid, errors): True se válido, lista de erros se inválido
    """
    errors = []
    
    # Validar planetas principais
    required_planets = [
        'sun_sign', 'moon_sign', 'mercury_sign', 'venus_sign', 'mars_sign',
        'jupiter_sign', 'saturn_sign', 'uranus_sign', 'neptune_sign', 'pluto_sign'
    ]
    
    for planet_key in required_planets:
        if planet_key not in chart_data or not chart_data[planet_key]:
            errors.append(f"Planeta {planet_key} não calculado")
    
    # Validar Ascendente e MC
    if 'ascendant_sign' not in chart_data or not chart_data['ascendant_sign']:
        errors.append("Ascendente não calculado")
    
    if 'midheaven_sign' not in chart_data or not chart_data['midheaven_sign']:
        errors.append("Meio do Céu não calculado")
    
    # Validar Nodos
    if 'north_node_sign' not in chart_data or not chart_data['north_node_sign']:
        errors.append("Nodo Norte não calculado")
    
    if 'south_node_sign' not in chart_data or not chart_data['south_node_sign']:
        errors.append("Nodo Sul não calculado")
    
    # Validar Quíron
    if 'chiron_sign' not in chart_data or not chart_data['chiron_sign']:
        errors.append("Quíron não calculado")
    
    # Validar que signos são válidos
    valid_signs = [
        'Áries', 'Touro', 'Gêmeos', 'Câncer', 'Leão', 'Virgem',
        'Libra', 'Escorpião', 'Sagitário', 'Capricórnio', 'Aquário', 'Peixes'
    ]
    
    for planet_key in required_planets:
        sign = chart_data.get(planet_key)
        if sign and sign not in valid_signs:
            errors.append(f"Signo inválido para {planet_key}: {sign}")
    
    return (len(errors) == 0, errors)


def validate_temperament_calculation(chart_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
    """
    Valida que o temperamento foi calculado corretamente.
    
    Args:
        chart_data: Dados do mapa astral
    
    Returns:
        Tuple (is_valid, temperament_data, errors)
    """
    errors = []
    
    try:
        temperament = calculate_temperament_from_chart(chart_data, 'pt')
        
        # Validar que o cálculo está correto
        # Deve contar apenas os 10 planetas principais (Sol, Lua, Ascendente = 3 pts cada, outros = 1 pt)
        # Planetas secundários: Mercúrio, Vênus, Marte, Júpiter, Saturno, Urano, Netuno, Plutão = 8 planetas
        expected_total = 3 + 3 + 3 + 8  # Sol + Lua + Asc + 8 planetas = 17 pontos
        
        if temperament['total_points'] != expected_total:
            errors.append(
                f"Temperamento calculado incorretamente: "
                f"total={temperament['total_points']}, esperado={expected_total}"
            )
        
        # Validar que elementos são válidos
        valid_elements = ['Fogo', 'Terra', 'Ar', 'Água']
        for element in temperament['points'].keys():
            if element not in valid_elements:
                errors.append(f"Elemento inválido no temperamento: {element}")
        
        return (len(errors) == 0, temperament, errors)
    
    except Exception as e:
        errors.append(f"Erro ao calcular temperamento: {str(e)}")
        return (False, {}, errors)


def validate_planet_houses(
    chart_data: Dict[str, Any],
    birth_date,
    birth_time: str,
    latitude: float,
    longitude: float
) -> Tuple[bool, Dict[str, int], List[str]]:
    """
    Valida que todas as casas dos planetas foram calculadas corretamente.
    
    Args:
        chart_data: Dados do mapa astral
        birth_date: Data de nascimento
        birth_time: Hora de nascimento
        latitude: Latitude
        longitude: Longitude
    
    Returns:
        Tuple (is_valid, houses_dict, errors)
    """
    errors = []
    houses = {}
    
    try:
        # Criar instância kerykeion para calcular casas
        kr = create_kr_instance(birth_date, birth_time, latitude, longitude)
        
        # Calcular casa de cada planeta
        planets = [
            'sun', 'moon', 'mercury', 'venus', 'mars',
            'jupiter', 'saturn', 'uranus', 'neptune', 'pluto'
        ]
        
        for planet in planets:
            try:
                house = get_planet_house(kr, planet)
                if house < 1 or house > 12:
                    errors.append(f"Casa inválida para {planet}: {house}")
                else:
                    houses[planet] = house
            except Exception as e:
                errors.append(f"Erro ao calcular casa de {planet}: {str(e)}")
        
        # Validar Ascendente (sempre casa 1)
        asc_house = get_planet_house(kr, 'ascendant') if hasattr(kr, 'ascendant') else 1
        if asc_house != 1:
            errors.append(f"Ascendente deve estar na casa 1, mas está na casa {asc_house}")
        
        return (len(errors) == 0, houses, errors)
    
    except Exception as e:
        errors.append(f"Erro ao calcular casas: {str(e)}")
        return (False, {}, errors)


def validate_chart_ruler(chart_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], List[str]]:
    """
    Valida que o regente do mapa foi identificado corretamente.
    
    Args:
        chart_data: Dados do mapa astral
    
    Returns:
        Tuple (is_valid, ruler_info, errors)
    """
    errors = []
    
    try:
        ascendant = chart_data.get('ascendant_sign')
        if not ascendant:
            errors.append("Ascendente não encontrado para calcular regente")
            return (False, {}, errors)
        
        ruler_info = get_chart_ruler(ascendant, chart_data)
        
        # Validar que o regente foi encontrado
        if 'error' in ruler_info:
            errors.append(f"Erro ao identificar regente: {ruler_info['error']}")
            return (False, ruler_info, errors)
        
        # Validar que o regente não é Quíron (não é regente de nenhum signo)
        if ruler_info.get('planet') == 'Quíron' or ruler_info.get('planet') == 'Chiron':
            errors.append("Quíron não pode ser regente do mapa")
        
        return (True, ruler_info, errors)
    
    except Exception as e:
        errors.append(f"Erro ao validar regente: {str(e)}")
        return (False, {}, errors)


def validate_complete_chart(
    birth_date,
    birth_time: str,
    latitude: float,
    longitude: float,
    timezone_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Valida e recalcula o mapa astral completo, garantindo que todos os dados estão corretos.
    
    Args:
        birth_date: Data de nascimento
        birth_time: Hora de nascimento
        latitude: Latitude
        longitude: Longitude
        timezone_name: Timezone (opcional)
    
    Returns:
        Dicionário com dados validados e calculados
    
    Raises:
        ChartValidationError: Se validação falhar
    """
    # 1. Recalcular mapa completo usando Swiss Ephemeris
    chart_data = calculate_birth_chart(
        birth_date=birth_date,
        birth_time=birth_time,
        latitude=latitude,
        longitude=longitude,
        timezone_name=timezone_name
    )
    
    # 2. Validar dados básicos
    is_valid, errors = validate_chart_data(chart_data)
    if not is_valid:
        raise ChartValidationError(f"Dados do mapa inválidos: {', '.join(errors)}")
    
    # 3. Validar e calcular temperamento
    temp_valid, temperament, temp_errors = validate_temperament_calculation(chart_data)
    if not temp_valid:
        raise ChartValidationError(f"Erro no cálculo do temperamento: {', '.join(temp_errors)}")
    
    # 4. Validar e calcular casas
    houses_valid, houses, house_errors = validate_planet_houses(
        chart_data, birth_date, birth_time, latitude, longitude
    )
    if not houses_valid:
        raise ChartValidationError(f"Erro no cálculo das casas: {', '.join(house_errors)}")
    
    # 5. Validar regente
    ruler_valid, ruler_info, ruler_errors = validate_chart_ruler(chart_data)
    if not ruler_valid:
        raise ChartValidationError(f"Erro na identificação do regente: {', '.join(ruler_errors)}")
    
    # 6. Adicionar casas ao chart_data
    planet_key_map = {
        'sun': 'sun_house',
        'moon': 'moon_house',
        'mercury': 'mercury_house',
        'venus': 'venus_house',
        'mars': 'mars_house',
        'jupiter': 'jupiter_house',
        'saturn': 'saturn_house',
        'uranus': 'uranus_house',
        'neptune': 'neptune_house',
        'pluto': 'pluto_house',
    }
    
    for planet, house in houses.items():
        key = planet_key_map.get(planet)
        if key:
            chart_data[key] = house
    
    # 7. Adicionar temperamento validado
    chart_data['_validated_temperament'] = temperament
    
    # 8. Adicionar regente validado
    chart_data['_validated_ruler'] = ruler_info
    
    # 9. Marcar como validado
    chart_data['_validated'] = True
    chart_data['_validation_errors'] = []
    
    return chart_data


def ensure_chart_validated(chart_data: Dict[str, Any]) -> bool:
    """
    Verifica se o mapa foi validado. Se não foi, lança exceção.
    
    Args:
        chart_data: Dados do mapa astral
    
    Returns:
        True se validado
    
    Raises:
        ChartValidationError: Se não foi validado
    """
    if not chart_data.get('_validated', False):
        raise ChartValidationError(
            "Mapa não foi validado. Use validate_complete_chart() antes de gerar relatórios."
        )
    
    return True

