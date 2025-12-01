"""
Serviço de Cálculo Astrológico usando Swiss Ephemeris (via kerykeion).
Fonte única de verdade para todas as posições planetárias e cálculos astrológicos.

Este serviço substitui os cálculos aproximados por cálculos precisos usando
Swiss Ephemeris, que é o padrão ouro para cálculos astrológicos profissionais.
"""
from datetime import datetime
from typing import Dict, Optional
import pytz
from kerykeion import AstrologicalSubject
from kerykeion.schemas.kr_models import AstrologicalSubjectModel
from timezonefinder import TimezoneFinder


# Mapeamento de signos em português
ZODIAC_SIGNS = [
    "Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem",
    "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes"
]

# Mapeamento de nomes de planetas para kerykeion
PLANET_KEYS = {
    "sun": "Sun",
    "moon": "Moon",
    "mercury": "Mercury",
    "venus": "Venus",
    "mars": "Mars",
    "jupiter": "Jupiter",
    "saturn": "Saturn",
    "uranus": "Uranus",
    "neptune": "Neptune",
    "pluto": "Pluto",
}

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

# Mapeamento de signos em inglês para português (kerykeion retorna em inglês)
SIGN_TRANSLATION = {
    "Aries": "Áries",
    "Taurus": "Touro",
    "Gemini": "Gêmeos",
    "Cancer": "Câncer",
    "Leo": "Leão",
    "Virgo": "Virgem",
    "Libra": "Libra",
    "Scorpio": "Escorpião",
    "Sagittarius": "Sagitário",
    "Capricorn": "Capricórnio",
    "Aquarius": "Aquário",
    "Pisces": "Peixes",
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


TZ_FINDER = TimezoneFinder()


def create_kr_instance(
    birth_date: datetime,
    birth_time: str,
    latitude: float,
    longitude: float,
    timezone_name: Optional[str] = None
) -> AstrologicalSubjectModel:
    """
    Cria uma instância AstrologicalSubject (kerykeion) com os dados de nascimento.
    
    Args:
        birth_date: Data de nascimento
        birth_time: Hora de nascimento no formato "HH:MM" (hora local)
        latitude: Latitude do local de nascimento
        longitude: Longitude do local de nascimento
        timezone_name: Nome do timezone (ex: 'America/Sao_Paulo'). Se None, tenta inferir da longitude
    
    Returns:
        Instância AstrologicalSubject com o mapa calculado
    """
    # Combinar data e hora
    time_parts = birth_time.split(":")
    hour = int(time_parts[0]) if len(time_parts) > 0 else 0
    minute = int(time_parts[1]) if len(time_parts) > 1 else 0
    
    # Se timezone não fornecido, tentar inferir da longitude
    if timezone_name is None:
        try:
            inferred_tz = TZ_FINDER.timezone_at(lat=latitude, lng=longitude)
        except Exception:
            inferred_tz = None
        
        if inferred_tz:
            timezone_name = inferred_tz
    
    if timezone_name is None:
        # Aproximação básica: longitude / 15 = timezone offset
        # Para produção, isso deve vir do frontend ou de um banco de dados de cidades
        tz_offset = round(longitude / 15.0)
        # Limitar a faixa razoável
        tz_offset = max(-12, min(14, tz_offset))
        # Criar timezone com UTC offset
        # Importante: na convenção Etc/GMT o sinal é invertido
        timezone_name = f"Etc/GMT{(-tz_offset):+d}"
    
    try:
        # Criar timezone
        tz = pytz.timezone(timezone_name)
    except:
        # Fallback para UTC se timezone inválido
        tz = pytz.UTC
    
    # Criar datetime local
    local_datetime = birth_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    # Localizar na timezone
    if local_datetime.tzinfo is None:
        local_datetime = tz.localize(local_datetime)
    
    # Criar instância AstrologicalSubject (API v5)
    # A classe ainda expõe os mesmos pontos planetários necessários
    subject = AstrologicalSubject(
        name="Natal",
        year=local_datetime.year,
        month=local_datetime.month,
        day=local_datetime.day,
        hour=local_datetime.hour,
        minute=local_datetime.minute,
        lat=latitude,
        lng=longitude,
        tz_str=timezone_name,
        online=False,
    )
    
    # Retorna o modelo interno (mais completo e com todos os pontos)
    return subject.model()


def get_planet_position(kr: AstrologicalSubjectModel, planet_key: str) -> Dict[str, float]:
    """
    Obtém a posição de um planeta do mapa kerykeion.
    
    Returns:
        Dict com 'longitude' (grau absoluto), 'sign' (nome do signo em inglês), 'position' (grau no signo)
    """
    planet_key_upper = PLANET_KEYS.get(planet_key.lower(), planet_key.capitalize())
    attr_name = planet_key_upper.lower()
    
    # Obter objeto do planeta
    planet_obj = getattr(kr, attr_name, None)
    
    if planet_obj is None:
        raise ValueError(f"Planeta não encontrado: {planet_key}")
    
    planet_data = planet_obj.model_dump()
    
    longitude = planet_data.get("abs_pos")
    position = planet_data.get("position")
    sign_en = planet_data.get("sign")
    
    if longitude is None or position is None or sign_en is None:
        raise ValueError(f"Dados incompletos para {planet_key}")
    
    return {
        "longitude": float(longitude),
        "sign_en": sign_en,
        "position": float(position),  # Grau no signo (0-30)
    }


def calculate_birth_chart(
    birth_date: datetime,
    birth_time: str,
    latitude: float,
    longitude: float,
    timezone_name: Optional[str] = None
) -> Dict[str, any]:
    """
    Calcula o mapa astral completo usando Swiss Ephemeris (via kerykeion).
    FONTE ÚNICA DE VERDADE para todas as posições planetárias.
    
    Args:
        birth_date: Data de nascimento
        birth_time: Hora de nascimento no formato "HH:MM" (hora local)
        latitude: Latitude do local de nascimento
        longitude: Longitude do local de nascimento
        timezone_name: Nome do timezone (ex: 'America/Sao_Paulo'). Se None, tenta inferir
    
    Returns:
        Dicionário completo com signos, graus e posições de todos os corpos celestes
    """
    # Criar instância kerykeion (fonte única de verdade)
    kr = create_kr_instance(birth_date, birth_time, latitude, longitude, timezone_name)
    
    # Dicionário para armazenar todas as longitudes (fonte única)
    planet_longitudes = {}
    
    # Calcular posições de todos os planetas
    planets_to_calculate = [
        "sun", "moon", "mercury", "venus", "mars",
        "jupiter", "saturn", "uranus", "neptune", "pluto"
    ]
    
    planet_data = {}
    for planet_key in planets_to_calculate:
        try:
            pos = get_planet_position(kr, planet_key)
            longitude = pos["longitude"]
            planet_longitudes[planet_key] = longitude
            
            # Obter signo em português
            sign_data = get_zodiac_sign(longitude)
            
            planet_data[planet_key] = {
                "sign": sign_data["sign"],
                "degree": sign_data["degree"],
                "longitude": longitude
            }
        except Exception as e:
            print(f"[WARNING] Erro ao calcular {planet_key}: {e}")
            # Se falhar, tentar usar valores padrão
            planet_data[planet_key] = {
                "sign": "Desconhecido",
                "degree": 0.0,
                "longitude": 0.0
            }
    
    # Obter Ascendente (Asc)
    asc_longitude = float(kr.ascendant.abs_pos)
    asc_data = get_zodiac_sign(asc_longitude)
    
    # Obter Meio do Céu (MC)
    mc_longitude = float(kr.medium_coeli.abs_pos)
    mc_data = get_zodiac_sign(mc_longitude)
    
    # Calcular planetas conjuntos ao MC
    MIDHEAVEN_CONJUNCTION_ORB = 5.0
    planets_conjunct_mc = []
    for planet_key, planet_display in PLANET_DISPLAY_NAMES.items():
        if planet_key in planet_longitudes:
            distance = shortest_angular_distance(planet_longitudes[planet_key], mc_longitude)
            if distance <= MIDHEAVEN_CONJUNCTION_ORB:
                planets_conjunct_mc.append(planet_display)
    
    # Obter Nodos Lunares
    # Utilizar o nodo verdadeiro como referência principal
    north_node_longitude = float(kr.true_north_lunar_node.abs_pos)
    south_node_longitude = (north_node_longitude + 180) % 360
    north_node_data = get_zodiac_sign(north_node_longitude)
    south_node_data = get_zodiac_sign(south_node_longitude)
    
    # Calcular Quíron (kerykeion pode não ter, usar fallback se necessário)
    chiron_longitude = None
    try:
        # Tentar obter Quíron se disponível
        if hasattr(kr, 'chiron'):
            chiron_longitude = float(kr.chiron.abs_pos)
        else:
            # Fallback para cálculo aproximado (será melhorado depois)
            # Por enquanto, calcular usando elementos orbitais simples
            chiron_longitude = calculate_chiron_fallback(birth_date, birth_time)
    except:
        chiron_longitude = calculate_chiron_fallback(birth_date, birth_time)
    
    chiron_data = get_zodiac_sign(chiron_longitude)
    
    # Construir resultado final com TODAS as informações
    # Atualizar dicionário principal de longitudes com ângulos-chave
    planet_longitudes.update({
        "ascendant": asc_longitude,
        "midheaven": mc_longitude,
        "north_node": north_node_longitude,
        "south_node": south_node_longitude,
        "chiron": chiron_longitude,
    })
    
    result = {
        # Luminares
        "sun_sign": planet_data["sun"]["sign"],
        "sun_degree": planet_data["sun"]["degree"],
        "sun_longitude": planet_data["sun"]["longitude"],
        "moon_sign": planet_data["moon"]["sign"],
        "moon_degree": planet_data["moon"]["degree"],
        "moon_longitude": planet_data["moon"]["longitude"],
        
        # Ascendente e MC
        "ascendant_sign": asc_data["sign"],
        "ascendant_degree": asc_data["degree"],
        "ascendant_longitude": asc_longitude,
        "midheaven_sign": mc_data["sign"],
        "midheaven_degree": mc_data["degree"],
        "midheaven_longitude": mc_longitude,
        "planets_conjunct_midheaven": planets_conjunct_mc,
        "uranus_on_midheaven": PLANET_DISPLAY_NAMES["uranus"] in planets_conjunct_mc,
        
        # Planetas Pessoais
        "mercury_sign": planet_data["mercury"]["sign"],
        "mercury_degree": planet_data["mercury"]["degree"],
        "mercury_longitude": planet_data["mercury"]["longitude"],
        "venus_sign": planet_data["venus"]["sign"],
        "venus_degree": planet_data["venus"]["degree"],
        "venus_longitude": planet_data["venus"]["longitude"],
        "mars_sign": planet_data["mars"]["sign"],
        "mars_degree": planet_data["mars"]["degree"],
        "mars_longitude": planet_data["mars"]["longitude"],
        
        # Planetas Sociais
        "jupiter_sign": planet_data["jupiter"]["sign"],
        "jupiter_degree": planet_data["jupiter"]["degree"],
        "jupiter_longitude": planet_data["jupiter"]["longitude"],
        "saturn_sign": planet_data["saturn"]["sign"],
        "saturn_degree": planet_data["saturn"]["degree"],
        "saturn_longitude": planet_data["saturn"]["longitude"],
        
        # Planetas Transpessoais
        "uranus_sign": planet_data["uranus"]["sign"],
        "uranus_degree": planet_data["uranus"]["degree"],
        "uranus_longitude": planet_data["uranus"]["longitude"],
        "neptune_sign": planet_data["neptune"]["sign"],
        "neptune_degree": planet_data["neptune"]["degree"],
        "neptune_longitude": planet_data["neptune"]["longitude"],
        "pluto_sign": planet_data["pluto"]["sign"],
        "pluto_degree": planet_data["pluto"]["degree"],
        "pluto_longitude": planet_data["pluto"]["longitude"],
        
        # Nodos Lunares
        "north_node_sign": north_node_data["sign"],
        "north_node_degree": north_node_data["degree"],
        "north_node_longitude": north_node_longitude,
        "south_node_sign": south_node_data["sign"],
        "south_node_degree": south_node_data["degree"],
        "south_node_longitude": south_node_longitude,
        
        # Quíron
        "chiron_sign": chiron_data["sign"],
        "chiron_degree": chiron_data["degree"],
        "chiron_longitude": chiron_longitude,
        
        # FONTE ÚNICA DE VERDADE: todas as longitudes em um único lugar
        "planet_longitudes": planet_longitudes,
    }
    
    return result


def calculate_chiron_fallback(birth_date: datetime, birth_time: str) -> float:
    """
    Fallback para cálculo de Quíron caso kerykeion não tenha.
    Usa elementos orbitais simplificados.
    """
    import math
    from datetime import timedelta
    
    # Data juliana aproximada
    # J2000.0 = 2451545.0
    epoch_j2000 = datetime(2000, 1, 1, 12, 0, 0)
    
    # Combinar data e hora
    time_parts = birth_time.split(":")
    hour = int(time_parts[0]) if len(time_parts) > 0 else 0
    minute = int(time_parts[1]) if len(time_parts) > 1 else 0
    birth_dt = birth_date.replace(hour=hour, minute=minute, second=0)
    
    # Dias desde J2000
    delta = birth_dt - epoch_j2000
    days_since_j2000 = delta.total_seconds() / 86400.0
    
    # Elementos orbitais de Quíron (simplificados)
    L0 = 102.5  # Longitude média em J2000 (graus)
    n = 360.0 / (50.76 * 365.25)  # Movimento médio diário (graus/dia)
    
    # Longitude média
    mean_longitude = (L0 + n * days_since_j2000) % 360
    
    # Aproximação simples (sem equação do centro por enquanto)
    return mean_longitude


# Função auxiliar para obter longitude de um planeta específico
def get_planet_longitude(kr: AstrologicalSubjectModel, planet_key: str) -> float:
    """Obtém apenas a longitude absoluta de um planeta."""
    pos = get_planet_position(kr, planet_key)
    return pos["longitude"]


def get_planet_house(kr: AstrologicalSubjectModel, planet_key: str) -> int:
    """
    Obtém a casa de um planeta usando os dados do kerykeion.
    Kerykeion calcula as casas corretamente usando o sistema de casas configurado.
    
    Returns:
        Número da casa (1-12)
    """
    planet_key_upper = PLANET_KEYS.get(planet_key.lower(), planet_key.capitalize())
    attr_name = planet_key_upper.lower()
    
    planet_obj = getattr(kr, attr_name, None)
    if planet_obj is None:
        return 1  # Default
    
    planet_data = planet_obj.model_dump()
    house = planet_data.get("house")
    
    if house is None:
        return 1  # Default
    
    # Kerykeion pode retornar casa como número ou como string (ex: "Ninth_House")
    if isinstance(house, int):
        return house
    
    if isinstance(house, str):
        # Converter string para número (ex: "Ninth_House" -> 9)
        house_mapping = {
            "First_House": 1, "Second_House": 2, "Third_House": 3,
            "Fourth_House": 4, "Fifth_House": 5, "Sixth_House": 6,
            "Seventh_House": 7, "Eighth_House": 8, "Ninth_House": 9,
            "Tenth_House": 10, "Eleventh_House": 11, "Twelfth_House": 12
        }
        return house_mapping.get(house, 1)
    
    # Tentar converter para int se possível
    try:
        return int(house)
    except (ValueError, TypeError):
        return 1  # Default


def calculate_solar_return(
    birth_date: datetime,
    birth_time: str,
    latitude: float,
    longitude: float,
    target_year: Optional[int] = None,
    timezone_name: Optional[str] = None
) -> Dict[str, any]:
    """
    Calcula o mapa de Revolução Solar usando Swiss Ephemeris (via kerykeion).
    
    A Revolução Solar é calculada para o momento exato em que o Sol retorna
    à mesma posição do nascimento, mas no ano especificado (ou ano atual).
    Usa Swiss Ephemeris para máxima precisão e cálculo correto de casas.
    
    Args:
        birth_date: Data de nascimento
        birth_time: Hora de nascimento no formato "HH:MM" (hora local)
        latitude: Latitude do local de nascimento
        longitude: Longitude do local de nascimento
        target_year: Ano para calcular a revolução (padrão: ano atual)
        timezone_name: Nome do timezone (ex: 'America/Sao_Paulo'). Se None, tenta inferir
    
    Returns:
        Dicionário com o mapa de revolução solar completo
    """
    from datetime import timedelta
    
    # Usar ano atual se não especificado
    if target_year is None:
        target_year = datetime.now().year
    
    # Calcular mapa natal para obter posição do Sol
    natal_chart = calculate_birth_chart(birth_date, birth_time, latitude, longitude, timezone_name)
    natal_sun_longitude = natal_chart["sun_longitude"]
    
    # Encontrar o momento exato do retorno solar
    # Começar com data aproximada (aniversário)
    time_parts = birth_time.split(":")
    hour = int(time_parts[0]) if len(time_parts) > 0 else 0
    minute = int(time_parts[1]) if len(time_parts) > 1 else 0
    
    # Data inicial aproximada
    solar_return_date = datetime(target_year, birth_date.month, birth_date.day, hour, minute, 0)
    
    # Refinar a data para encontrar o momento exato do retorno solar
    # O Sol se move aproximadamente 0.9856 graus por dia (~365.25 dias para 360 graus)
    best_date = solar_return_date
    best_diff = 360.0
    
    # Buscar em um intervalo de ±3 dias
    for day_offset in range(-3, 4):
        test_date = solar_return_date + timedelta(days=day_offset)
        
        try:
            # Calcular mapa para esta data de teste
            test_chart = calculate_birth_chart(
                test_date, 
                birth_time, 
                latitude, 
                longitude, 
                timezone_name
            )
            test_sun_longitude = test_chart["sun_longitude"]
            
            # Calcular diferença angular (considerando que pode ter dado uma volta completa)
            diff = shortest_angular_distance(test_sun_longitude, natal_sun_longitude)
            
            if diff < best_diff:
                best_diff = diff
                best_date = test_date
        except Exception as e:
            print(f"[WARNING] Erro ao calcular posição solar para {test_date}: {e}")
            continue
    
    # Refinar ainda mais com horas (buscar dentro de ±24 horas)
    final_date = best_date
    final_diff = best_diff
    
    for hour_offset in range(-24, 25):
        test_date = best_date + timedelta(hours=hour_offset)
        
        try:
            test_chart = calculate_birth_chart(
                test_date, 
                birth_time, 
                latitude, 
                longitude, 
                timezone_name
            )
            test_sun_longitude = test_chart["sun_longitude"]
            diff = shortest_angular_distance(test_sun_longitude, natal_sun_longitude)
            
            if diff < final_diff:
                final_diff = diff
                final_date = test_date
        except Exception as e:
            continue
    
    # Calcular mapa completo da revolução solar para o momento exato
    solar_return_chart = calculate_birth_chart(
        final_date, 
        birth_time, 
        latitude, 
        longitude, 
        timezone_name
    )
    
    # Criar instância kerykeion para obter casas corretas
    kr_sr = create_kr_instance(final_date, birth_time, latitude, longitude, timezone_name)
    
    # Obter casas dos planetas (kerykeion calcula corretamente)
    planets_to_get_houses = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"]
    
    planet_houses = {}
    for planet_key in planets_to_get_houses:
        try:
            house = get_planet_house(kr_sr, planet_key)
            planet_houses[planet_key] = house
        except Exception as e:
            print(f"[WARNING] Erro ao obter casa de {planet_key}: {e}")
            planet_houses[planet_key] = 1
    
    # Construir resultado no formato esperado
    result = {
        "solar_return_date": final_date.isoformat(),
        "target_year": target_year,
        
        # Ascendente
        "ascendant_sign": solar_return_chart["ascendant_sign"],
        "ascendant_degree": solar_return_chart["ascendant_degree"],
        
        # Sol
        "sun_sign": solar_return_chart["sun_sign"],
        "sun_degree": solar_return_chart["sun_degree"],
        "sun_house": planet_houses.get("sun", 1),
        
        # Lua
        "moon_sign": solar_return_chart["moon_sign"],
        "moon_degree": solar_return_chart["moon_degree"],
        "moon_house": planet_houses.get("moon", 1),
        
        # Planetas
        "mercury_sign": solar_return_chart.get("mercury_sign"),
        "mercury_degree": solar_return_chart.get("mercury_degree"),
        "mercury_house": planet_houses.get("mercury"),
        
        "venus_sign": solar_return_chart.get("venus_sign"),
        "venus_degree": solar_return_chart.get("venus_degree"),
        "venus_house": planet_houses.get("venus"),
        
        "mars_sign": solar_return_chart.get("mars_sign"),
        "mars_degree": solar_return_chart.get("mars_degree"),
        "mars_house": planet_houses.get("mars"),
        
        "jupiter_sign": solar_return_chart.get("jupiter_sign"),
        "jupiter_degree": solar_return_chart.get("jupiter_degree"),
        "jupiter_house": planet_houses.get("jupiter"),
        
        "saturn_sign": solar_return_chart.get("saturn_sign"),
        "saturn_degree": solar_return_chart.get("saturn_degree"),
        "saturn_house": planet_houses.get("saturn"),
        
        # Meio do Céu
        "midheaven_sign": solar_return_chart["midheaven_sign"],
        "midheaven_degree": solar_return_chart["midheaven_degree"],
        
        # Informações adicionais para validação
        "sun_return_precision": final_diff,  # Diferença em graus (deve ser muito pequena)
        "planet_longitudes": solar_return_chart.get("planet_longitudes", {}),
    }
    
    return result

