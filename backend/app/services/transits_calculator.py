"""
Serviço para calcular trânsitos futuros baseados no mapa astral do usuário.
"""

import ephem
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import math
from app.services.astrology_calculator import (
    calculate_planet_position,
    get_zodiac_sign,
    ZODIAC_SIGNS
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
    
    # Calcular posições planetárias do mapa natal
    natal_positions = {}
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
    
    # Calcular ascendente natal
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
                        
                        # Retorno de Saturno (conjunção exata)
                        if slow_planet == 'saturn' and aspect_type == 'conjunção' and angle < 1.0:
                            is_significant = True
                            transit_type = 'saturn-return'
                        
                        if is_significant:
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
                                description = f"Saturno retorna à sua posição natal em {natal_sign_data['sign']}. Este é um período crucial de amadurecimento, responsabilidade e recompensas por trabalho árduo. Você será testado em áreas relacionadas à estrutura, disciplina e compromissos de longo prazo."
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
                                natal_point_display = natal_point_names.get(natal_name, natal_name.capitalize())
                                
                                title = f"{transit_planet} em {aspect_name} com seu {natal_point_display}"
                                description = _generate_transit_description(
                                    transit_planet, aspect_type, natal_point_display, natal_sign_data['sign']
                                )
                            
                            transits.append({
                                'date': current_date.isoformat(),
                                'planet': transit_planet,
                                'transit_type': transit_type,
                                'aspect_type': aspect_type,
                                'natal_point': natal_name,
                                'natal_sign': natal_sign_data['sign'],
                                'transit_sign': transit_sign_data['sign'],
                                'angle': angle,
                                'title': title,
                                'description': description,
                                'is_active': current_date <= today + timedelta(days=30)  # Ativo se nos próximos 30 dias
                            })
            except Exception as e:
                print(f"[WARNING] Erro ao calcular trânsito de {slow_planet} em {current_date}: {e}")
                continue
        
        current_date += check_interval
    
    # Ordenar por data e remover duplicatas próximas
    transits.sort(key=lambda x: x['date'])
    
    # Filtrar duplicatas (mesmo trânsito em datas próximas)
    filtered_transits = []
    seen_transits = set()
    
    for transit in transits:
        key = (transit['planet'], transit['aspect_type'], transit['natal_point'])
        if key not in seen_transits:
            seen_transits.add(key)
            filtered_transits.append(transit)
            
            if len(filtered_transits) >= max_transits:
                break
    
    return filtered_transits[:max_transits]


def _generate_transit_description(
    transit_planet: str,
    aspect_type: str,
    natal_point: str,
    natal_sign: str
) -> str:
    """Gera descrição do trânsito baseado no planeta, aspecto e ponto natal."""
    
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
    
    return descriptions.get(natal_point, f"{transit_planet} em {aspect_type} com seu {natal_point} traz {meaning} nesta área do seu mapa.")


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

