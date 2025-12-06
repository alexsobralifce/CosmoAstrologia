"""
Serviço para calcular os melhores momentos para ações específicas baseado em astrologia.
Utiliza aspectos e casas astrológicas para determinar timing ideal.
"""

import ephem
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from app.services.astrology_calculator import get_zodiac_sign
from app.services.transits_calculator import calculate_aspect_angle, get_aspect_type


# Mapeamento de ações para casas astrológicas relevantes
ACTION_HOUSES = {
    'pedir_aumento': {
        'primary_houses': [2, 10],  # Dinheiro e Carreira
        'secondary_houses': [6, 11],  # Trabalho e Networking
        'beneficial_planets': ['Júpiter', 'Sol', 'Vênus'],
        'avoid_planets': ['Saturno', 'Marte'],
        'preferred_aspects': ['trígono', 'sextil', 'conjunção']
    },
    'assinar_contrato': {
        'primary_houses': [7, 10],  # Parcerias e Carreira
        'secondary_houses': [2, 9],  # Recursos e Jurídico
        'beneficial_planets': ['Júpiter', 'Mercúrio', 'Vênus'],
        'avoid_planets': ['Marte', 'Saturno'],
        'preferred_aspects': ['trígono', 'sextil']
    },
    'primeiro_encontro': {
        'primary_houses': [5, 7],  # Romance e Parcerias
        'secondary_houses': [1, 11],  # Identidade e Amizades
        'beneficial_planets': ['Vênus', 'Júpiter', 'Lua'],
        'avoid_planets': ['Saturno', 'Marte'],
        'preferred_aspects': ['trígono', 'sextil', 'conjunção']
    },
    'apresentacao_publica': {
        'primary_houses': [10, 1],  # Carreira e Identidade
        'secondary_houses': [3, 9],  # Comunicação e Expansão
        'beneficial_planets': ['Sol', 'Mercúrio', 'Júpiter'],
        'avoid_planets': ['Saturno', 'Marte'],
        'preferred_aspects': ['trígono', 'sextil']
    },
    'negociacao': {
        'primary_houses': [7, 2],  # Parcerias e Recursos
        'secondary_houses': [3, 9],  # Comunicação e Jurídico
        'beneficial_planets': ['Mercúrio', 'Júpiter', 'Vênus'],
        'avoid_planets': ['Marte', 'Saturno'],
        'preferred_aspects': ['trígono', 'sextil']
    },
    'investimento': {
        'primary_houses': [2, 8],  # Recursos Próprios e Compartilhados
        'secondary_houses': [5, 11],  # Especulação e Futuro
        'beneficial_planets': ['Júpiter', 'Vênus'],
        'avoid_planets': ['Saturno', 'Marte', 'Plutão'],
        'preferred_aspects': ['trígono', 'sextil']
    },
    'mudanca_carreira': {
        'primary_houses': [10, 1],  # Carreira e Identidade
        'secondary_houses': [4, 9],  # Fundação e Expansão
        'beneficial_planets': ['Júpiter', 'Urano', 'Sol'],
        'avoid_planets': ['Saturno'],
        'preferred_aspects': ['trígono', 'sextil', 'conjunção']
    },
    'iniciar_projeto': {
        'primary_houses': [1, 10],  # Identidade e Carreira
        'secondary_houses': [5, 11],  # Criatividade e Futuro
        'beneficial_planets': ['Sol', 'Júpiter', 'Mercúrio'],
        'avoid_planets': ['Saturno', 'Marte'],
        'preferred_aspects': ['trígono', 'sextil']
    }
}

# Planetas e seus nomes em português
PLANET_NAMES = {
    'sun': 'Sol',
    'moon': 'Lua',
    'mercury': 'Mercúrio',
    'venus': 'Vênus',
    'mars': 'Marte',
    'jupiter': 'Júpiter',
    'saturn': 'Saturno',
    'uranus': 'Urano',
    'neptune': 'Netuno',
    'pluto': 'Plutão'
}


