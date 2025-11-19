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
    }

