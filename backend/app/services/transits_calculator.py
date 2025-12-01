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
                                natal_point_display = natal_point_names.get(natal_name, natal_name.capitalize())
                                
                                title = f"{transit_planet} em {aspect_name} com seu {natal_point_display}"
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


def _generate_detailed_transit_description(
    transit_planet: str,
    aspect_type: str,
    natal_point: str,
    natal_sign: str,
    transit_type: str
) -> str:
    """Gera descrição didática e detalhada do trânsito focada no impacto prático no dia a dia."""
    
    # Mapeamento de aspectos para português
    aspect_names_pt = {
        'conjunção': 'Conjunção',
        'sextil': 'Sextil',
        'quadratura': 'Quadratura',
        'trígono': 'Trígono',
        'oposição': 'Oposição'
    }
    
    aspect_display = aspect_names_pt.get(aspect_type, aspect_type.capitalize())
    
    # Descrições didáticas por planeta e aspecto, focadas no impacto prático
    transit_descriptions = {
        ('Júpiter', 'conjunção'): f"""**O que é uma {aspect_display}?**
Uma conjunção acontece quando {transit_planet} se alinha exatamente com seu {natal_point}. É como se duas forças cósmicas se unissem, potencializando seus efeitos.

**Como isso impacta sua rotina:**
• Você sentirá uma expansão natural nas áreas relacionadas ao seu {natal_point}
• Oportunidades podem aparecer de forma mais frequente e natural
• Sua confiança e otimismo tendem a aumentar
• É um período favorável para iniciar projetos importantes relacionados a essa área
• Você pode sentir mais energia e motivação no dia a dia

**O que fazer na prática:**
Aproveite este momento para expandir seus horizontes. Se o trânsito afeta seu Sol, foque em projetos pessoais. Se afeta sua Lua, cuide mais das suas emoções e necessidades. Se afeta Mercúrio, é hora de estudar e comunicar. Se afeta Vênus, invista em relacionamentos e criatividade. Se afeta Marte, canalize sua energia em ações concretas.

**Exemplos práticos:**
• Se afeta seu Sol: "Decidi fazer um curso de especialização que sempre quis, e as oportunidades de crescimento profissional apareceram naturalmente."
• Se afeta sua Lua: "Comecei a cuidar melhor da minha saúde emocional, e me sinto mais equilibrado e confiante no dia a dia."
• Se afeta Mercúrio: "Consegui fechar um contrato importante após uma apresentação que fluiu de forma natural e convincente."
• Se afeta Vênus: "Um novo relacionamento começou de forma harmoniosa, e me sinto mais criativo e inspirado."
• Se afeta Marte: "Iniciei um projeto que estava adiando há meses, e a energia para executá-lo veio naturalmente." """,

        ('Júpiter', 'oposição'): f"""**O que é uma {aspect_display}?**
Uma oposição acontece quando {transit_planet} está exatamente oposto ao seu {natal_point} no mapa. É como um espelho que reflete e amplifica as dinâmicas dessa área.

**Como isso impacta sua rotina:**
• Você pode sentir uma tensão entre suas necessidades internas e oportunidades externas
• Tendência a excessos ou exageros na área relacionada ao seu {natal_point}
• Necessidade de encontrar equilíbrio entre diferentes aspectos da vida
• Pode haver conflitos entre o que você quer e o que o mundo oferece
• Período de aprendizado sobre limites e moderação

**O que fazer na prática:**
Evite exageros e busque equilíbrio. Se o trânsito afeta seu Sol, não se sobrecarregue com projetos. Se afeta sua Lua, cuide para não deixar emoções dominarem. Se afeta Mercúrio, evite prometer mais do que pode cumprir. Se afeta Vênus, não idealize demais relacionamentos. Se afeta Marte, controle impulsos e canalize energia de forma construtiva.

**Exemplos práticos:**
• Se afeta seu Sol: "Aceitei muitos projetos ao mesmo tempo e acabei me sobrecarregando. Aprendi a dizer não e priorizar o que realmente importa."
• Se afeta sua Lua: "Minhas emoções ficaram muito intensas e precisei criar limites para não me desgastar emocionalmente."
• Se afeta Mercúrio: "Prometi entregar mais do que conseguia e tive que renegociar prazos. Aprendi a ser mais realista."
• Se afeta Vênus: "Idealizei demais um relacionamento e precisei ajustar minhas expectativas para a realidade."
• Se afeta Marte: "Aja com impulso e depois me arrependi. Aprendi a pensar antes de agir." """,

        ('Júpiter', 'quadratura'): f"""**O que é uma {aspect_display}?**
Uma quadratura forma um ângulo de 90 graus entre {transit_planet} e seu {natal_point}. É um aspecto desafiador que cria tensão e necessidade de ação.

**Como isso impacta sua rotina:**
• Júpiter em quadratura traz oportunidades que chegam com obstáculos - você sentirá que precisa "merecer" o que deseja
• Sua rotina pode ser interrompida por situações que exigem decisões importantes sobre expansão vs. estabilidade
• Você pode sentir uma pressão interna para crescer, mas com limitações práticas que precisam ser respeitadas
• Período onde otimismo e realidade se encontram - você precisará equilibrar sonhos grandes com passos práticos
• A energia de Júpiter quer expandir, mas a quadratura exige que você trabalhe com disciplina para alcançar crescimento real

**O que fazer na prática:**
Encare os desafios como oportunidades de crescimento. Se o trânsito afeta seu Sol, seja paciente com projetos pessoais. Se afeta sua Lua, trabalhe suas emoções de forma consciente. Se afeta Mercúrio, revise sua comunicação. Se afeta Vênus, seja realista em relacionamentos. Se afeta Marte, canalize energia de forma disciplinada.

**Exemplos práticos:**
• Se afeta seu Sol: "Recebi uma proposta de trabalho melhor, mas exigia mudanças significativas. Tive que pesar cuidadosamente os prós e contras antes de decidir."
• Se afeta sua Lua: "Queria expandir minha vida social, mas minhas responsabilidades familiares exigiam atenção. Aprendi a equilibrar ambos."
• Se afeta Mercúrio: "Tive oportunidades de aprender coisas novas, mas precisava organizar melhor meu tempo para não me sobrecarregar."
• Se afeta Vênus: "Um relacionamento promissor apareceu, mas exigia compromissos que precisava considerar cuidadosamente."
• Se afeta Marte: "Queria iniciar vários projetos ao mesmo tempo, mas aprendi que focar em um de cada vez traz melhores resultados." """,

        ('Júpiter', 'sextil'): f"""**O que é um {aspect_display}?**
Um sextil forma um ângulo de 60 graus entre {transit_planet} e seu {natal_point}. É um aspecto harmonioso menor que oferece oportunidades de crescimento.

**Como isso impacta sua rotina:**
• Oportunidades de expansão aparecem de forma suave e natural
• Você sente uma leve expansão de confiança e otimismo
• Período favorável para pequenos desenvolvimentos e melhorias
• Coisas tendem a fluir melhor, mas de forma mais sutil que um trígono
• Menos tensão e mais facilidade nas áreas relacionadas ao seu {natal_point}

**O que fazer na prática:**
Aproveite as oportunidades que aparecem. Se o trânsito afeta seu Sol, invista em pequenos projetos pessoais. Se afeta sua Lua, cuide das suas emoções. Se afeta Mercúrio, comunique-se e aprenda. Se afeta Vênus, invista em relacionamentos. Se afeta Marte, aja com confiança.

**Exemplos práticos:**
• Se afeta seu Sol: "Oportunidades de crescimento apareceram de forma natural e consegui avançar em projetos pessoais."
• Se afeta sua Lua: "Me sinto mais equilibrado emocionalmente e confiante no dia a dia."
• Se afeta Mercúrio: "Minha comunicação melhorou e consegui aprender coisas novas com facilidade."
• Se afeta Vênus: "Meus relacionamentos estão mais harmoniosos e me sinto mais criativo."
• Se afeta Marte: "Tenho energia para agir e minhas ações têm gerado resultados positivos." """,

        ('Júpiter', 'trígono'): f"""**O que é uma {aspect_display}?**
Um trígono forma um ângulo de 120 graus entre {transit_planet} e seu {natal_point}. É um aspecto harmonioso que facilita o fluxo de energia.

**Como isso impacta sua rotina:**
• As coisas tendem a fluir de forma mais natural e fácil
• Oportunidades aparecem sem muito esforço
• Você sente mais confiança e otimismo no dia a dia
• Período favorável para desenvolvimento e crescimento
• Menos tensão e mais harmonia nas áreas relacionadas ao seu {natal_point}

**O que fazer na prática:**
Aproveite este momento harmonioso. Se o trânsito afeta seu Sol, invista em projetos pessoais. Se afeta sua Lua, cuide bem das suas emoções. Se afeta Mercúrio, comunique-se e aprenda. Se afeta Vênus, invista em relacionamentos e criatividade. Se afeta Marte, aja com confiança.

**Exemplos práticos:**
• Se afeta seu Sol: "As oportunidades apareceram naturalmente e consegui avançar em projetos pessoais sem muito esforço."
• Se afeta sua Lua: "Me sinto emocionalmente equilibrado e confiante, o que melhorou muito minha qualidade de vida."
• Se afeta Mercúrio: "Minha comunicação fluiu de forma natural e consegui aprender coisas novas com facilidade."
• Se afeta Vênus: "Meus relacionamentos estão harmoniosos e me sinto mais criativo e inspirado."
• Se afeta Marte: "Tenho energia e confiança para agir, e minhas ações têm gerado resultados positivos." """,

        ('Saturno', 'conjunção'): f"""**O que é uma {aspect_display}?**
Uma conjunção acontece quando {transit_planet} se alinha exatamente com seu {natal_point}. Saturno traz lições de responsabilidade, estrutura e disciplina.

**Como isso impacta sua rotina:**
• Você sentirá necessidade de estruturar e organizar melhor a área relacionada ao seu {natal_point}
• Pode haver restrições ou limitações que exigem paciência
• Período de amadurecimento e aprendizado sobre responsabilidades
• Necessidade de trabalhar com disciplina e consistência
• Recompensas virão através de esforço e dedicação

**O que fazer na prática:**
Seja disciplinado e paciente. Se o trânsito afeta seu Sol, estruture seus projetos pessoais. Se afeta sua Lua, estabeleça rotinas emocionais saudáveis. Se afeta Mercúrio, organize seus estudos e comunicação. Se afeta Vênus, seja sério em relacionamentos. Se afeta Marte, canalize energia de forma disciplinada.

**Exemplos práticos:**
• Se afeta seu Sol: "Estruturei meus projetos pessoais com prazos e metas claras, e isso trouxe resultados consistentes ao longo do tempo."
• Se afeta sua Lua: "Criei uma rotina de autocuidado emocional e me sinto muito mais equilibrado e centrado."
• Se afeta Mercúrio: "Organizei meus estudos e comunicação de forma sistemática, e isso melhorou muito minha produtividade."
• Se afeta Vênus: "Levei meus relacionamentos mais a sério e isso trouxe profundidade e comprometimento mútuo."
• Se afeta Marte: "Canalizei minha energia de forma disciplinada e consegui realizar objetivos que antes pareciam impossíveis." """,

        ('Saturno', 'oposição'): f"""**O que é uma {aspect_display}?**
Uma oposição acontece quando {transit_planet} está exatamente oposto ao seu {natal_point}. Saturno testa seus compromissos e estruturas.

**Como isso impacta sua rotina:**
• Saturno em oposição cria um espelho de responsabilidades - você verá claramente o que precisa assumir vs. o que pode delegar
• Sua rotina será testada por compromissos externos que confrontam suas necessidades pessoais
• Período onde você precisa negociar entre o que quer fazer e o que precisa fazer - não há como evitar responsabilidades
• Você sentirá a pressão de estruturas externas (trabalho, família, sociedade) que exigem que você amadureça em certas áreas
• A energia de Saturno mostra o que você construiu até agora e o que ainda precisa construir - pode haver frustração, mas também clareza

**O que fazer na prática:**
Encontre equilíbrio entre suas necessidades e responsabilidades. Se o trânsito afeta seu Sol, não se sobrecarregue. Se afeta sua Lua, estabeleça limites emocionais. Se afeta Mercúrio, seja claro em compromissos. Se afeta Vênus, equilibre relacionamentos. Se afeta Marte, controle impulsos.

**Exemplos práticos:**
• Se afeta seu Sol: "Precisei equilibrar meus projetos pessoais com responsabilidades familiares. Aprendi a dizer não quando necessário."
• Se afeta sua Lua: "Minhas necessidades emocionais entraram em conflito com compromissos externos. Estabeleci limites claros."
• Se afeta Mercúrio: "Tive que ser muito claro sobre meus compromissos e prazos, aprendendo a não prometer mais do que posso cumprir."
• Se afeta Vênus: "Um relacionamento exigiu mais comprometimento do que eu estava preparado. Tive que ser honesto sobre minhas limitações."
• Se afeta Marte: "Minha energia para agir foi testada por responsabilidades que não podia ignorar. Aprendi a priorizar." """,

        ('Saturno', 'quadratura'): f"""**O que é uma {aspect_display}?**
Uma quadratura forma um ângulo de 90 graus entre {transit_planet} e seu {natal_point}. Saturno cria desafios que exigem trabalho árduo.

**Como isso impacta sua rotina:**
• Saturno em quadratura traz restrições práticas e concretas - você sentirá que "nada vem fácil" nesta área
• Sua rotina será interrompida por obstáculos reais que exigem paciência e persistência para superar
• Você pode sentir que está sendo "testado" - cada passo à frente parece exigir o dobro de esforço
• Período onde você precisa trabalhar com o que tem, não com o que gostaria de ter - realidade crua e dura
• A energia de Saturno força você a construir estruturas sólidas, mesmo quando você quer resultados rápidos - não há atalhos

**O que fazer na prática:**
Seja persistente e disciplinado. Se o trânsito afeta seu Sol, trabalhe com paciência em projetos. Se afeta sua Lua, gerencie emoções com maturidade. Se afeta Mercúrio, revise e organize comunicação. Se afeta Vênus, seja realista em relacionamentos. Se afeta Marte, canalize energia de forma controlada.

**Exemplos práticos:**
• Se afeta seu Sol: "Meus projetos pessoais enfrentaram obstáculos inesperados. Tive que trabalhar com paciência e disciplina para superá-los."
• Se afeta sua Lua: "Minhas emoções foram testadas por situações difíceis. Aprendi a gerenciá-las com maturidade e responsabilidade."
• Se afeta Mercúrio: "Minha comunicação enfrentou limitações práticas. Tive que ser mais organizado e claro em minhas palavras."
• Se afeta Vênus: "Um relacionamento passou por dificuldades reais. Tive que trabalhar com paciência para construir algo sólido."
• Se afeta Marte: "Minha energia para agir foi limitada por obstáculos práticos. Aprendi a trabalhar com disciplina e persistência." """,

        ('Saturno', 'sextil'): f"""**O que é um {aspect_display}?**
Um sextil forma um ângulo de 60 graus entre {transit_planet} e seu {natal_point}. Saturno oferece oportunidades suaves de estruturação.

**Como isso impacta sua rotina:**
• Oportunidades de organização aparecem de forma suave e natural
• Você sente uma leve necessidade de estruturar melhor a área relacionada ao seu {natal_point}
• Período favorável para pequenos ajustes e melhorias organizacionais
• Disciplina e consistência fluem de forma mais fácil, mas de forma mais sutil que um trígono
• A energia de Saturno trabalha a seu favor de forma suave, trazendo maturidade sem pressão excessiva

**O que fazer na prática:**
Aproveite para fazer pequenos ajustes organizacionais. Se o trânsito afeta seu Sol, organize projetos pessoais. Se afeta sua Lua, estabeleça rotinas emocionais. Se afeta Mercúrio, organize estudos. Se afeta Vênus, estruture relacionamentos. Se afeta Marte, canalize energia de forma organizada.

**Exemplos práticos:**
• Se afeta seu Sol: "Consegui organizar meus projetos pessoais de forma natural. As estruturas que criei funcionaram bem."
• Se afeta sua Lua: "Estabeleci rotinas emocionais saudáveis que melhoraram minha qualidade de vida."
• Se afeta Mercúrio: "Organizei meus estudos e comunicação de forma sistemática, e tudo fluiu bem."
• Se afeta Vênus: "Estruturei meus relacionamentos de forma madura e isso trouxe estabilidade."
• Se afeta Marte: "Canalizei minha energia de forma organizada e consegui realizar objetivos importantes." """,

        ('Saturno', 'trígono'): f"""**O que é uma {aspect_display}?**
Um trígono forma um ângulo de 120 graus entre {transit_planet} e seu {natal_point}. Saturno facilita estruturação e organização.

**Como isso impacta sua rotina:**
• Saturno em trígono traz organização natural - você sentirá que as estruturas que precisa se formam sem muito esforço
• Sua rotina se estabiliza de forma harmoniosa - você consegue estabelecer hábitos e rotinas que realmente funcionam
• Período onde disciplina e consistência fluem naturalmente - você não precisa se forçar, apenas seguir o fluxo
• Você colhe recompensas por esforços passados - estruturas que construiu anteriormente agora dão frutos
• A energia de Saturno trabalha a seu favor, trazendo maturidade e responsabilidade sem a pressão de quadratura ou oposição

**O que fazer na prática:**
Aproveite para estruturar sua vida. Se o trânsito afeta seu Sol, organize projetos pessoais. Se afeta sua Lua, estabeleça rotinas emocionais. Se afeta Mercúrio, organize estudos. Se afeta Vênus, estruture relacionamentos. Se afeta Marte, canalize energia de forma organizada.

**Exemplos práticos:**
• Se afeta seu Sol: "Consegui organizar meus projetos pessoais de forma natural e eficiente. As estruturas que criei funcionaram perfeitamente."
• Se afeta sua Lua: "Estabeleci rotinas emocionais saudáveis que se tornaram parte natural da minha vida diária."
• Se afeta Mercúrio: "Organizei meus estudos e comunicação de forma sistemática, e tudo fluiu sem esforço excessivo."
• Se afeta Vênus: "Estruturei meus relacionamentos de forma madura e responsável, e isso trouxe estabilidade e profundidade."
• Se afeta Marte: "Canalizei minha energia de forma organizada e disciplinada, e consegui realizar objetivos importantes." """,

        ('Urano', 'conjunção'): f"""**O que é uma {aspect_display}?**
Uma conjunção acontece quando {transit_planet} se alinha exatamente com seu {natal_point}. Urano traz mudanças súbitas e inovação.

**Como isso impacta sua rotina:**
• Urano em conjunção traz rupturas elétricas - sua rotina pode ser completamente transformada por eventos inesperados
• Você sentirá uma urgência interna por liberdade e independência - padrões antigos se tornam insuportáveis
• Período onde o inesperado se torna o normal - você precisa estar preparado para mudanças que chegam sem aviso
• Sua rotina diária pode ser interrompida por insights súbitos, oportunidades inovadoras ou necessidade urgente de mudança
• A energia de Urano quer quebrar tudo que é rígido e previsível - você pode sentir que precisa "explodir" certas estruturas

**O que fazer na prática:**
Esteja aberto a mudanças. Se o trânsito afeta seu Sol, aceite transformações pessoais. Se afeta sua Lua, permita mudanças emocionais. Se afeta Mercúrio, experimente novas formas de comunicação. Se afeta Vênus, esteja aberto a relacionamentos diferentes. Se afeta Marte, canalize energia de forma inovadora.

**Exemplos práticos:**
• Se afeta seu Sol: "De repente, percebi que precisava mudar completamente minha direção na vida. Aceitei a mudança e me sinto mais autêntico."
• Se afeta sua Lua: "Minhas emoções mudaram de forma súbita e inesperada. Aprendi a aceitar essas transformações como parte do meu crescimento."
• Se afeta Mercúrio: "Tive insights revolucionários sobre como me comunicar. Experimentei novas formas de expressão que funcionaram muito melhor."
• Se afeta Vênus: "Um relacionamento inesperado apareceu e mudou minha perspectiva sobre amor e conexão."
• Se afeta Marte: "Minha forma de agir mudou completamente. Encontrei novas maneiras de canalizar minha energia que são muito mais eficazes." """,

        ('Urano', 'oposição'): f"""**O que é uma {aspect_display}?**
Uma oposição acontece quando {transit_planet} está exatamente oposto ao seu {natal_point}. Urano cria tensão entre estabilidade e mudança.

**Como isso impacta sua rotina:**
• Urano em oposição cria um espelho de liberdade - você vê claramente o que precisa mudar, mas também o que precisa manter
• Sua rotina será tensionada entre o conforto do conhecido e a urgência por algo novo e diferente
• Período onde você questiona tudo que construiu - "Isso ainda me serve?" se torna uma pergunta constante
• Você sentirá pressão externa por mudanças (pessoas, situações, eventos) que confrontam sua necessidade de estabilidade
• A energia de Urano mostra o que precisa ser libertado, mas a oposição exige que você encontre um equilíbrio - não pode quebrar tudo

**O que fazer na prática:**
Encontre equilíbrio entre estabilidade e mudança. Se o trânsito afeta seu Sol, não rejeite mudanças necessárias. Se afeta sua Lua, permita evolução emocional. Se afeta Mercúrio, esteja aberto a novas ideias. Se afeta Vênus, não se prenda a relacionamentos antigos. Se afeta Marte, canalize energia de forma inovadora.

**Exemplos práticos:**
• Se afeta seu Sol: "Senti conflito entre minha necessidade de estabilidade e o desejo de mudar. Encontrei um equilíbrio que funcionou para mim."
• Se afeta sua Lua: "Minhas emoções oscilaram entre o conforto do conhecido e a urgência por algo novo. Aprendi a integrar ambos."
• Se afeta Mercúrio: "Questionei minhas formas antigas de pensar, mas mantive o que ainda funcionava. Encontrei um equilíbrio."
• Se afeta Vênus: "Precisei equilibrar relacionamentos estáveis com a necessidade de experimentar algo diferente."
• Se afeta Marte: "Minha forma de agir foi tensionada entre padrões antigos e novas possibilidades. Encontrei uma síntese." """,

        ('Urano', 'quadratura'): f"""**O que é uma {aspect_display}?**
Uma quadratura forma um ângulo de 90 graus entre {transit_planet} e seu {natal_point}. Urano cria rupturas e necessidade de adaptação.

**Como isso impacta sua rotina:**
• Urano em quadratura traz rupturas forçadas - sua rotina será interrompida por eventos que você não pode controlar
• Você sentirá uma tensão entre querer manter o status quo e a necessidade urgente de mudar - não há como evitar
• Período onde mudanças chegam de forma abrupta e desestabilizadora - você precisa se adaptar rapidamente ou ficar para trás
• Sua rotina diária pode ser completamente virada de cabeça para baixo - o que funcionava antes não funciona mais
• A energia de Urano força você a quebrar padrões rígidos - você pode resistir, mas a mudança virá de qualquer forma

**O que fazer na prática:**
Seja flexível e adaptável. Se o trânsito afeta seu Sol, aceite mudanças pessoais. Se afeta sua Lua, gerencie emoções com flexibilidade. Se afeta Mercúrio, adapte-se a novas formas de comunicação. Se afeta Vênus, esteja aberto a mudanças em relacionamentos. Se afeta Marte, canalize energia de forma inovadora.

**Exemplos práticos:**
• Se afeta seu Sol: "Minha vida pessoal foi virada de cabeça para baixo por eventos inesperados. Tive que me adaptar rapidamente e me reinventar."
• Se afeta sua Lua: "Minhas emoções foram desestabilizadas por mudanças súbitas. Aprendi a ser flexível e me adaptar."
• Se afeta Mercúrio: "Minha forma de comunicar foi interrompida por situações inesperadas. Tive que encontrar novas maneiras de me expressar."
• Se afeta Vênus: "Meus relacionamentos passaram por rupturas inesperadas. Tive que me adaptar a novas dinâmicas."
• Se afeta Marte: "Minha forma de agir foi interrompida por eventos inesperados. Aprendi a ser mais flexível e adaptável." """,

        ('Urano', 'trígono'): f"""**O que é uma {aspect_display}?**
Um trígono forma um ângulo de 120 graus entre {transit_planet} e seu {natal_point}. Urano facilita mudanças positivas e inovação.

**Como isso impacta sua rotina:**
• Urano em trígono traz inovação fluida - mudanças positivas chegam de forma natural e sem resistência
• Sua rotina se renova de forma harmoniosa - você consegue experimentar coisas novas sem perder estabilidade
• Período onde liberdade e independência fluem naturalmente - você sente que pode ser autêntico sem quebrar tudo
• Você tem insights inovadores que se materializam facilmente - ideias revolucionárias encontram caminho para se tornar realidade
• A energia de Urano trabalha a seu favor, trazendo libertação e inovação sem a tensão de quadratura ou oposição

**O que fazer na prática:**
Aproveite para inovar. Se o trânsito afeta seu Sol, experimente novas formas de expressão. Se afeta sua Lua, permita evolução emocional. Se afeta Mercúrio, explore novas ideias. Se afeta Vênus, esteja aberto a relacionamentos diferentes. Se afeta Marte, canalize energia de forma criativa.

**Exemplos práticos:**
• Se afeta seu Sol: "Experimentei novas formas de me expressar e me sinto mais autêntico e livre. As mudanças vieram naturalmente."
• Se afeta sua Lua: "Minhas emoções evoluíram de forma positiva e natural. Sinto mais liberdade emocional."
• Se afeta Mercúrio: "Explorei novas ideias e formas de pensar que se materializaram facilmente. Minha comunicação melhorou."
• Se afeta Vênus: "Estou aberto a relacionamentos diferentes e inovadores. Sinto mais liberdade para me conectar."
• Se afeta Marte: "Canalizei minha energia de forma criativa e inovadora. Sinto mais liberdade para agir." """,

        ('Netuno', 'conjunção'): f"""**O que é uma {aspect_display}?**
Uma conjunção acontece quando {transit_planet} se alinha exatamente com seu {natal_point}. Netuno traz inspiração espiritual e criatividade.

**Como isso impacta sua rotina:**
• Netuno em conjunção dissolve fronteiras - sua rotina pode se tornar mais fluida e menos rígida, às vezes confusa
• Você sentirá uma necessidade profunda de conectar-se com algo transcendente - rotinas mundanas podem parecer vazias
• Período onde intuição e sensibilidade aumentam drasticamente - você pode sentir coisas que não consegue explicar logicamente
• Sua rotina diária pode ser interrompida por momentos de inspiração, sonhos vívidos ou necessidade de isolamento para processar
• A energia de Netuno quer dissolver o ego e conectar com o divino - você pode sentir que precisa "perder-se" para se encontrar

**O que fazer na prática:**
Conecte-se com sua intuição. Se o trânsito afeta seu Sol, explore sua espiritualidade. Se afeta sua Lua, cuide de suas emoções com compaixão. Se afeta Mercúrio, use criatividade na comunicação. Se afeta Vênus, invista em arte e relacionamentos compassivos. Se afeta Marte, canalize energia de forma criativa.

**Exemplos práticos:**
• Se afeta seu Sol: "Senti uma necessidade profunda de explorar minha espiritualidade. Minha rotina se tornou mais fluida e inspirada."
• Se afeta sua Lua: "Minhas emoções se tornaram mais sensíveis e intuitivas. Aprendi a confiar mais na minha intuição."
• Se afeta Mercúrio: "Minha comunicação se tornou mais criativa e inspirada. Uso mais metáforas e expressão artística."
• Se afeta Vênus: "Meus relacionamentos se tornaram mais compassivos e inspirados. Sinto conexões mais profundas."
• Se afeta Marte: "Canalizei minha energia de forma mais criativa e inspirada. Sinto que estou servindo a algo maior." """,

        ('Netuno', 'oposição'): f"""**O que é uma {aspect_display}?**
Uma oposição acontece quando {transit_planet} está exatamente oposto ao seu {natal_point}. Netuno pode trazer ilusões e necessidade de clareza.

**Como isso impacta sua rotina:**
• Netuno em oposição cria um espelho de ilusão - você vê claramente o que é real vs. o que é fantasia
• Sua rotina será tensionada entre sonhos idealizados e realidade prática - você precisa encontrar o equilíbrio
• Período onde você precisa discernir entre o que é inspiração genuína e o que é escapismo - não pode viver só de sonhos
• Você sentirá a pressão de situações externas que revelam ilusões - pessoas ou eventos mostram a verdade que você não queria ver
• A energia de Netuno mostra o que precisa ser dissolvido, mas a oposição exige que você mantenha os pés no chão - não pode se perder completamente

**O que fazer na prática:**
Busque clareza e discernimento. Se o trânsito afeta seu Sol, seja realista sobre si mesmo. Se afeta sua Lua, gerencie emoções com clareza. Se afeta Mercúrio, comunique-se de forma clara. Se afeta Vênus, seja realista em relacionamentos. Se afeta Marte, canalize energia de forma consciente.

**Exemplos práticos:**
• Se afeta seu Sol: "Precisei equilibrar meus sonhos idealizados com a realidade prática. Aprendi a ser mais realista sobre mim mesmo."
• Se afeta sua Lua: "Minhas emoções oscilaram entre idealização e realidade. Aprendi a discernir entre o que é real e o que é fantasia."
• Se afeta Mercúrio: "Precisei equilibrar comunicação inspirada com clareza prática. Aprendi a ser mais direto quando necessário."
• Se afeta Vênus: "Meus relacionamentos passaram por um processo de desidealização. Aprendi a ver as pessoas como realmente são."
• Se afeta Marte: "Precisei equilibrar ação inspirada com ação prática. Aprendi a canalizar energia de forma mais consciente." """,

        ('Netuno', 'quadratura'): f"""**O que é uma {aspect_display}?**
Uma quadratura forma um ângulo de 90 graus entre {transit_planet} e seu {natal_point}. Netuno pode trazer desorientação e necessidade de discernimento.

**Como isso impacta sua rotina:**
• Netuno em quadratura traz confusão forçada - sua rotina pode ser desestabilizada por ilusões que se revelam como falsas
• Você sentirá uma tensão entre querer acreditar em sonhos e a necessidade urgente de ver a realidade - não há como evitar a verdade
• Período onde ilusões são quebradas de forma dolorosa - você pode descobrir que estava enganado sobre algo importante
• Sua rotina diária pode ser interrompida por descobertas que mudam completamente sua perspectiva - o que você pensava que sabia não é verdade
• A energia de Netuno força você a discernir entre realidade e fantasia - você pode resistir, mas a verdade virá de qualquer forma

**O que fazer na prática:**
Seja prático e discernente. Se o trânsito afeta seu Sol, busque clareza sobre seus objetivos. Se afeta sua Lua, gerencie emoções com discernimento. Se afeta Mercúrio, comunique-se claramente. Se afeta Vênus, seja realista em relacionamentos. Se afeta Marte, canalize energia de forma consciente.

**Exemplos práticos:**
• Se afeta seu Sol: "Descobri que estava iludido sobre mim mesmo. Tive que enfrentar verdades difíceis e me tornar mais realista."
• Se afeta sua Lua: "Minhas emoções foram desestabilizadas por descobertas sobre ilusões que eu mantinha. Aprendi a ser mais discernente."
• Se afeta Mercúrio: "Minha comunicação foi afetada por confusão e falta de clareza. Tive que trabalhar para me comunicar de forma mais direta."
• Se afeta Vênus: "Descobri ilusões em meus relacionamentos. Tive que ver as pessoas como realmente são, não como eu queria que fossem."
• Se afeta Marte: "Minha forma de agir foi afetada por confusão e falta de direção. Aprendi a canalizar energia de forma mais consciente e prática." """,

        ('Netuno', 'sextil'): f"""**O que é um {aspect_display}?**
Um sextil forma um ângulo de 60 graus entre {transit_planet} e seu {natal_point}. Netuno oferece oportunidades suaves de inspiração e criatividade.

**Como isso impacta sua rotina:**
• Oportunidades de inspiração e criatividade aparecem de forma suave e natural
• Você sente uma leve conexão com algo maior na área relacionada ao seu {natal_point}
• Período favorável para pequenas explorações espirituais e criativas
• Intuição e criatividade fluem de forma mais fácil, mas de forma mais sutil que um trígono
• A energia de Netuno trabalha a seu favor de forma suave, trazendo inspiração sem confusão excessiva

**O que fazer na prática:**
Aproveite para explorar criatividade e espiritualidade. Se o trânsito afeta seu Sol, explore sua espiritualidade. Se afeta sua Lua, conecte-se com suas emoções de forma compassiva. Se afeta Mercúrio, use criatividade na comunicação. Se afeta Vênus, invista em arte e relacionamentos. Se afeta Marte, canalize energia de forma criativa.

**Exemplos práticos:**
• Se afeta seu Sol: "Explorei minha espiritualidade de forma natural. Sinto conexão com algo maior."
• Se afeta sua Lua: "Conectei-me com minhas emoções de forma compassiva. Sinto mais compaixão."
• Se afeta Mercúrio: "Usei criatividade na comunicação de forma natural. Minhas palavras se tornaram mais inspiradas."
• Se afeta Vênus: "Investi em arte e relacionamentos de forma inspirada. Sinto conexões mais profundas."
• Se afeta Marte: "Canalizei minha energia de forma criativa. Sinto que estou servindo a algo maior." """,

        ('Netuno', 'trígono'): f"""**O que é uma {aspect_display}?**
Um trígono forma um ângulo de 120 graus entre {transit_planet} e seu {natal_point}. Netuno facilita inspiração artística e conexão espiritual.

**Como isso impacta sua rotina:**
• Netuno em trígono traz inspiração fluida - criatividade e espiritualidade fluem naturalmente sem confusão excessiva
• Sua rotina se torna mais inspirada e compassiva - você sente conexão com algo maior sem perder os pés no chão
• Período onde intuição e criatividade trabalham juntas harmoniosamente - você tem insights que se materializam facilmente
• Você sente compaixão e conexão espiritual sem a desorientação de quadratura ou oposição - tudo flui naturalmente
• A energia de Netuno trabalha a seu favor, trazendo inspiração e transcendência sem perder contato com a realidade prática

**O que fazer na prática:**
Aproveite para criar e inspirar-se. Se o trânsito afeta seu Sol, explore sua espiritualidade. Se afeta sua Lua, conecte-se com suas emoções de forma compassiva. Se afeta Mercúrio, use criatividade na comunicação. Se afeta Vênus, invista em arte e relacionamentos. Se afeta Marte, canalize energia de forma criativa.

**Exemplos práticos:**
• Se afeta seu Sol: "Explorei minha espiritualidade de forma natural e inspirada. Sinto conexão com algo maior sem perder a realidade."
• Se afeta sua Lua: "Conectei-me com minhas emoções de forma compassiva e inspirada. Sinto mais compaixão por mim e pelos outros."
• Se afeta Mercúrio: "Usei criatividade na comunicação de forma natural e eficaz. Minhas palavras se tornaram mais inspiradas."
• Se afeta Vênus: "Investi em arte e relacionamentos de forma inspirada. Sinto conexões mais profundas e compassivas."
• Se afeta Marte: "Canalizei minha energia de forma criativa e inspirada. Sinto que estou servindo a algo maior." """,

        ('Plutão', 'conjunção'): f"""**O que é uma {aspect_display}?**
Uma conjunção acontece quando {transit_planet} se alinha exatamente com seu {natal_point}. Plutão traz transformação profunda e renascimento.

**Como isso impacta sua rotina:**
• Plutão em conjunção traz morte e renascimento - sua rotina será completamente transformada através de crises profundas
• Você sentirá uma necessidade urgente de transformar tudo que é superficial - padrões antigos se tornam insuportáveis
• Período onde poder pessoal e controle se encontram - você precisa aprender a usar poder de forma construtiva, não destrutiva
• Sua rotina diária pode ser interrompida por crises transformadoras - o que não serve mais precisa morrer para que algo novo nasça
• A energia de Plutão quer destruir tudo que é falso e superficial - você pode resistir, mas a transformação é inevitável e profunda

**O que fazer na prática:**
Aceite transformações necessárias. Se o trânsito afeta seu Sol, permita mudanças profundas em sua identidade. Se afeta sua Lua, transforme padrões emocionais. Se afeta Mercúrio, renove sua forma de pensar. Se afeta Vênus, transforme relacionamentos. Se afeta Marte, canalize poder de forma construtiva.

**Exemplos práticos:**
• Se afeta seu Sol: "Passei por uma transformação profunda em minha identidade. Tive que deixar ir padrões antigos e renascer como uma pessoa nova."
• Se afeta sua Lua: "Meus padrões emocionais foram completamente transformados. Tive que enfrentar traumas profundos para renascer."
• Se afeta Mercúrio: "Minha forma de pensar foi completamente renovada. Tive que questionar tudo que acreditava e reconstruir."
• Se afeta Vênus: "Meus relacionamentos passaram por transformações profundas. Tive que deixar ir o que não servia mais."
• Se afeta Marte: "Minha forma de agir foi completamente transformada. Aprendi a usar poder de forma construtiva, não destrutiva." """,

        ('Plutão', 'oposição'): f"""**O que é uma {aspect_display}?**
Uma oposição acontece quando {transit_planet} está exatamente oposto ao seu {natal_point}. Plutão cria confrontos com poder e necessidade de transformação.

**Como isso impacta sua rotina:**
• Plutão em oposição cria um espelho de poder - você vê claramente dinâmicas de controle e manipulação, suas e dos outros
• Sua rotina será tensionada por confrontos com poder - pessoas ou situações mostram onde você está sendo controlado ou controlando demais
• Período onde você precisa transformar dinâmicas antigas de poder - não pode continuar controlando ou sendo controlado
• Você sentirá a pressão de situações externas que revelam abusos de poder - o que estava escondido vem à tona
• A energia de Plutão mostra o que precisa ser transformado, mas a oposição exige que você encontre equilíbrio - não pode destruir tudo

**O que fazer na prática:**
Transforme dinâmicas antigas. Se o trânsito afeta seu Sol, não tente controlar demais. Se afeta sua Lua, transforme padrões emocionais. Se afeta Mercúrio, renove comunicação. Se afeta Vênus, transforme relacionamentos. Se afeta Marte, canalize poder de forma consciente.

**Exemplos práticos:**
• Se afeta seu Sol: "Enfrentei confrontos com poder que revelaram onde eu estava controlando demais. Aprendi a equilibrar controle e libertação."
• Se afeta sua Lua: "Minhas emoções foram tensionadas por dinâmicas de poder. Tive que transformar padrões antigos de controle emocional."
• Se afeta Mercúrio: "Minha comunicação foi afetada por confrontos com poder. Tive que renovar minha forma de me expressar."
• Se afeta Vênus: "Meus relacionamentos passaram por confrontos com dinâmicas de poder. Tive que transformar relacionamentos tóxicos."
• Se afeta Marte: "Minha forma de agir foi tensionada por confrontos com poder. Aprendi a canalizar poder de forma mais consciente." """,

        ('Plutão', 'quadratura'): f"""**O que é uma {aspect_display}?**
Uma quadratura forma um ângulo de 90 graus entre {transit_planet} e seu {natal_point}. Plutão cria crises transformadoras.

**Como isso impacta sua rotina:**
• Plutão em quadratura traz crises forçadas - sua rotina será completamente desestabilizada por eventos transformadores que você não pode evitar
• Você sentirá uma tensão entre querer manter controle e a necessidade urgente de transformar - não há como evitar a mudança
• Período onde crises profundas chegam de forma abrupta - você precisa transformar ou ser destruído - não há meio termo
• Sua rotina diária pode ser completamente virada de cabeça para baixo por crises que exigem renascimento total
• A energia de Plutão força você a enfrentar o que precisa morrer - você pode resistir, mas a transformação virá de qualquer forma, através de crise

**O que fazer na prática:**
Encare crises como oportunidades de transformação. Se o trânsito afeta seu Sol, permita mudanças pessoais profundas. Se afeta sua Lua, transforme padrões emocionais. Se afeta Mercúrio, renove pensamento. Se afeta Vênus, transforme relacionamentos. Se afeta Marte, canalize poder de forma construtiva.

**Exemplos práticos:**
• Se afeta seu Sol: "Enfrentei uma crise profunda que exigiu transformação total. Tive que renascer completamente como pessoa."
• Se afeta sua Lua: "Minhas emoções foram desestabilizadas por uma crise transformadora. Tive que transformar padrões emocionais profundos."
• Se afeta Mercúrio: "Minha forma de pensar foi completamente renovada através de uma crise. Tive que reconstruir tudo do zero."
• Se afeta Vênus: "Meus relacionamentos passaram por uma crise transformadora. Tive que deixar ir o que não servia mais."
• Se afeta Marte: "Minha forma de agir foi completamente transformada através de uma crise. Aprendi a usar poder de forma construtiva." """,

        ('Plutão', 'sextil'): f"""**O que é um {aspect_display}?**
Um sextil forma um ângulo de 60 graus entre {transit_planet} e seu {natal_point}. Plutão oferece oportunidades suaves de transformação e renovação.

**Como isso impacta sua rotina:**
• Oportunidades de transformação aparecem de forma suave e natural
• Você sente uma leve necessidade de renovar a área relacionada ao seu {natal_point}
• Período favorável para pequenas transformações e renovações
• Transformações fluem de forma mais fácil, mas de forma mais sutil que um trígono
• A energia de Plutão trabalha a seu favor de forma suave, trazendo renovação sem crises profundas

**O que fazer na prática:**
Aproveite para fazer pequenas transformações. Se o trânsito afeta seu Sol, permita transformações positivas. Se afeta sua Lua, renove padrões emocionais. Se afeta Mercúrio, renove pensamento. Se afeta Vênus, transforme relacionamentos positivamente. Se afeta Marte, canalize poder de forma construtiva.

**Exemplos práticos:**
• Se afeta seu Sol: "Transformações positivas chegaram de forma natural. Me sinto renovado e mais autêntico."
• Se afeta sua Lua: "Renovei padrões emocionais de forma suave. Sinto mais equilíbrio emocional."
• Se afeta Mercúrio: "Renovei minha forma de pensar de forma natural. Sinto mais clareza mental."
• Se afeta Vênus: "Transformei relacionamentos de forma positiva. Sinto conexões mais profundas."
• Se afeta Marte: "Canalizei poder de forma construtiva. Sinto mais força e determinação." """,

        ('Plutão', 'trígono'): f"""**O que é uma {aspect_display}?**
Um trígono forma um ângulo de 120 graus entre {transit_planet} e seu {natal_point}. Plutão facilita transformação positiva e renovação.

**Como isso impacta sua rotina:**
• Transformações positivas podem acontecer de forma mais suave
• Período favorável para renovação profunda
• Menos tensão e mais facilidade em transformar
• Oportunidades de renascer de forma positiva
• Crescimento através de poder pessoal construtivo

**O que fazer na prática:**
Aproveite para renovar-se. Se o trânsito afeta seu Sol, permita transformações positivas. Se afeta sua Lua, renove padrões emocionais. Se afeta Mercúrio, renove pensamento. Se afeta Vênus, transforme relacionamentos positivamente. Se afeta Marte, canalize poder de forma construtiva."""
    }
    
    # Descrição especial para retorno de Saturno
    if transit_type == 'saturn-return':
        return f"""**O que é um Retorno de Saturno?**
O Retorno de Saturno acontece quando Saturno completa uma volta completa ao redor do Sol e retorna à posição exata que ocupava no seu mapa natal. É um marco astrológico importante que ocorre aproximadamente aos 29-30 anos, 58-59 anos e 87-88 anos.

**Como isso impacta sua rotina:**
• Período de amadurecimento e definição de estruturas na sua vida
• Você será testado em áreas relacionadas a responsabilidade, disciplina e compromissos de longo prazo
• Necessidade de avaliar o que construiu até agora e o que precisa ser ajustado
• Recompensas por trabalho árduo e esforços anteriores
• Período de consolidar conquistas e estabelecer bases sólidas para o futuro

**O que fazer na prática:**
Este é um momento crucial para estruturar sua vida. Avalie suas responsabilidades, compromissos e objetivos de longo prazo. Seja disciplinado e paciente com processos que exigem tempo. Este é o momento de colher recompensas por esforços passados e estabelecer bases sólidas para o futuro. Não tenha medo de assumir responsabilidades que realmente importam para você."""
    
    # Buscar descrição específica ou usar genérica
    key = (transit_planet, aspect_type)
    description = transit_descriptions.get(key)
    
    if not description:
        # Descrição genérica se não encontrar específica
        description = f"""**O que é uma {aspect_names_pt.get(aspect_type, aspect_type)}?**
Uma {aspect_type} acontece quando {transit_planet} forma um aspecto específico com seu {natal_point} no mapa natal.

**Como isso impacta sua rotina:**
Este trânsito influencia a área da sua vida relacionada ao seu {natal_point}. Preste atenção às mudanças e oportunidades que aparecem durante este período.

**O que fazer na prática:**
Esteja consciente das influências deste trânsito e use-as de forma construtiva na sua rotina diária."""
    
    return description


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