def calculate_house_cusp(
    observer: ephem.Observer,
    house_number: int,
    birth_date: datetime,
    birth_time: str,
    latitude: float,
    longitude: float
) -> float:
    """
    Calcula a cúspide de uma casa astrológica.
    Tenta usar Swiss Ephemeris (kerykeion) se disponível, senão usa sistema Equal House.
    """
    # Tentar usar Swiss Ephemeris primeiro (mais preciso)
    try:
        from app.services.swiss_ephemeris_calculator import create_kr_instance
        
        # Criar instância kerykeion
        kr = create_kr_instance(birth_date, birth_time, latitude, longitude, None)
        
        # kerykeion fornece as casas através do objeto houses
        if hasattr(kr, 'houses') and kr.houses:
            # Acessar casa específica (house_1, house_2, etc.)
            house_attr = f"house_{house_number}"
            if hasattr(kr.houses, house_attr):
                house_obj = getattr(kr.houses, house_attr)
                if hasattr(house_obj, 'abs_pos'):
                    house_cusp = float(house_obj.abs_pos)
                    return house_cusp
    except Exception as e:
        # Se falhar, usar cálculo simplificado
        pass
    
    # Fallback: Calcular Ascendente (cúspide da Casa 1)
    from app.services.astrology_calculator import calculate_ascendant
    ascendant = calculate_ascendant(observer)
    
    # Calcular MC (cúspide da Casa 10)
    from app.services.astrology_calculator import calculate_midheaven
    mc = calculate_midheaven(observer)
    
    # Sistema Equal House simplificado
    # Cada casa tem 30 graus a partir do Ascendente
    house_cusps = {
        1: ascendant,
        2: (ascendant + 30) % 360,
        3: (ascendant + 60) % 360,
        4: (ascendant + 90) % 360,
        5: (ascendant + 120) % 360,
        6: (ascendant + 150) % 360,
        7: (ascendant + 180) % 360,
        8: (ascendant + 210) % 360,
        9: (ascendant + 240) % 360,
        10: mc,
        11: (mc + 30) % 360,
        12: (mc + 60) % 360
    }
    
    return house_cusps.get(house_number, ascendant)


def calculate_planet_position_swiss(
    check_date: datetime,
    latitude: float,
    longitude: float,
    planet_name: str
) -> float:
    """
    Calcula a posição de um planeta usando Swiss Ephemeris (biblioteca padrão).
    """
    try:
        from app.services.swiss_ephemeris_calculator import create_kr_instance, get_planet_longitude
        
        # Criar instância kerykeion para a data/hora de trânsito
        time_str = check_date.strftime("%H:%M")
        kr = create_kr_instance(check_date, time_str, latitude, longitude, None)
        
        # Mapear nomes de planetas para chaves do kerykeion
        planet_map = {
            'sun': 'Sun',
            'moon': 'Moon',
            'mercury': 'Mercury',
            'venus': 'Venus',
            'mars': 'Mars',
            'jupiter': 'Jupiter',
            'saturn': 'Saturn',
            'uranus': 'Uranus',
            'neptune': 'Neptune',
            'pluto': 'Pluto'
        }
        
        planet_key = planet_map.get(planet_name.lower())
        if not planet_key:
            raise ValueError(f"Planeta desconhecido: {planet_name}")
        
        # Obter longitude do planeta usando função do swiss_ephemeris_calculator
        return get_planet_longitude(kr, planet_key)
            
    except Exception as e:
        # Fallback para PyEphem se Swiss Ephemeris falhar
        from app.services.astrology_calculator import calculate_planet_position
        observer = ephem.Observer()
        observer.lat = str(latitude)
        observer.lon = str(longitude)
        observer.date = check_date.strftime('%Y/%m/%d %H:%M:%S')
        return calculate_planet_position(observer, planet_name)


def check_planetary_aspects_to_house(
    check_date: datetime,
    latitude: float,
    longitude: float,
    house_cusp: float,
    planets_to_check: List[str],
    preferred_aspects: List[str],
    orb: float = 8.0
) -> List[Dict[str, any]]:
    """
    Verifica aspectos entre planetas e a cúspide de uma casa usando Swiss Ephemeris.
    """
    aspects_found = []
    
    for planet_name in planets_to_check:
        try:
            planet_longitude = calculate_planet_position_swiss(
                check_date, latitude, longitude, planet_name
            )
            angle = calculate_aspect_angle(planet_longitude, house_cusp)
            aspect_type = get_aspect_type(angle, orb=orb)
            
            if aspect_type and aspect_type in preferred_aspects:
                planet_display = PLANET_NAMES.get(planet_name, planet_name)
                aspects_found.append({
                    'planet': planet_display,
                    'aspect_type': aspect_type,
                    'angle': angle,
                    'is_harmonious': aspect_type in ['trígono', 'sextil', 'conjunção']
                })
        except Exception as e:
            continue
    
    return aspects_found


