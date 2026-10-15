"""
Serviço para calcular trânsitos futuros baseados no mapa astral do usuário.
"""

import ephem
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import math
from app.services.astrology_calculator import (
    calculate_planet_position,
    get_zodiac_sign,
    ZODIAC_SIGNS
)
from app.services.transit_descriptions import (
    GENERIC_TRANSIT_DESCRIPTION,
    SATURN_RETURN_DESCRIPTION,
    TEMPLATES as TRANSIT_DESCRIPTION_TEMPLATES,
)


def calculate_aspect_angle(angle1: float, angle2: float) -> float:
    """Calcula o menor ângulo entre duas posições."""
    diff = abs(angle1 - angle2)
    if diff > 180:
        diff = 360 - diff
    return diff


def get_aspect_type(angle: float, orb: float = 8.0) -> Optional[str]:
    """
    Determina o tipo de aspecto baseado no ângulo.
    Retorna None se não for um aspecto válido dentro do orbe.
    """
    # Aspectos principais
    aspects = {
        0: 'conjunção',
        60: 'sextil',
        90: 'quadratura',
        120: 'trígono',
        180: 'oposição'
    }
    
    for aspect_angle, aspect_name in aspects.items():
        if abs(angle - aspect_angle) <= orb:
            return aspect_name
    
    return None


