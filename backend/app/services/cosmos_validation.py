"""
Módulo de Validação do Cosmos Astral Engine
Implementa as regras matemáticas de validação astronômica.
"""
from typing import Tuple, Optional
from app.services.astrology_calculator import shortest_angular_distance


# Limites astronômicos máximos (em graus)
MERCURY_SUN_MAX_DISTANCE = 28.0
VENUS_SUN_MAX_DISTANCE = 48.0
VENUS_MERCURY_MAX_DISTANCE = 76.0

# Orbes de aspectos (em graus)
ASPECT_ORBS = {
    'conjunction': 8.0,
    'sextile': 4.0,
    'square': 6.0,
    'trine': 8.0,
    'opposition': 8.0,
    'quincunx': 2.0,
}

# Ângulos ideais dos aspectos (em graus)
ASPECT_ANGLES = {
    'conjunction': 0.0,
    'sextile': 60.0,
    'square': 90.0,
    'trine': 120.0,
    'opposition': 180.0,
    'quincunx': 150.0,
}


def validate_mercury_sun_distance(mercury_longitude: float, sun_longitude: float) -> Tuple[bool, Optional[str]]:
    """
    Valida se a distância entre Mercúrio e Sol é astronomicamente possível.
    
    Args:
        mercury_longitude: Longitude eclíptica de Mercúrio (0-360°)
        sun_longitude: Longitude eclíptica do Sol (0-360°)
    
    Returns:
        Tuple[bool, Optional[str]]: (é_válido, tipo_aspecto_ou_None)
    
    Regra: Máximo 28° de distância.
    Permitido: Conjunção (0-10°) ou Sem Aspecto.
    Proibido: Quadratura, Trígono, Oposição, Sextil.
    """
    distance = shortest_angular_distance(mercury_longitude, sun_longitude)
    
    if distance > MERCURY_SUN_MAX_DISTANCE:
        return False, f"Distância de {distance:.1f}° viola limite máximo de {MERCURY_SUN_MAX_DISTANCE}°"
    
    # Conjunção válida (0-10°)
    if distance <= 10.0:
        return True, "conjunction"
    
    # Sem aspecto (entre 10° e 28°)
    return True, None


def validate_venus_sun_distance(venus_longitude: float, sun_longitude: float) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Valida se a distância entre Vênus e Sol é astronomicamente possível.
    
    Args:
        venus_longitude: Longitude eclíptica de Vênus (0-360°)
        sun_longitude: Longitude eclíptica do Sol (0-360°)
    
    Returns:
        Tuple[bool, Optional[str], Optional[str]]: (é_válido, tipo_aspecto_ou_None, erro_ou_None)
    
    Regra: Máximo 48° de distância.
    Permitido: Conjunção (0-10°), Semi-Sextil (30°), Semi-Quadratura (45°).
    Proibido: Sextil (60°), Quadratura (90°), Trígono (120°), Oposição (180°).
    """
    distance = shortest_angular_distance(venus_longitude, sun_longitude)
    
    if distance > VENUS_SUN_MAX_DISTANCE:
        return False, None, f"Distância de {distance:.1f}° viola limite máximo de {VENUS_SUN_MAX_DISTANCE}°"
    
    # Conjunção válida (0-10°)
    if distance <= 10.0:
        return True, "conjunction", None
    
    # Semi-Sextil válido (aproximadamente 30°)
    if 28.0 <= distance <= 32.0:
        return True, "semi-sextile", None
    
    # Semi-Quadratura válida (aproximadamente 45°)
    if 43.0 <= distance <= 47.0:
        return True, "semi-square", None
    
    # Verificar aspectos proibidos
    if 56.0 <= distance <= 64.0:  # Sextil
        return False, "sextile", "Sextil (60°) é proibido entre Vênus e Sol"
    
    if 84.0 <= distance <= 96.0:  # Quadratura
        return False, "square", "Quadratura (90°) é proibida entre Vênus e Sol"
    
    if 112.0 <= distance <= 128.0:  # Trígono
        return False, "trine", "Trígono (120°) é proibido entre Vênus e Sol"
    
    if 172.0 <= distance <= 188.0:  # Oposição
        return False, "opposition", "Oposição (180°) é proibida entre Vênus e Sol"
    
    # Sem aspecto (outras distâncias válidas)
    return True, None, None


def validate_venus_mercury_distance(venus_longitude: float, mercury_longitude: float) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Valida se a distância entre Vênus e Mercúrio é astronomicamente possível.
    
    Args:
        venus_longitude: Longitude eclíptica de Vênus (0-360°)
        mercury_longitude: Longitude eclíptica de Mercúrio (0-360°)
    
    Returns:
        Tuple[bool, Optional[str], Optional[str]]: (é_válido, tipo_aspecto_ou_None, erro_ou_None)
    
    Regra: Máximo 76° de distância.
    Permitido: Conjunção, Sextil.
    Proibido: Quadratura, Trígono, Oposição.
    """
    distance = shortest_angular_distance(venus_longitude, mercury_longitude)
    
    if distance > VENUS_MERCURY_MAX_DISTANCE:
        return False, None, f"Distância de {distance:.1f}° viola limite máximo de {VENUS_MERCURY_MAX_DISTANCE}°"
    
    # Conjunção válida (0-10°)
    if distance <= 10.0:
        return True, "conjunction", None
    
    # Sextil válido (56-64°)
    if 56.0 <= distance <= 64.0:
        return True, "sextile", None
    
    # Verificar aspectos proibidos
    if 84.0 <= distance <= 96.0:  # Quadratura
        return False, "square", "Quadratura (90°) é proibida entre Vênus e Mercúrio"
    
    if 112.0 <= distance <= 128.0:  # Trígono
        return False, "trine", "Trígono (120°) é proibido entre Vênus e Mercúrio"
    
    if 172.0 <= distance <= 188.0:  # Oposição
        return False, "opposition", "Oposição (180°) é proibida entre Vênus e Mercúrio"
    
    # Sem aspecto (outras distâncias válidas até 76°)
    return True, None, None


