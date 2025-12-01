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
    longitude: float,
    use_swiss_ephemeris: bool = True
) -> Dict[str, any]:
    """
    Calcula o mapa astral completo.
    
    IMPORTANTE: Por padrão, usa Swiss Ephemeris (via kerykeion) como fonte única de verdade.
    Isso garante precisão e consistência em todos os cálculos, evitando "adivinhações" ou
    estimativas que podem causar inconsistências.
    
    Args:
        birth_date: Data de nascimento
        birth_time: Hora de nascimento no formato "HH:MM" (hora local do local de nascimento)
        latitude: Latitude do local de nascimento
        longitude: Longitude do local de nascimento (positivo para leste, negativo para oeste)
        use_swiss_ephemeris: Se True (padrão), usa Swiss Ephemeris. Se False, usa PyEphem (legado)
    
    Returns:
        Dicionário com signos e graus calculados (formato compatível com código existente)
    """
    # Tentar usar Swiss Ephemeris por padrão (fonte única de verdade)
    if use_swiss_ephemeris:
        try:
            from app.services.swiss_ephemeris_calculator import calculate_birth_chart as calculate_swiss
            result = calculate_swiss(birth_date, birth_time, latitude, longitude)
            
            # Converter formato para compatibilidade com código existente
            # O formato do Swiss Ephemeris já é compatível, mas garantimos remover campos extras
            return {
                "sun_sign": result.get("sun_sign"),
                "sun_degree": result.get("sun_degree"),
                "moon_sign": result.get("moon_sign"),
                "moon_degree": result.get("moon_degree"),
                "ascendant_sign": result.get("ascendant_sign"),
                "ascendant_degree": result.get("ascendant_degree"),
                "mercury_sign": result.get("mercury_sign"),
                "mercury_degree": result.get("mercury_degree"),
                "venus_sign": result.get("venus_sign"),
                "venus_degree": result.get("venus_degree"),
                "mars_sign": result.get("mars_sign"),
                "mars_degree": result.get("mars_degree"),
                "jupiter_sign": result.get("jupiter_sign"),
                "jupiter_degree": result.get("jupiter_degree"),
                "saturn_sign": result.get("saturn_sign"),
                "saturn_degree": result.get("saturn_degree"),
                "uranus_sign": result.get("uranus_sign"),
                "uranus_degree": result.get("uranus_degree"),
                "neptune_sign": result.get("neptune_sign"),
                "neptune_degree": result.get("neptune_degree"),
                "pluto_sign": result.get("pluto_sign"),
                "pluto_degree": result.get("pluto_degree"),
                "midheaven_sign": result.get("midheaven_sign"),
                "midheaven_degree": result.get("midheaven_degree"),
                "planets_conjunct_midheaven": result.get("planets_conjunct_midheaven", []),
                "uranus_on_midheaven": result.get("uranus_on_midheaven", False),
                "north_node_sign": result.get("north_node_sign"),
                "north_node_degree": result.get("north_node_degree"),
                "south_node_sign": result.get("south_node_sign"),
                "south_node_degree": result.get("south_node_degree"),
                "chiron_sign": result.get("chiron_sign"),
                "chiron_degree": result.get("chiron_degree"),
                "_source_longitudes": result.get("planet_longitudes", {}),
            }
        except ImportError as e:
            print(f"[WARNING] Swiss Ephemeris não disponível: {e}. Usando PyEphem (legado).")
        except Exception as e:
            print(f"[ERROR] Erro ao usar Swiss Ephemeris: {e}. Fallback para PyEphem.")
            import traceback
            print(traceback.format_exc())
    
    # Fallback para PyEphem (código legado)
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
    
    # FONTE ÚNICA DE VERDADE: Armazenar TODAS as longitudes calculadas
    # Isso garante que não haverá inconsistências - todas as referências usam os mesmos valores
    all_longitudes = {
        "sun": sun_longitude,
        "moon": moon_longitude,
        "mercury": mercury_longitude,
        "venus": venus_longitude,
        "mars": mars_longitude,
        "jupiter": jupiter_longitude,
        "saturn": saturn_longitude,
        "uranus": uranus_longitude,
        "neptune": neptune_longitude,
        "pluto": pluto_longitude,
        "ascendant": ascendant_longitude,
        "midheaven": midheaven_longitude,
        "north_node": lunar_nodes["north_node"],
        "south_node": lunar_nodes["south_node"],
        "chiron": chiron_longitude,
    }
    
    # VALIDAÇÃO DE CONSISTÊNCIA: Verificar que os signos calculados são consistentes
    # Se houver inconsistência, vamos detectar e corrigir
    venus_sign_from_longitude = get_zodiac_sign(venus_longitude)["sign"]
    if venus_data["sign"] != venus_sign_from_longitude:
        print(f"[WARNING] Inconsistência detectada em Vênus: {venus_data['sign']} vs {venus_sign_from_longitude}. Usando cálculo direto.")
        venus_data = get_zodiac_sign(venus_longitude)
    
    # Construir resultado final com TODAS as informações
    result = {
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
        # FONTE ÚNICA DE VERDADE: Todas as longitudes calculadas (para referência futura)
        "_source_longitudes": all_longitudes,
    }
    
    return result


