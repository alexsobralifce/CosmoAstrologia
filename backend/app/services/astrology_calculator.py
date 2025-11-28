import ephem
from datetime import datetime
from typing import Dict, Optional, List


# Mapeamento de signos em português
ZODIAC_SIGNS = [
    "Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem",
    "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes"
]

PLANET_DISPLAY_NAMES = {
    "sun": "Sol",
    "moon": "Lua",
    "mercury": "Mercúrio",
    "venus": "Vênus",
    "mars": "Marte",
    "jupiter": "Júpiter",
    "saturn": "Saturno",
    "uranus": "Urano",
    "neptune": "Netuno",
    "pluto": "Plutão",
}

MIDHEAVEN_CONJUNCTION_ORB = 5.0  # graus de orbe para conjunções com o MC

# Períodos orbitais dos planetas em anos terrestres
# Usado para calcular retornos planetários e ciclos críticos
PERIODOS_ORBITAIS = {
    'Saturno': 29.5,   # anos - Retorno de Saturno ~28-30 anos
    'Júpiter': 11.86,  # anos - Retorno de Júpiter ~12 anos
    'Urano': 84.0,     # anos - Oposição de Urano ~42 anos (84/2)
    'Netuno': 164.8,   # anos - Ciclo geracional muito longo
    'Plutão': 248.0    # anos - Ciclo geracional extremamente longo
}


def get_zodiac_sign(longitude: float) -> Dict[str, any]:
    """Converte longitude eclíptica em signo e grau."""
    normalized = longitude % 360
    if normalized < 0:
        normalized += 360
    
    sign_index = int(normalized / 30)
    degree = normalized % 30
    
    return {
        "sign": ZODIAC_SIGNS[sign_index],
        "degree": degree
    }


def shortest_angular_distance(angle1: float, angle2: float) -> float:
    """
    Retorna a menor distância angular absoluta entre dois ângulos (em graus).
    Resultado sempre no intervalo [0, 180].
    """
    diff = (angle1 - angle2 + 180) % 360 - 180
    return abs(diff)


def calculate_planet_position(observer: ephem.Observer, planet_name: str) -> float:
    """Calcula a posição de um planeta em longitude eclíptica."""
    import math
    
    # Criar objeto do planeta
    planet_map = {
        "sun": ephem.Sun(),
        "moon": ephem.Moon(),
        "mercury": ephem.Mercury(),
        "venus": ephem.Venus(),
        "mars": ephem.Mars(),
        "jupiter": ephem.Jupiter(),
        "saturn": ephem.Saturn(),
        "uranus": ephem.Uranus(),
        "neptune": ephem.Neptune(),
        "pluto": ephem.Pluto(),
    }
    
    if planet_name.lower() not in planet_map:
        raise ValueError(f"Planeta desconhecido: {planet_name}")
    
    planet = planet_map[planet_name.lower()]
    planet.compute(observer)
    
    # PyEphem fornece ra e dec em radianos
    ra_rad = float(planet.ra)
    dec_rad = float(planet.dec)
    
    # Obter obliquidade da eclíptica
    jd = ephem.julian_date(observer.date)
    T = (jd - 2451545.0) / 36525.0
    # Fórmula de obliquidade da eclíptica (em radianos)
    obliquity_rad = math.radians(23.439291 - 0.0130042 * T - 1.64e-7 * T * T + 5.04e-7 * T * T * T)
    
    # Converter RA/Dec para longitude eclíptica
    # Fórmula correta: tan(lambda) = (sin(RA) * cos(obliquity) + tan(Dec) * sin(obliquity)) / cos(RA)
    # Ou: lambda = atan2(sin(RA) * cos(obliquity) + tan(Dec) * sin(obliquity), cos(RA))
    
    sin_ra = math.sin(ra_rad)
    cos_ra = math.cos(ra_rad)
    tan_dec = math.tan(dec_rad)
    sin_obl = math.sin(obliquity_rad)
    cos_obl = math.cos(obliquity_rad)
    
    # Longitude eclíptica
    numerator = sin_ra * cos_obl + tan_dec * sin_obl
    denominator = cos_ra
    
    lon_rad = math.atan2(numerator, denominator)
    longitude = math.degrees(lon_rad)
    
    # Normalizar para 0-360
    if longitude < 0:
        longitude += 360
    
    return longitude