def validate_aspect(planet1_longitude: float, planet2_longitude: float, aspect_type: str) -> Tuple[bool, float, Optional[str]]:
    """
    Valida se um aspecto específico existe entre dois planetas.
    
    Args:
        planet1_longitude: Longitude eclíptica do primeiro planeta (0-360°)
        planet2_longitude: Longitude eclíptica do segundo planeta (0-360°)
        aspect_type: Tipo de aspecto ('conjunction', 'sextile', 'square', 'trine', 'opposition', 'quincunx')
    
    Returns:
        Tuple[bool, float, Optional[str]]: (é_válido, distância, erro_ou_None)
    """
    if aspect_type not in ASPECT_ANGLES:
        return False, 0.0, f"Tipo de aspecto inválido: {aspect_type}"
    
    distance = shortest_angular_distance(planet1_longitude, planet2_longitude)
    ideal_angle = ASPECT_ANGLES[aspect_type]
    orb = ASPECT_ORBS[aspect_type]
    
    # Calcular diferença do ângulo ideal
    angle_diff = abs(distance - ideal_angle)
    
    # Para conjunção e oposição, verificar também através de 360°
    if aspect_type in ['conjunction', 'opposition']:
        # Verificar se está próximo ao ângulo ideal através de 360°
        angle_diff_wrap = min(angle_diff, abs(360 - distance - ideal_angle))
        angle_diff = min(angle_diff, angle_diff_wrap)
    
    # Verificar se está dentro do orbe
    if angle_diff <= orb:
        return True, distance, None
    
    return False, distance, f"Distância de {distance:.1f}° não está dentro do orbe de {orb}° para {aspect_type}"