def find_aspect_start_end_dates(
    birth_observer: ephem.Observer,
    transit_observer: ephem.Observer,
    slow_planet: str,
    natal_longitude: float,
    aspect_type: str,
    orb: float = 8.0,
    check_date: datetime = None
) -> Tuple[Optional[datetime], Optional[datetime]]:
    """
    Encontra as datas de início e fim de um aspecto.
    Retorna (start_date, end_date) ou (None, None) se não encontrar.
    Versão otimizada com menos cálculos para evitar timeout.
    """
    if check_date is None:
        check_date = datetime.now()
    
    # Definir ângulo alvo do aspecto
    aspect_targets = {
        'conjunção': 0,
        'sextil': 60,
        'quadratura': 90,
        'trígono': 120,
        'oposição': 180
    }
    target_angle = aspect_targets.get(aspect_type)
    if target_angle is None:
        return (None, None)
    
    # Para evitar timeout, usar estimativas mais simples para planetas muito lentos
    # Plutão e Netuno se movem muito devagar, então usar estimativas
    if slow_planet in ['pluto', 'neptune']:
        # Para planetas muito lentos, usar estimativas baseadas no tipo de aspecto
        duration_days = {
            'conjunção': 60,
            'sextil': 40,
            'quadratura': 50,
            'trígono': 40,
            'oposição': 60
        }
        estimated_duration = duration_days.get(aspect_type, 50)
        start_date = check_date - timedelta(days=estimated_duration // 2)
        end_date = check_date + timedelta(days=estimated_duration // 2)
        return (start_date, end_date)
    
    # Buscar data de início (quando entra no orbe) - buscar 30 dias para trás com intervalo maior
    start_date = None
    search_date = check_date - timedelta(days=30)
    search_interval = timedelta(days=2)  # Intervalo maior para ser mais rápido
    
    prev_angle = None
    iterations = 0
    max_iterations = 30  # Limitar iterações para evitar loops infinitos
    
    while search_date <= check_date and iterations < max_iterations:
        try:
            temp_observer = ephem.Observer()
            temp_observer.lat = transit_observer.lat
            temp_observer.lon = transit_observer.lon
            temp_observer.date = search_date.strftime('%Y/%m/%d %H:%M:%S')
            
            transit_longitude = calculate_planet_position(temp_observer, slow_planet)
            angle = calculate_aspect_angle(transit_longitude, natal_longitude)
            angle_diff = abs(angle - target_angle)
            
            # Se está dentro do orbe agora e não estava antes, encontramos o início
            if angle_diff <= orb:
                if prev_angle is not None and abs(prev_angle - target_angle) > orb:
                    start_date = search_date
                    break
                elif start_date is None:
                    start_date = search_date
            
            prev_angle = angle
            search_date += search_interval
            iterations += 1
        except Exception as e:
            search_date += search_interval
            iterations += 1
            continue
    
    # Buscar data de fim (quando sai do orbe) - buscar 60 dias para frente com intervalo maior
    end_date = None
    search_date = check_date
    max_search = check_date + timedelta(days=60)
    
    prev_angle = None
    was_in_orb = False
    iterations = 0
    max_iterations = 30  # Limitar iterações
    
    while search_date <= max_search and iterations < max_iterations:
        try:
            temp_observer = ephem.Observer()
            temp_observer.lat = transit_observer.lat
            temp_observer.lon = transit_observer.lon
            temp_observer.date = search_date.strftime('%Y/%m/%d %H:%M:%S')
            
            transit_longitude = calculate_planet_position(temp_observer, slow_planet)
            angle = calculate_aspect_angle(transit_longitude, natal_longitude)
            angle_diff = abs(angle - target_angle)
            
            # Se estava dentro do orbe e agora saiu, encontramos o fim
            if was_in_orb and angle_diff > orb:
                end_date = search_date
                break
            
            if angle_diff <= orb:
                was_in_orb = True
            else:
                was_in_orb = False
            
            search_date += search_interval
            iterations += 1
        except Exception as e:
            search_date += search_interval
            iterations += 1
            continue
    
    # Se não encontrou fim, estimar baseado no tipo de aspecto
    if start_date and not end_date:
        # Estimativas baseadas na velocidade dos planetas lentos
        duration_days = {
            'conjunção': 30,
            'sextil': 20,
            'quadratura': 25,
            'trígono': 20,
            'oposição': 30
        }
        estimated_duration = duration_days.get(aspect_type, 30)
        end_date = start_date + timedelta(days=estimated_duration)
    
    return (start_date, end_date)


def calculate_future_transits(
    birth_date: datetime,
    birth_time: str,
    latitude: float,
    longitude: float,
    months_ahead: int = 24,
    max_transits: int = 10
) -> List[Dict[str, any]]:
    """
    Calcula trânsitos futuros baseados no mapa natal do usuário.
    
    Args:
        birth_date: Data de nascimento
        birth_time: Hora de nascimento (HH:MM)
        latitude: Latitude do local de nascimento
        longitude: Longitude do local de nascimento
        months_ahead: Quantos meses à frente calcular (padrão: 24)
        max_transits: Número máximo de trânsitos a retornar (padrão: 10)
    
    Returns:
        Lista de trânsitos futuros ordenados por data
    """
    # Calcular posições planetárias do mapa natal
    time_parts = birth_time.split(":")
    hour = int(time_parts[0]) if len(time_parts) > 0 else 0
    minute = int(time_parts[1]) if len(time_parts) > 1 else 0
    
    # Converter para UTC (aproximação)
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
    
    # Criar observador para o mapa natal
    birth_observer = ephem.Observer()
    birth_observer.lat = str(latitude)
    birth_observer.lon = str(longitude)
    birth_observer.date = birth_datetime.strftime('%Y/%m/%d %H:%M:%S')
    
    # FONTE ÚNICA DE VERDADE: Usar dados do mapa natal do cache
    # Isso garante que usamos as mesmas posições calculadas anteriormente
    from app.services.chart_data_cache import get_or_calculate_chart
    from app.services.astrology_calculator import calculate_birth_chart
    
    # Obter mapa natal completo do cache (fonte única)
    natal_chart = get_or_calculate_chart(
        birth_date=birth_date,
        birth_time=birth_time,
        latitude=latitude,
        longitude=longitude,
        calculate_func=calculate_birth_chart
    )
    
    # Extrair longitudes do mapa natal (fonte única de verdade)
    natal_positions = {}
    if "_source_longitudes" in natal_chart:
        # Usar longitudes da fonte única
        source_lons = natal_chart["_source_longitudes"]
        planet_key_map = {
            'sun': 'sun',
            'moon': 'moon',
            'mercury': 'mercury',
            'venus': 'venus',
            'mars': 'mars',
            'jupiter': 'jupiter',
            'saturn': 'saturn',
            'uranus': 'uranus',
            'neptune': 'neptune',
            'pluto': 'pluto'
        }
        for planet_name in ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']:
            key = planet_key_map.get(planet_name)
            if key and key in source_lons:
                natal_positions[planet_name] = source_lons[key]
    else:
        # Fallback: calcular diretamente se não tiver cache
        planets_to_check = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto']
        for planet_name in planets_to_check:
            try:
                longitude = calculate_planet_position(birth_observer, planet_name)
                natal_positions[planet_name] = longitude
            except Exception as e:
                print(f"[WARNING] Erro ao calcular posição natal de {planet_name}: {e}")
                continue
    
    # Planetas lentos que fazem trânsitos importantes
    slow_planets = ['jupiter', 'saturn', 'uranus', 'neptune', 'pluto']
    
    # Planetas e pontos importantes do mapa natal para verificar trânsitos
    natal_points = {
        'sun': 'Sol',
        'moon': 'Lua',
        'mercury': 'Mercúrio',
        'venus': 'Vênus',
        'mars': 'Marte',
        'ascendant': None  # Será calculado separadamente
    }
    
    # Obter ascendente do mapa natal (fonte única)
    if "_source_longitudes" in natal_chart and "ascendant" in natal_chart["_source_longitudes"]:
        natal_ascendant = natal_chart["_source_longitudes"]["ascendant"]
        natal_positions['ascendant'] = natal_ascendant
    else:
        # Fallback: calcular diretamente
        try:
            from app.services.astrology_calculator import calculate_ascendant
            natal_ascendant = calculate_ascendant(birth_observer)
            natal_positions['ascendant'] = natal_ascendant
        except Exception as e:
            print(f"[WARNING] Erro ao calcular ascendente natal: {e}")
    
    transits = []
    today = datetime.now()
    end_date = today + timedelta(days=months_ahead * 30)
    
    # Verificar trânsitos em intervalos de 7 dias (para não sobrecarregar)
    current_date = today
    check_interval = timedelta(days=7)
    
    while current_date <= end_date and len(transits) < max_transits * 2:  # Buscar mais para filtrar depois
        # Criar observador para a data atual
        transit_observer = ephem.Observer()
        transit_observer.lat = str(latitude)
        transit_observer.lon = str(longitude)
        
        # Converter para UTC
        utc_date = current_date
        transit_observer.date = utc_date.strftime('%Y/%m/%d %H:%M:%S')
        
        # Verificar trânsitos de planetas lentos
        for slow_planet in slow_planets:
            try:
                transit_longitude = calculate_planet_position(transit_observer, slow_planet)
                
                # Verificar aspectos com planetas e pontos do mapa natal
                for natal_point, natal_name in natal_points.items():
                    if natal_point not in natal_positions:
                        continue
                    
                    natal_longitude = natal_positions[natal_point]
                    angle = calculate_aspect_angle(transit_longitude, natal_longitude)
                    aspect_type = get_aspect_type(angle, orb=8.0)
                    
                    if aspect_type:
                        # Verificar se é um trânsito significativo
                        is_significant = False
                        transit_type = None
                        
                        # TODOS os tipos de aspectos são significativos
                        # Conjunções e oposições são sempre significativas
                        if aspect_type in ['conjunção', 'oposição']:
                            is_significant = True
                            if aspect_type == 'conjunção':
                                transit_type = 'conjunction'
                            else:
                                transit_type = 'opposition'
                        
                        # Quadraturas e trígonos também são importantes
                        elif aspect_type in ['quadratura', 'trígono']:
                            is_significant = True
                            if aspect_type == 'quadratura':
                                transit_type = 'square'
                            else:
                                transit_type = 'trine'
                        
                        # Sextis também são importantes (aspecto harmonioso menor)
                        elif aspect_type == 'sextil':
                            is_significant = True
                            transit_type = 'sextile'
                        
                        # Retorno de Saturno (conjunção exata)
                        if slow_planet == 'saturn' and aspect_type == 'conjunção' and angle < 1.0:
                            is_significant = True
                            transit_type = 'saturn-return'
                        
                        if is_significant:
                            # Calcular datas de início e fim do aspecto
                            # Usar try/except para evitar que erros quebrem o cálculo
                            start_date = current_date
                            end_date = current_date
                            
                            try:
                                calculated_start, calculated_end = find_aspect_start_end_dates(
                                    birth_observer,
                                    transit_observer,
                                    slow_planet,
                                    natal_longitude,
                                    aspect_type,
                                    orb=8.0,
                                    check_date=current_date
                                )
                                
                                if calculated_start:
                                    start_date = calculated_start
                                if calculated_end:
                                    end_date = calculated_end
                            except Exception as e:
                                print(f"[WARNING] Erro ao calcular datas de aspecto: {e}")
                                # Usar estimativas se houver erro
                                pass
                            
                            # Se não encontrou datas ou houve erro, usar estimativas
                            if start_date == current_date or end_date == current_date:
                                # Estimativa baseada no tipo de aspecto
                                duration_days = {
                                    'conjunção': 30,
                                    'sextil': 20,
                                    'quadratura': 25,
                                    'trígono': 20,
                                    'oposição': 30
                                }
                                estimated_duration = duration_days.get(aspect_type, 30)
                                if start_date == current_date:
                                    start_date = current_date - timedelta(days=estimated_duration // 2)
                                if end_date == current_date:
                                    end_date = current_date + timedelta(days=estimated_duration)
                            
                            # Obter signos
                            transit_sign_data = get_zodiac_sign(transit_longitude)
                            natal_sign_data = get_zodiac_sign(natal_longitude)
                            
                            planet_names = {
                                'jupiter': 'Júpiter',
                                'saturn': 'Saturno',
                                'uranus': 'Urano',
                                'neptune': 'Netuno',
                                'pluto': 'Plutão'
                            }
                            
                            aspect_names = {
                                'conjunction': 'conjunção',
                                'opposition': 'oposição',
                                'square': 'quadratura',
                                'trine': 'trígono'
                            }
                            
                            transit_planet = planet_names.get(slow_planet, slow_planet.capitalize())
                            aspect_name = aspect_names.get(transit_type, aspect_type)
                            
                            # Criar título e descrição
                            if transit_type == 'saturn-return':
                                title = f"Retorno de Saturno: Marco de Amadurecimento"
                                description = _generate_detailed_transit_description(
                                    transit_planet, aspect_type, 'Sol', natal_sign_data['sign'], transit_type
                                )
                            else:
                                # Converter nome do ponto natal para português
                                natal_point_names = {
                                    'sun': 'Sol',
                                    'moon': 'Lua',
                                    'mercury': 'Mercúrio',
                                    'venus': 'Vênus',
                                    'mars': 'Marte',
                                    'ascendant': 'Ascendente'
                                }
                                
                                # Mapeamento de gênero para concordância correta
                                natal_point_gender = {
                                    'sun': 'masculino',      # seu Sol
                                    'moon': 'feminino',      # sua Lua
                                    'mercury': 'masculino',  # seu Mercúrio
                                    'venus': 'feminino',     # sua Vênus
                                    'mars': 'masculino',     # seu Marte
                                    'ascendant': 'masculino' # seu Ascendente
                                }
                                
                                natal_point_display = natal_point_names.get(natal_name, natal_name.capitalize())
                                gender = natal_point_gender.get(natal_name, 'masculino')
                                
                                # Usar "sua" para feminino e "seu" para masculino
                                possessive = "sua" if gender == 'feminino' else "seu"
                                
                                title = f"{transit_planet} em {aspect_name} com {possessive} {natal_point_display}"
                                description = _generate_detailed_transit_description(
                                    transit_planet, aspect_type, natal_point_display, natal_sign_data['sign'], transit_type
                                )
                            
                            # Garantir que as datas são válidas
                            if not isinstance(start_date, datetime):
                                start_date = current_date
                            if not isinstance(end_date, datetime):
                                end_date = current_date + timedelta(days=30)
                            
                            # Garantir que end_date é depois de start_date
                            if end_date < start_date:
                                end_date = start_date + timedelta(days=30)
                            
                            transits.append({
                                'date': start_date.isoformat(),
                                'start_date': start_date.isoformat(),
                                'end_date': end_date.isoformat(),
                                'planet': transit_planet,
                                'transit_type': transit_type,
                                'aspect_type': aspect_type,
                                'natal_point': natal_name,
                                'natal_sign': natal_sign_data['sign'],
                                'transit_sign': transit_sign_data['sign'],
                                'angle': angle,
                                'title': title,
                                'description': description,
                                'is_active': start_date <= today <= end_date  # Ativo se hoje está entre início e fim
                            })
            except Exception as e:
                print(f"[WARNING] Erro ao calcular trânsito de {slow_planet} em {current_date}: {e}")
                continue
        
        current_date += check_interval
    
    # Ordenar por data e remover duplicatas próximas
    transits.sort(key=lambda x: x['date'])
    
    # FILTRAR TRANSTOS PASSADOS - Apenas transitos válidos (futuros/atuais)
    # Um trânsito é válido se end_date >= hoje (ainda não terminou)
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    valid_transits = []
    
    for transit in transits:
        try:
            # Parsear end_date do trânsito
            end_date_str = transit.get('end_date', '')
            if end_date_str:
                # Parsear ISO format string
                if isinstance(end_date_str, str):
                    # Remover timezone se presente
                    if 'T' in end_date_str:
                        # Extrair apenas a parte da data
                        date_part = end_date_str.split('T')[0]
                        end_date = datetime.strptime(date_part, '%Y-%m-%d')
                    else:
                        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                elif isinstance(end_date_str, datetime):
                    end_date = end_date_str.replace(hour=0, minute=0, second=0, microsecond=0)
                else:
                    continue  # Formato desconhecido, pular
                
                # Filtrar: apenas transitos que ainda não terminaram
                if end_date >= today:
                    valid_transits.append(transit)
                # else: trânsito já passou, não incluir
            else:
                # Se não tem end_date, verificar start_date
                start_date_str = transit.get('start_date', transit.get('date', ''))
                if start_date_str:
                    # Parsear ISO format string
                    if isinstance(start_date_str, str):
                        # Remover timezone se presente
                        if 'T' in start_date_str:
                            # Extrair apenas a parte da data
                            date_part = start_date_str.split('T')[0]
                            start_date = datetime.strptime(date_part, '%Y-%m-%d')
                        else:
                            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                    elif isinstance(start_date_str, datetime):
                        start_date = start_date_str.replace(hour=0, minute=0, second=0, microsecond=0)
                    else:
                        continue  # Formato desconhecido, pular
                    
                    # Se start_date >= hoje, incluir (trânsito futuro)
                    if start_date >= today:
                        valid_transits.append(transit)
                    # else: trânsito já passou, não incluir
                # Se não tem nenhuma data, não incluir
        except (ValueError, TypeError) as e:
            print(f"[WARNING] Erro ao processar data do trânsito no calculador: {e}, transit: {transit.get('title', 'N/A')}")
            # Em caso de erro, não incluir o trânsito (segurança)
            continue
    
    # Filtrar duplicatas (mesmo trânsito em datas próximas)
    filtered_transits = []
    seen_transits = set()
    
    for transit in valid_transits:
        key = (transit['planet'], transit['aspect_type'], transit['natal_point'])
        if key not in seen_transits:
            seen_transits.add(key)
            filtered_transits.append(transit)
            
            if len(filtered_transits) >= max_transits:
                break
    
    print(f"[TRANSITS CALCULATOR] Total calculado: {len(transits)}, Válidos (não passados): {len(valid_transits)}, Após remover duplicatas: {len(filtered_transits)}")
    
    return filtered_transits[:max_transits]


def _get_possessive_for_natal_point(natal_point: str) -> str:
    """
    Retorna o possessivo correto (seu/sua) baseado no gênero do ponto natal.
    """
    # Mapeamento de gênero para pontos astrológicos
    gender_map = {
        'Sol': 'masculino',
        'Lua': 'feminino',
        'Mercúrio': 'masculino',
        'Vênus': 'feminino',
        'Marte': 'masculino',
        'Ascendente': 'masculino',
        'ascendant': 'masculino',
        'sun': 'masculino',
        'moon': 'feminino',
        'mercury': 'masculino',
        'venus': 'feminino',
        'mars': 'masculino'
    }
    
    gender = gender_map.get(natal_point, 'masculino')
    return "sua" if gender == 'feminino' else "seu"


def _generate_transit_description(
    transit_planet: str,
    aspect_type: str,
    natal_point: str,
    natal_sign: str
) -> str:
    """Gera descrição do trânsito baseado no planeta, aspecto e ponto natal."""
    
    # Obter possessivo correto
    possessive = _get_possessive_for_natal_point(natal_point)
    
    planet_meanings = {
        'Júpiter': {
            'conjunção': 'expansão, crescimento e oportunidades',
            'oposição': 'excesso, otimismo exagerado e necessidade de equilíbrio',
            'quadratura': 'desafios de crescimento e necessidade de ajustes',
            'trígono': 'facilidade, sorte e desenvolvimento natural'
        },
        'Saturno': {
            'conjunção': 'lições de responsabilidade, estrutura e disciplina',
            'oposição': 'testes de compromisso e necessidade de equilíbrio',
            'quadratura': 'desafios, restrições e necessidade de trabalho árduo',
            'trígono': 'estruturação natural e recompensas por esforço'
        },
        'Urano': {
            'conjunção': 'mudanças súbitas, inovação e libertação',
            'oposição': 'tensões entre estabilidade e mudança',
            'quadratura': 'rupturas inesperadas e necessidade de adaptação',
            'trígono': 'mudanças positivas e inovação facilitada'
        },
        'Netuno': {
            'conjunção': 'inspiração espiritual, criatividade e intuição',
            'oposição': 'ilusões, confusão e necessidade de clareza',
            'quadratura': 'desorientação e necessidade de discernimento',
            'trígono': 'inspiração artística e conexão espiritual'
        },
        'Plutão': {
            'conjunção': 'transformação profunda, renascimento e poder',
            'oposição': 'confrontos com poder e necessidade de transformação',
            'quadratura': 'crises transformadoras e necessidade de mudança',
            'trígono': 'transformação positiva e renovação profunda'
        }
    }
    
    meanings = planet_meanings.get(transit_planet, {})
    meaning = meanings.get(aspect_type, 'influência significativa')
    
    descriptions = {
        'Sol': f"Este trânsito afeta sua identidade, vitalidade e expressão pessoal. {transit_planet} traz {meaning} nesta área fundamental do seu ser.",
        'Lua': f"Este trânsito influencia suas emoções, necessidades e padrões de segurança. {transit_planet} traz {meaning} em sua vida emocional.",
        'Mercúrio': f"Este trânsito afeta sua comunicação, pensamento e aprendizado. {transit_planet} traz {meaning} em como você processa e compartilha informações.",
        'Vênus': f"Este trânsito influencia relacionamentos, valores e criatividade. {transit_planet} traz {meaning} em sua vida afetiva e estética.",
        'Marte': f"Este trânsito afeta sua energia, ação e assertividade. {transit_planet} traz {meaning} em como você age e persegue seus objetivos.",
        'Ascendente': f"Este trânsito influencia sua personalidade externa e como você se apresenta ao mundo. {transit_planet} traz {meaning} em sua imagem e primeira impressão.",
        'ascendant': f"Este trânsito influencia sua personalidade externa e como você se apresenta ao mundo. {transit_planet} traz {meaning} em sua imagem e primeira impressão."
    }
    
    # Obter possessivo correto para o ponto natal
    possessive = _get_possessive_for_natal_point(natal_point)
    default_desc = f"{transit_planet} em {aspect_type} com {possessive} {natal_point} traz {meaning} nesta área do seu mapa."
    return descriptions.get(natal_point, default_desc)


def _generate_detailed_transit_description(
    transit_planet: str,
    aspect_type: str,
    natal_point: str,
    natal_sign: str,
    transit_type: str
) -> str:
    """Gera descrição didática do trânsito, focada no impacto prático no dia a dia."""
    aspect_names_pt = {
        'conjunção': 'Conjunção',
        'sextil': 'Sextil',
        'quadratura': 'Quadratura',
        'trígono': 'Trígono',
        'oposição': 'Oposição'
    }
    aspect_display = aspect_names_pt.get(aspect_type, aspect_type.capitalize())
    possessive = _get_possessive_for_natal_point(natal_point)

    if transit_type == 'saturn-return':
        return SATURN_RETURN_DESCRIPTION

    template = TRANSIT_DESCRIPTION_TEMPLATES.get((transit_planet, aspect_type))
    if template is None:
        return GENERIC_TRANSIT_DESCRIPTION.format(
            aspect_name=aspect_names_pt.get(aspect_type, aspect_type),
            aspect_type=aspect_type,
            transit_planet=transit_planet,
            possessive=possessive,
            natal_point=natal_point,
        )
    return template.format(
        transit_planet=transit_planet,
        aspect_display=aspect_display,
        possessive=possessive,
        natal_point=natal_point,
    )


def format_transit_timeframe(start_date: datetime, end_date: Optional[datetime] = None) -> str:
    """Formata o período do trânsito de forma legível."""
    months_pt = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    
    start_str = f"{months_pt[start_date.month - 1]} {start_date.year}"
    
    if end_date:
        end_str = f"{months_pt[end_date.month - 1]} {end_date.year}"
        return f"{start_str} - {end_str}"
    
    return f"A partir de {start_str}"