def calculate_ascendant(observer: ephem.Observer) -> float:
    """Calcula o ascendente em longitude eclíptica."""
    import math
    
    # Calcular Local Sidereal Time (LST) - PyEphem retorna em radianos
    lst_rad = float(observer.sidereal_time())
    
    # Latitude do observador em radianos
    lat_rad = float(observer.lat)
    
    # Obter obliquidade da eclíptica
    jd = ephem.julian_date(observer.date)
    T = (jd - 2451545.0) / 36525.0
    # Fórmula de obliquidade da eclíptica (em radianos)
    obliquity_rad = math.radians(23.439291 - 0.0130042 * T - 1.64e-7 * T * T + 5.04e-7 * T * T * T)
    
    # Calcular ascendente usando fórmula astronômica correta
    # A fórmula correta é: Ascendente = atan2(cos(LST), sin(LST) * cos(obliquity) + tan(lat) * sin(obliquity))
    # Mas há uma variação: precisamos calcular a interseção do horizonte com a eclíptica
    
    sin_lst = math.sin(lst_rad)
    cos_lst = math.cos(lst_rad)
    sin_obl = math.sin(obliquity_rad)
    cos_obl = math.cos(obliquity_rad)
    tan_lat = math.tan(lat_rad)
    
    # Fórmula correta para o ascendente
    # O ascendente é a longitude eclíptica do ponto que está no horizonte leste
    # A fórmula correta é: ASC = atan2(cos(LST), -(sin(LST) * cos(obliquity) + tan(lat) * sin(obliquity)))
    # Esta fórmula dá resultados mais precisos para latitudes do hemisfério sul
    
    numerator = cos_lst
    denominator = -(sin_lst * cos_obl + tan_lat * sin_obl)
    
    asc_rad = math.atan2(numerator, denominator)
    asc_deg = math.degrees(asc_rad)
    
    # Normalizar para 0-360
    if asc_deg < 0:
        asc_deg += 360
    
    return asc_deg


def calculate_midheaven(observer: ephem.Observer) -> float:
    """Calcula o Meio do Céu (MC) em longitude eclíptica."""
    import math

    lst_rad = float(observer.sidereal_time())

    jd = ephem.julian_date(observer.date)
    T = (jd - 2451545.0) / 36525.0
    obliquity_rad = math.radians(23.439291 - 0.0130042 * T - 1.64e-7 * T * T + 5.04e-7 * T * T * T)

    numerator = math.sin(lst_rad) * math.cos(obliquity_rad)
    denominator = math.cos(lst_rad)

    mc_rad = math.atan2(numerator, denominator)
    mc_deg = math.degrees(mc_rad)

    if mc_deg < 0:
        mc_deg += 360

    return mc_deg


def calculate_chiron(observer: ephem.Observer) -> float:
    """
    Calcula a posição de Quíron usando elementos orbitais.
    
    Quíron é um centauro (corpo menor) descoberto em 1977, conhecido como
    "a ferida do curador" na astrologia. Sua órbita está entre Saturno e Urano.
    
    Elementos orbitais de Quíron (Epoch J2000):
    - Período orbital: ~50.76 anos
    - Semi-eixo maior: 13.65 UA
    - Excentricidade: 0.3786
    - Inclinação: 6.93°
    """
    import math
    
    # Data juliana
    jd = ephem.julian_date(observer.date)
    
    # Dias desde J2000.0 (1 Jan 2000, 12:00 UT)
    days_since_j2000 = jd - 2451545.0
    
    # Elementos orbitais de Quíron (simplificados para cálculo)
    # Longitude média no epoch J2000.0 (em graus) - Quíron estava em ~102° (Câncer/Leão)
    L0 = 102.5
    
    # Movimento médio diário (graus/dia)
    # Período orbital de Quíron ≈ 50.76 anos ≈ 18537 dias
    n = 360.0 / (50.76 * 365.25)  # ≈ 0.01942°/dia
    
    # Longitude média atual
    mean_longitude = (L0 + n * days_since_j2000) % 360
    
    # Elementos para a equação do centro
    e = 0.3786  # Excentricidade
    omega = 339.56  # Longitude do perihélio (graus)
    
    # Anomalia média
    M = mean_longitude - omega
    M_rad = math.radians(M)
    
    # Equação do centro (aproximação para excentricidade moderada)
    C = (2 * e - 0.25 * e**3) * math.sin(M_rad) + \
        1.25 * e**2 * math.sin(2 * M_rad) + \
        (13/12) * e**3 * math.sin(3 * M_rad)
    C_deg = math.degrees(C)
    
    # Longitude verdadeira
    true_longitude = (mean_longitude + C_deg) % 360
    
    if true_longitude < 0:
        true_longitude += 360
    
    return true_longitude