def calculate_best_timing(
    action_type: str,
    birth_date: datetime,
    birth_time: str,
    latitude: float,
    longitude: float,
    days_ahead: int = 30
) -> Dict[str, any]:
    """
    Calcula os melhores momentos para uma ação específica.
    
    Args:
        action_type: Tipo de ação (ex: 'pedir_aumento', 'assinar_contrato')
        birth_date: Data de nascimento
        birth_time: Hora de nascimento (HH:MM)
        latitude: Latitude do local
        longitude: Longitude do local
        days_ahead: Quantos dias à frente calcular (padrão: 30)
    
    Returns:
        Dicionário com melhores momentos e análise
    """
    if action_type not in ACTION_HOUSES:
        return {
            'error': f'Ação desconhecida: {action_type}',
            'best_moments': []
        }
    
    action_config = ACTION_HOUSES[action_type]
    
    # Converter hora de nascimento
    time_parts = birth_time.split(":")
    hour = int(time_parts[0]) if len(time_parts) > 0 else 0
    minute = int(time_parts[1]) if len(time_parts) > 1 else 0
    
    # Criar observador para mapa natal
    birth_observer = ephem.Observer()
    birth_observer.lat = str(latitude)
    birth_observer.lon = str(longitude)
    birth_datetime = birth_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
    birth_observer.date = birth_datetime.strftime('%Y/%m/%d %H:%M:%S')
    
    # Calcular cúspides das casas relevantes no mapa natal
    natal_house_cusps = {}
    for house_num in action_config['primary_houses'] + action_config['secondary_houses']:
        natal_house_cusps[house_num] = calculate_house_cusp(
            birth_observer, 
            house_num,
            birth_date,
            birth_time,
            latitude,
            longitude
        )
    
    # Buscar melhores momentos nos próximos dias
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    best_moments = []
    
    # Verificar a cada 6 horas (4 vezes por dia)
    check_interval = timedelta(hours=6)
    current_date = today
    end_date = today + timedelta(days=days_ahead)
    
    # Planetas a verificar
    all_planets = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']
    
    while current_date <= end_date:
        # Calcular score para este momento (usando Swiss Ephemeris diretamente)
        score = 0
        aspects_found = []
        reasons = []
        
        # Verificar aspectos em casas primárias (peso maior)
        for house_num in action_config['primary_houses']:
            house_cusp = natal_house_cusps[house_num]
            
            # Verificar aspectos de planetas benéficos
            for planet_name in all_planets:
                planet_display = PLANET_NAMES.get(planet_name, planet_name)
                
                if planet_display in action_config['beneficial_planets']:
                    try:
                        # Usar Swiss Ephemeris (biblioteca padrão)
                        transit_planet_longitude = calculate_planet_position_swiss(
                            current_date, latitude, longitude, planet_name
                        )
                        angle = calculate_aspect_angle(transit_planet_longitude, house_cusp)
                        aspect_type = get_aspect_type(angle, orb=8.0)
                        
                        # VALIDAÇÃO RIGOROSA: Verificar novamente se o aspecto está dentro do orbe
                        if aspect_type and aspect_type in action_config['preferred_aspects']:
                            # Definir ângulos alvo para cada aspecto
                            aspect_targets = {
                                'conjunção': 0,
                                'sextil': 60,
                                'quadratura': 90,
                                'trígono': 120,
                                'oposição': 180
                            }
                            target_angle = aspect_targets.get(aspect_type)
                            
                            # Validar se está realmente dentro do orbe de 8°
                            if target_angle is not None:
                                angle_diff = abs(angle - target_angle)
                                if angle_diff > 8.0:
                                    # Aspecto fora do orbe - não adicionar
                                    continue
                            
                            # Pontuação baseada no tipo de aspecto
                            if aspect_type == 'trígono':
                                score += 10
                            elif aspect_type == 'sextil':
                                score += 7
                            elif aspect_type == 'conjunção':
                                score += 8
                            
                            # VALIDAÇÃO CRÍTICA: Garantir que house_num está na lista permitida
                            if house_num not in action_config['primary_houses']:
                                print(f"[ERROR] Bug detectado: house_num {house_num} não está em primary_houses {action_config['primary_houses']}")
                                continue
                            
                            aspects_found.append({
                                'planet': planet_display,
                                'house': house_num,
                                'aspect_type': aspect_type,
                                'is_primary': True
                            })
                            
                            reasons.append(f"{planet_display} em {aspect_type} com Casa {house_num}")
                    except Exception as e:
                        # Log erro silenciosamente (não quebrar o cálculo)
                        continue
        
        # Verificar aspectos em casas secundárias (peso menor)
        for house_num in action_config['secondary_houses']:
            house_cusp = natal_house_cusps[house_num]
            
            for planet_name in all_planets:
                planet_display = PLANET_NAMES.get(planet_name, planet_name)
                
                if planet_display in action_config['beneficial_planets']:
                    try:
                        # Usar Swiss Ephemeris (biblioteca padrão)
                        transit_planet_longitude = calculate_planet_position_swiss(
                            current_date, latitude, longitude, planet_name
                        )
                        angle = calculate_aspect_angle(transit_planet_longitude, house_cusp)
                        aspect_type = get_aspect_type(angle, orb=8.0)
                        
                        # VALIDAÇÃO RIGOROSA: Verificar novamente se o aspecto está dentro do orbe
                        if aspect_type and aspect_type in action_config['preferred_aspects']:
                            # Definir ângulos alvo para cada aspecto
                            aspect_targets = {
                                'conjunção': 0,
                                'sextil': 60,
                                'quadratura': 90,
                                'trígono': 120,
                                'oposição': 180
                            }
                            target_angle = aspect_targets.get(aspect_type)
                            
                            # Validar se está realmente dentro do orbe de 8°
                            if target_angle is not None:
                                angle_diff = abs(angle - target_angle)
                                if angle_diff > 8.0:
                                    # Aspecto fora do orbe - não adicionar
                                    continue
                            
                            # Pontuação menor para casas secundárias
                            if aspect_type == 'trígono':
                                score += 5
                            elif aspect_type == 'sextil':
                                score += 3
                            elif aspect_type == 'conjunção':
                                score += 4
                            
                            # VALIDAÇÃO CRÍTICA: Garantir que house_num está na lista permitida
                            if house_num not in action_config['secondary_houses']:
                                print(f"[ERROR] Bug detectado: house_num {house_num} não está em secondary_houses {action_config['secondary_houses']}")
                                continue
                            
                            aspects_found.append({
                                'planet': planet_display,
                                'house': house_num,
                                'aspect_type': aspect_type,
                                'is_primary': False
                            })
                            
                            reasons.append(f"{planet_display} em {aspect_type} com Casa {house_num}")
                    except Exception as e:
                        # Log erro silenciosamente (não quebrar o cálculo)
                        continue
        
        # Penalizar se planetas desfavoráveis estão em aspectos tensos
        for planet_name in all_planets:
            planet_display = PLANET_NAMES.get(planet_name, planet_name)
            
            if planet_display in action_config['avoid_planets']:
                for house_num in action_config['primary_houses']:
                    house_cusp = natal_house_cusps[house_num]
                    try:
                        # Usar Swiss Ephemeris (biblioteca padrão)
                        transit_planet_longitude = calculate_planet_position_swiss(
                            current_date, latitude, longitude, planet_name
                        )
                        angle = calculate_aspect_angle(transit_planet_longitude, house_cusp)
                        aspect_type = get_aspect_type(angle, orb=8.0)
                        
                        if aspect_type in ['quadratura', 'oposição']:
                            score -= 5
                            reasons.append(f"⚠️ {planet_display} em {aspect_type} com Casa {house_num}")
                    except:
                        continue
        
        # Verificar Lua Fora de Curso (penalizar)
        from app.services.moon_void_calculator import calculate_moon_void_of_course
        moon_void = calculate_moon_void_of_course(
            check_date=current_date,
            latitude=latitude,
            longitude=longitude
        )
        
        if moon_void.get('is_void', False):
            score -= 3
            reasons.append("⚠️ Lua Fora de Curso")
        
        # Adicionar momento se score for positivo
        if score > 0:
            best_moments.append({
                'date': current_date.isoformat(),
                'score': score,
                'aspects': aspects_found,
                'reasons': reasons,
                'is_moon_void': moon_void.get('is_void', False)
            })
        
        current_date += check_interval
    
    # Ordenar por score (maior primeiro)
    best_moments.sort(key=lambda x: x['score'], reverse=True)
    
    # Retornar top 10 melhores momentos
    return {
        'action_type': action_type,
        'action_config': action_config,
        'best_moments': best_moments[:10],
        'total_checked': len(best_moments),
        'analysis_date': datetime.now().isoformat()
    }