def calculate_temperament_points(planet_positions: dict) -> dict:
    """
    Calcula os pontos de temperamento por elemento.
    
    Args:
        planet_positions: Dicionário com posições planetárias
            Formato: {
                'sun': {'sign': 'Leão', 'element': 'Fire'},
                'moon': {'sign': 'Touro', 'element': 'Earth'},
                ...
            }
    
    Returns:
        Dict com contagem de pontos por elemento:
        {
            'fire': 5,
            'earth': 3,
            'air': 1,
            'water': 0
        }
    
    Regra: Sol/Lua/Ascendente = 3 pontos cada.
           Outros planetas = 1 ponto cada.
    """
    points = {
        'fire': 0,
        'earth': 0,
        'air': 0,
        'water': 0
    }
    
    # Mapeamento de signos para elementos
    sign_to_element = {
        'Áries': 'fire', 'Leão': 'fire', 'Sagitário': 'fire',
        'Touro': 'earth', 'Virgem': 'earth', 'Capricórnio': 'earth',
        'Gêmeos': 'air', 'Libra': 'air', 'Aquário': 'air',
        'Câncer': 'water', 'Escorpião': 'water', 'Peixes': 'water',
        # Inglês também
        'Aries': 'fire', 'Leo': 'fire', 'Sagittarius': 'fire',
        'Taurus': 'earth', 'Virgo': 'earth', 'Capricorn': 'earth',
        'Gemini': 'air', 'Libra': 'air', 'Aquarius': 'air',
        'Cancer': 'water', 'Scorpio': 'water', 'Pisces': 'water',
    }
    
    # Planetas que valem 3 pontos
    major_planets = ['sun', 'moon', 'ascendant']
    
    for planet_key, planet_data in planet_positions.items():
        if not isinstance(planet_data, dict):
            # Se não for dict, tentar como string (signo direto)
            sign = str(planet_data)
            element = sign_to_element.get(sign)
            if element:
                # Se for major planet, valer 3, senão 1
                if planet_key.lower() in [p.lower() for p in major_planets]:
                    points[element] += 3
                else:
                    points[element] += 1
            continue
        
        # Tentar obter signo do dict
        sign = planet_data.get('sign', '') or planet_data.get('element', '')
        element = sign_to_element.get(sign)
        
        # Se não encontrou pelo signo, tentar pelo elemento direto
        if not element:
            element_key = planet_data.get('element', '').lower()
            if element_key in points:
                element = element_key
        
        if not element:
            continue
        
        # Determinar pontuação
        if planet_key.lower() in [p.lower() for p in major_planets]:
            points[element] += 3
        else:
            points[element] += 1
    
    return points


def validate_temperament_interpretation(planet_positions: dict, interpretation: str) -> Tuple[bool, Optional[str]]:
    """
    Valida se uma interpretação de temperamento está correta.
    
    Args:
        planet_positions: Dicionário com posições planetárias
        interpretation: Texto da interpretação
    
    Returns:
        Tuple[bool, Optional[str]]: (é_válido, erro_ou_None)
    
    Regra: Se um elemento tem planetas, NÃO pode ser dito "ausente" ou "ponto cego".
    """
    points = calculate_temperament_points(planet_positions)
    
    interpretation_lower = interpretation.lower()
    
    # Verificar cada elemento
    element_names = {
        'fire': ['fogo', 'fire'],
        'earth': ['terra', 'earth'],
        'air': ['ar', 'air'],
        'water': ['água', 'water', 'agua']
    }
    
    errors = []
    
    for element, names in element_names.items():
        element_points = points[element]
        
        # Se tem pontos, verificar se não está sendo dito ausente
        if element_points > 0:
            for name in names:
                # Verificar frases que indicam ausência
                if name in interpretation_lower:
                    import re
                    # Padrões que indicam ausência (mais flexíveis)
                    absent_patterns = [
                        rf'\b{re.escape(name)}\s+(está|é|ser)\s+ausente',  # "fogo está ausente"
                        rf'{re.escape(name)}\s+ausente',  # "fogo ausente"
                        rf'ausente.*?{re.escape(name)}',  # "ausente...fogo"
                        rf'ausência\s+de\s+{re.escape(name)}',  # "ausência de fogo"
                        rf'falta\s+de\s+{re.escape(name)}',  # "falta de fogo"
                        rf'sem\s+{re.escape(name)}',  # "sem fogo"
                        rf'{re.escape(name)}\s+ponto\s+cego',  # "fogo ponto cego"
                        rf'ponto\s+cego\s+{re.escape(name)}',  # "ponto cego fogo"
                        rf'blind\s+spot\s+{re.escape(name)}',  # "blind spot fogo"
                    ]
                    
                    for pattern in absent_patterns:
                        if re.search(pattern, interpretation_lower):
                            errors.append(
                                f"Elemento {element} tem {element_points} pontos, mas interpretação diz que está ausente"
                            )
                            break  # Encontrou erro, não precisa verificar mais padrões
    
    if errors:
        return False, "; ".join(errors)
    
    return True, None