def calculate_lunar_nodes(observer: ephem.Observer) -> Dict[str, float]:
    """
    Calcula os Nodos Lunares (Norte e Sul) em longitude eclíptica.
    O Nodo Norte (Cabeça do Dragão) é onde a Lua cruza a eclíptica para o norte.
    O Nodo Sul (Cauda do Dragão) é exatamente oposto (180°).
    """
    import math
    
    # Calcular a posição da Lua
    moon = ephem.Moon()
    moon.compute(observer)
    
    # Obter a longitude do nodo ascendente da Lua
    # PyEphem fornece isso através de moon.hlat (heliocentric lat) e cálculos
    
    # Usar a data juliana para calcular o nodo médio
    jd = ephem.julian_date(observer.date)
    
    # Fórmula para o Nodo Lunar Médio (Mean Node)
    # Baseado em fórmulas astronômicas padrão
    T = (jd - 2451545.0) / 36525.0  # Séculos desde J2000
    
    # Longitude do Nodo Norte Médio (em graus)
    # Fórmula de Meeus (Astronomical Algorithms)
    omega = 125.04452 - 1934.136261 * T + 0.0020708 * T * T + T * T * T / 450000.0
    
    # Normalizar para 0-360
    north_node = omega % 360
    if north_node < 0:
        north_node += 360
    
    # Nodo Sul é exatamente oposto
    south_node = (north_node + 180) % 360
    
    return {
        "north_node": north_node,
        "south_node": south_node
    }