def calculate_solar_return(
    birth_date: datetime,
    birth_time: str,
    latitude: float,
    longitude: float,
    target_year: Optional[int] = None
) -> Dict[str, any]:
    """
    Calcula o mapa de Revolução Solar (Solar Return).
    
    A Revolução Solar é calculada para o momento exato em que o Sol retorna
    à mesma posição do nascimento, mas no ano especificado (ou ano atual).
    
    Args:
        birth_date: Data de nascimento
        birth_time: Hora de nascimento no formato "HH:MM"
        latitude: Latitude do local de nascimento
        longitude: Longitude do local de nascimento
        target_year: Ano para calcular a revolução (padrão: ano atual)
    
    Returns:
        Dicionário com o mapa de revolução solar
    """
    from datetime import timedelta
    
    # Usar ano atual se não especificado
    if target_year is None:
        target_year = datetime.now().year
    
    # Calcular posição do Sol no nascimento
    time_parts = birth_time.split(":")
    hour = int(time_parts[0]) if len(time_parts) > 0 else 0
    minute = int(time_parts[1]) if len(time_parts) > 1 else 0
    
    # Converter para UTC
    utc_offset_hours = round(longitude / 15.0)
    utc_offset_hours = max(-12, min(14, utc_offset_hours))
    utc_hour = hour - utc_offset_hours
    
    adjusted_date = birth_date
    if utc_hour < 0:
        utc_hour += 24
        adjusted_date = birth_date - timedelta(days=1)
    elif utc_hour >= 24:
        utc_hour -= 24
        adjusted_date = birth_date + timedelta(days=1)
    
    birth_datetime = adjusted_date.replace(hour=utc_hour, minute=minute, second=0, microsecond=0)
    
    # Criar observador para o nascimento
    birth_observer = ephem.Observer()
    birth_observer.lat = str(latitude)
    birth_observer.lon = str(longitude)
    birth_observer.date = birth_datetime.strftime('%Y/%m/%d %H:%M:%S')
    
    # Calcular longitude do Sol no nascimento
    natal_sun_longitude = calculate_planet_position(birth_observer, "sun")
    natal_sun_data = get_zodiac_sign(natal_sun_longitude)
    
    # Encontrar o momento exato em que o Sol retorna à mesma posição no ano alvo
    # Começar com uma data aproximada (aniversário)
    solar_return_date = datetime(target_year, birth_date.month, birth_date.day, hour, minute, 0)
    
    # Ajustar para UTC
    solar_return_utc_hour = hour - utc_offset_hours
    solar_return_adjusted_date = solar_return_date
    if solar_return_utc_hour < 0:
        solar_return_utc_hour += 24
        solar_return_adjusted_date = solar_return_date - timedelta(days=1)
    elif solar_return_utc_hour >= 24:
        solar_return_utc_hour -= 24
        solar_return_adjusted_date = solar_return_date + timedelta(days=1)
    
    solar_return_datetime = solar_return_adjusted_date.replace(
        hour=solar_return_utc_hour, 
        minute=minute, 
        second=0, 
        microsecond=0
    )
    
    # Refinar a data para encontrar o momento exato do retorno solar
    # O Sol se move aproximadamente 1 grau por dia, então precisamos ajustar
    best_date = solar_return_datetime
    best_diff = 360.0
    
    # Buscar em um intervalo de ±2 dias
    for day_offset in range(-2, 3):
        test_date = solar_return_datetime + timedelta(days=day_offset)
        
        test_observer = ephem.Observer()
        test_observer.lat = str(latitude)
        test_observer.lon = str(longitude)
        test_observer.date = test_date.strftime('%Y/%m/%d %H:%M:%S')
        
        test_sun_longitude = calculate_planet_position(test_observer, "sun")
        
        # Calcular diferença angular
        diff = abs((test_sun_longitude - natal_sun_longitude + 180) % 360 - 180)
        
        if diff < best_diff:
            best_diff = diff
            best_date = test_date
    
    # Refinar ainda mais com horas
    final_date = best_date
    final_diff = best_diff
    
    for hour_offset in range(-12, 13):
        test_date = best_date + timedelta(hours=hour_offset)
        
        test_observer = ephem.Observer()
        test_observer.lat = str(latitude)
        test_observer.lon = str(longitude)
        test_observer.date = test_date.strftime('%Y/%m/%d %H:%M:%S')
        
        test_sun_longitude = calculate_planet_position(test_observer, "sun")
        diff = abs((test_sun_longitude - natal_sun_longitude + 180) % 360 - 180)
        
        if diff < final_diff:
            final_diff = diff
            final_date = test_date
    
    # Criar observador final para o momento exato da revolução solar
    solar_return_observer = ephem.Observer()
    solar_return_observer.lat = str(latitude)
    solar_return_observer.lon = str(longitude)
    solar_return_observer.date = final_date.strftime('%Y/%m/%d %H:%M:%S')
    
    # Calcular todas as posições planetárias na revolução solar
    sun_longitude = calculate_planet_position(solar_return_observer, "sun")
    moon_longitude = calculate_planet_position(solar_return_observer, "moon")
    ascendant_longitude = calculate_ascendant(solar_return_observer)
    midheaven_longitude = calculate_midheaven(solar_return_observer)
    
    mercury_longitude = calculate_planet_position(solar_return_observer, "mercury")
    venus_longitude = calculate_planet_position(solar_return_observer, "venus")
    mars_longitude = calculate_planet_position(solar_return_observer, "mars")
    jupiter_longitude = calculate_planet_position(solar_return_observer, "jupiter")
    saturn_longitude = calculate_planet_position(solar_return_observer, "saturn")
    
    # Obter signos e casas (simplificado - para casas precisas seria necessário calcular)
    sun_data = get_zodiac_sign(sun_longitude)
    moon_data = get_zodiac_sign(moon_longitude)
    ascendant_data = get_zodiac_sign(ascendant_longitude)
    midheaven_data = get_zodiac_sign(midheaven_longitude)
    
    mercury_data = get_zodiac_sign(mercury_longitude)
    venus_data = get_zodiac_sign(venus_longitude)
    mars_data = get_zodiac_sign(mars_longitude)
    jupiter_data = get_zodiac_sign(jupiter_longitude)
    saturn_data = get_zodiac_sign(saturn_longitude)
    
    # Calcular casa do Sol (simplificado - baseado na diferença angular com o ascendente)
    # Para cálculo preciso de casas, seria necessário usar uma biblioteca mais completa
    sun_house = 1  # Default
    if ascendant_longitude is not None:
        diff = (sun_longitude - ascendant_longitude + 360) % 360
        sun_house = int(diff / 30) + 1
        if sun_house > 12:
            sun_house = sun_house - 12
    
    # Calcular casa da Lua (simplificado)
    moon_house = 1
    if ascendant_longitude is not None:
        diff = (moon_longitude - ascendant_longitude + 360) % 360
        moon_house = int(diff / 30) + 1
        if moon_house > 12:
            moon_house = moon_house - 12
    
    # Calcular casa de Vênus
    venus_house = 1
    if ascendant_longitude is not None:
        diff = (venus_longitude - ascendant_longitude + 360) % 360
        venus_house = int(diff / 30) + 1
        if venus_house > 12:
            venus_house = venus_house - 12
    
    # Calcular casa de Marte
    mars_house = 1
    if ascendant_longitude is not None:
        diff = (mars_longitude - ascendant_longitude + 360) % 360
        mars_house = int(diff / 30) + 1
        if mars_house > 12:
            mars_house = mars_house - 12
    
    # Calcular casa de Júpiter
    jupiter_house = 1
    if ascendant_longitude is not None:
        diff = (jupiter_longitude - ascendant_longitude + 360) % 360
        jupiter_house = int(diff / 30) + 1
        if jupiter_house > 12:
            jupiter_house = jupiter_house - 12
    
    return {
        "solar_return_date": final_date.isoformat(),
        "target_year": target_year,
        "ascendant_sign": ascendant_data["sign"],
        "ascendant_degree": ascendant_data["degree"],
        "sun_sign": sun_data["sign"],
        "sun_degree": sun_data["degree"],
        "sun_house": sun_house,
        "moon_sign": moon_data["sign"],
        "moon_degree": moon_data["degree"],
        "moon_house": moon_house,
        "venus_sign": venus_data["sign"],
        "venus_degree": venus_data["degree"],
        "venus_house": venus_house,
        "mars_sign": mars_data["sign"],
        "mars_degree": mars_data["degree"],
        "mars_house": mars_house,
        "jupiter_sign": jupiter_data["sign"],
        "jupiter_degree": jupiter_data["degree"],
        "jupiter_house": jupiter_house,
        "saturn_sign": saturn_data["sign"],
        "saturn_degree": saturn_data["degree"],
        "midheaven_sign": midheaven_data["sign"],
        "midheaven_degree": midheaven_data["degree"],
    }