def calculate_birth_chart(
    birth_date: datetime,
    birth_time: str,
    latitude: float,
    longitude: float
) -> Dict[str, any]:
    """
    Calcula o mapa astral completo.
    
    Args:
        birth_date: Data de nascimento
        birth_time: Hora de nascimento no formato "HH:MM" (hora local do local de nascimento)
        latitude: Latitude do local de nascimento
        longitude: Longitude do local de nascimento (positivo para leste, negativo para oeste)
    
    Returns:
        Dicionário com signos e graus calculados
    """
    # Combinar data e hora
    time_parts = birth_time.split(":")
    hour = int(time_parts[0]) if len(time_parts) > 0 else 0
    minute = int(time_parts[1]) if len(time_parts) > 1 else 0
    
    # IMPORTANTE: PyEphem espera hora em UTC
    # Calcular fuso horário aproximado baseado na longitude
    # Longitude em graus: cada 15° = 1 hora de diferença
    # Brasil está aproximadamente em UTC-3 (longitude ~-45°)
    # Para cálculos mais precisos, seria necessário usar uma biblioteca de timezone
    # Por enquanto, usamos aproximação: longitude negativa (oeste) = UTC negativo
    utc_offset_hours = round(longitude / 15.0)
    # Limitar a faixa razoável de fusos horários (-12 a +14)
    utc_offset_hours = max(-12, min(14, utc_offset_hours))
    
    # Converter hora local para UTC
    utc_hour = hour - utc_offset_hours
    
    # Ajustar dia se necessário
    adjusted_date = birth_date
    if utc_hour < 0:
        utc_hour += 24
        from datetime import timedelta
        adjusted_date = birth_date - timedelta(days=1)
    elif utc_hour >= 24:
        utc_hour -= 24
        from datetime import timedelta
        adjusted_date = birth_date + timedelta(days=1)
    
    combined_datetime = adjusted_date.replace(hour=utc_hour, minute=minute, second=0, microsecond=0)
    
    # Criar observador (local de nascimento)
    observer = ephem.Observer()
    observer.lat = str(latitude)
    observer.lon = str(longitude)
    # PyEphem espera datetime em UTC
    observer.date = combined_datetime.strftime('%Y/%m/%d %H:%M:%S')
    
    # Calcular posições dos corpos celestes principais
    sun_longitude = calculate_planet_position(observer, "sun")
    moon_longitude = calculate_planet_position(observer, "moon")
    ascendant_longitude = calculate_ascendant(observer)
    midheaven_longitude = calculate_midheaven(observer)
    
    # Calcular posições dos planetas principais (para determinar regente do mapa)
    mercury_longitude = calculate_planet_position(observer, "mercury")
    venus_longitude = calculate_planet_position(observer, "venus")
    mars_longitude = calculate_planet_position(observer, "mars")
    jupiter_longitude = calculate_planet_position(observer, "jupiter")
    saturn_longitude = calculate_planet_position(observer, "saturn")
    uranus_longitude = calculate_planet_position(observer, "uranus")
    neptune_longitude = calculate_planet_position(observer, "neptune")
    pluto_longitude = calculate_planet_position(observer, "pluto")

    planet_longitudes = {
        PLANET_DISPLAY_NAMES["sun"]: sun_longitude,
        PLANET_DISPLAY_NAMES["moon"]: moon_longitude,
        PLANET_DISPLAY_NAMES["mercury"]: mercury_longitude,
        PLANET_DISPLAY_NAMES["venus"]: venus_longitude,
        PLANET_DISPLAY_NAMES["mars"]: mars_longitude,
        PLANET_DISPLAY_NAMES["jupiter"]: jupiter_longitude,
        PLANET_DISPLAY_NAMES["saturn"]: saturn_longitude,
        PLANET_DISPLAY_NAMES["uranus"]: uranus_longitude,
        PLANET_DISPLAY_NAMES["neptune"]: neptune_longitude,
        PLANET_DISPLAY_NAMES["pluto"]: pluto_longitude,
    }
    
    # Obter signos
    sun_data = get_zodiac_sign(sun_longitude)
    moon_data = get_zodiac_sign(moon_longitude)
    ascendant_data = get_zodiac_sign(ascendant_longitude)
    midheaven_data = get_zodiac_sign(midheaven_longitude)

    planets_conjunct_midheaven: List[str] = [
        name for name, longitude in planet_longitudes.items()
        if shortest_angular_distance(longitude, midheaven_longitude) <= MIDHEAVEN_CONJUNCTION_ORB
    ]
    mercury_data = get_zodiac_sign(mercury_longitude)
    venus_data = get_zodiac_sign(venus_longitude)
    mars_data = get_zodiac_sign(mars_longitude)
    jupiter_data = get_zodiac_sign(jupiter_longitude)
    saturn_data = get_zodiac_sign(saturn_longitude)
    uranus_data = get_zodiac_sign(uranus_longitude)
    neptune_data = get_zodiac_sign(neptune_longitude)
    pluto_data = get_zodiac_sign(pluto_longitude)
    
    # Calcular nodos lunares
    lunar_nodes = calculate_lunar_nodes(observer)
    north_node_data = get_zodiac_sign(lunar_nodes["north_node"])
    south_node_data = get_zodiac_sign(lunar_nodes["south_node"])
    
    # Calcular Quíron (a ferida do curador)
    chiron_longitude = calculate_chiron(observer)
    chiron_data = get_zodiac_sign(chiron_longitude)
    
    return {
        "sun_sign": sun_data["sign"],
        "sun_degree": sun_data["degree"],
        "moon_sign": moon_data["sign"],
        "moon_degree": moon_data["degree"],
        "ascendant_sign": ascendant_data["sign"],
        "ascendant_degree": ascendant_data["degree"],
        # Planetas principais
        "mercury_sign": mercury_data["sign"],
        "mercury_degree": mercury_data["degree"],
        "venus_sign": venus_data["sign"],
        "venus_degree": venus_data["degree"],
        "mars_sign": mars_data["sign"],
        "mars_degree": mars_data["degree"],
        "jupiter_sign": jupiter_data["sign"],
        "jupiter_degree": jupiter_data["degree"],
        "saturn_sign": saturn_data["sign"],
        "saturn_degree": saturn_data["degree"],
        "uranus_sign": uranus_data["sign"],
        "uranus_degree": uranus_data["degree"],
        "neptune_sign": neptune_data["sign"],
        "neptune_degree": neptune_data["degree"],
        "pluto_sign": pluto_data["sign"],
        "pluto_degree": pluto_data["degree"],
        "midheaven_sign": midheaven_data["sign"],
        "midheaven_degree": midheaven_data["degree"],
        "planets_conjunct_midheaven": planets_conjunct_midheaven,
        "uranus_on_midheaven": PLANET_DISPLAY_NAMES["uranus"] in planets_conjunct_midheaven,
        # Nodos Lunares
        "north_node_sign": north_node_data["sign"],
        "north_node_degree": north_node_data["degree"],
        "south_node_sign": south_node_data["sign"],
        "south_node_degree": south_node_data["degree"],
        # Quíron (a ferida do curador)
        "chiron_sign": chiron_data["sign"],
        "chiron_degree": chiron_data["degree"],
    }

