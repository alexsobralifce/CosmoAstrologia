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
Aproveite este momento para expandir seus horizontes. Se o trânsito afeta seu Sol, foque em projetos pessoais. Se afeta sua Lua, cuide mais das suas emoções e necessidades. Se afeta Mercúrio, é hora de estudar e comunicar. Se afeta Vênus, invista em relacionamentos e criatividade. Se afeta Marte, canalize sua energia em ações concretas.""",

        ('Júpiter', 'oposição'): f"""**O que é uma {aspect_display}?**
Uma oposição acontece quando {transit_planet} está exatamente oposto ao seu {natal_point} no mapa. É como um espelho que reflete e amplifica as dinâmicas dessa área.

**Como isso impacta sua rotina:**
• Você pode sentir uma tensão entre suas necessidades internas e oportunidades externas
• Tendência a excessos ou exageros na área relacionada ao seu {natal_point}
• Necessidade de encontrar equilíbrio entre diferentes aspectos da vida
• Pode haver conflitos entre o que você quer e o que o mundo oferece
• Período de aprendizado sobre limites e moderação

**O que fazer na prática:**
Evite exageros e busque equilíbrio. Se o trânsito afeta seu Sol, não se sobrecarregue com projetos. Se afeta sua Lua, cuide para não deixar emoções dominarem. Se afeta Mercúrio, evite prometer mais do que pode cumprir. Se afeta Vênus, não idealize demais relacionamentos. Se afeta Marte, controle impulsos e canalize energia de forma construtiva.""",

        ('Júpiter', 'quadratura'): f"""**O que é uma {aspect_display}?**
Uma quadratura forma um ângulo de 90 graus entre {transit_planet} e seu {natal_point}. É um aspecto desafiador que cria tensão e necessidade de ação.

**Como isso impacta sua rotina:**
• Você enfrentará desafios que exigirão ajustes na área relacionada ao seu {natal_point}
• Pode sentir frustração ou impaciência quando as coisas não saem como esperado
• Necessidade de trabalhar mais para alcançar seus objetivos
• Oportunidades podem vir acompanhadas de obstáculos
• Período de crescimento através de superação de dificuldades

**O que fazer na prática:**
Encare os desafios como oportunidades de crescimento. Se o trânsito afeta seu Sol, seja paciente com projetos pessoais. Se afeta sua Lua, trabalhe suas emoções de forma consciente. Se afeta Mercúrio, revise sua comunicação. Se afeta Vênus, seja realista em relacionamentos. Se afeta Marte, canalize energia de forma disciplinada.""",

        ('Júpiter', 'trígono'): f"""**O que é uma {aspect_display}?**
Um trígono forma um ângulo de 120 graus entre {transit_planet} e seu {natal_point}. É um aspecto harmonioso que facilita o fluxo de energia.

**Como isso impacta sua rotina:**
• As coisas tendem a fluir de forma mais natural e fácil
• Oportunidades aparecem sem muito esforço
• Você sente mais confiança e otimismo no dia a dia
• Período favorável para desenvolvimento e crescimento
• Menos tensão e mais harmonia nas áreas relacionadas ao seu {natal_point}

**O que fazer na prática:**
Aproveite este momento harmonioso. Se o trânsito afeta seu Sol, invista em projetos pessoais. Se afeta sua Lua, cuide bem das suas emoções. Se afeta Mercúrio, comunique-se e aprenda. Se afeta Vênus, invista em relacionamentos e criatividade. Se afeta Marte, aja com confiança.""",

        ('Saturno', 'conjunção'): f"""**O que é uma {aspect_display}?**
Uma conjunção acontece quando {transit_planet} se alinha exatamente com seu {natal_point}. Saturno traz lições de responsabilidade, estrutura e disciplina.

**Como isso impacta sua rotina:**
• Você sentirá necessidade de estruturar e organizar melhor a área relacionada ao seu {natal_point}
• Pode haver restrições ou limitações que exigem paciência
• Período de amadurecimento e aprendizado sobre responsabilidades
• Necessidade de trabalhar com disciplina e consistência
• Recompensas virão através de esforço e dedicação

**O que fazer na prática:**
Seja disciplinado e paciente. Se o trânsito afeta seu Sol, estruture seus projetos pessoais. Se afeta sua Lua, estabeleça rotinas emocionais saudáveis. Se afeta Mercúrio, organize seus estudos e comunicação. Se afeta Vênus, seja sério em relacionamentos. Se afeta Marte, canalize energia de forma disciplinada.""",

        ('Saturno', 'oposição'): f"""**O que é uma {aspect_display}?**
Uma oposição acontece quando {transit_planet} está exatamente oposto ao seu {natal_point}. Saturno testa seus compromissos e estruturas.

**Como isso impacta sua rotina:**
• Você pode sentir tensão entre suas necessidades pessoais e responsabilidades externas
• Necessidade de encontrar equilíbrio entre liberdade e compromissos
• Testes sobre limites e estruturas na área relacionada ao seu {natal_point}
• Período de aprendizado sobre o que realmente importa
• Pode haver pressão externa que exige ajustes

**O que fazer na prática:**
Encontre equilíbrio entre suas necessidades e responsabilidades. Se o trânsito afeta seu Sol, não se sobrecarregue. Se afeta sua Lua, estabeleça limites emocionais. Se afeta Mercúrio, seja claro em compromissos. Se afeta Vênus, equilibre relacionamentos. Se afeta Marte, controle impulsos.""",

        ('Saturno', 'quadratura'): f"""**O que é uma {aspect_display}?**
Uma quadratura forma um ângulo de 90 graus entre {transit_planet} e seu {natal_point}. Saturno cria desafios que exigem trabalho árduo.

**Como isso impacta sua rotina:**
• Você enfrentará obstáculos e restrições na área relacionada ao seu {natal_point}
• Necessidade de trabalhar mais e com mais disciplina
• Pode sentir frustração ou limitações
• Período de aprendizado através de dificuldades
• Recompensas virão apenas após esforço consistente

**O que fazer na prática:**
Seja persistente e disciplinado. Se o trânsito afeta seu Sol, trabalhe com paciência em projetos. Se afeta sua Lua, gerencie emoções com maturidade. Se afeta Mercúrio, revise e organize comunicação. Se afeta Vênus, seja realista em relacionamentos. Se afeta Marte, canalize energia de forma controlada.""",

        ('Saturno', 'trígono'): f"""**O que é uma {aspect_display}?**
Um trígono forma um ângulo de 120 graus entre {transit_planet} e seu {natal_point}. Saturno facilita estruturação e organização.

**Como isso impacta sua rotina:**
• Você sentirá facilidade em estruturar e organizar a área relacionada ao seu {natal_point}
• Período favorável para estabelecer rotinas e hábitos saudáveis
• Recompensas por esforços anteriores
• Menos tensão e mais estabilidade
• Crescimento através de disciplina natural

**O que fazer na prática:**
Aproveite para estruturar sua vida. Se o trânsito afeta seu Sol, organize projetos pessoais. Se afeta sua Lua, estabeleça rotinas emocionais. Se afeta Mercúrio, organize estudos. Se afeta Vênus, estruture relacionamentos. Se afeta Marte, canalize energia de forma organizada.""",

        ('Urano', 'conjunção'): f"""**O que é uma {aspect_display}?**
Uma conjunção acontece quando {transit_planet} se alinha exatamente com seu {natal_point}. Urano traz mudanças súbitas e inovação.

**Como isso impacta sua rotina:**
• Você pode experimentar mudanças inesperadas na área relacionada ao seu {natal_point}
• Necessidade de liberdade e independência aumenta
• Período de inovação e quebra de padrões antigos
• Pode haver eventos súbitos que alteram sua rotina
• Necessidade de adaptação rápida a novas situações

**O que fazer na prática:**
Esteja aberto a mudanças. Se o trânsito afeta seu Sol, aceite transformações pessoais. Se afeta sua Lua, permita mudanças emocionais. Se afeta Mercúrio, experimente novas formas de comunicação. Se afeta Vênus, esteja aberto a relacionamentos diferentes. Se afeta Marte, canalize energia de forma inovadora.""",

        ('Urano', 'oposição'): f"""**O que é uma {aspect_display}?**
Uma oposição acontece quando {transit_planet} está exatamente oposto ao seu {natal_point}. Urano cria tensão entre estabilidade e mudança.

**Como isso impacta sua rotina:**
• Você pode sentir conflito entre necessidade de estabilidade e desejo de mudança
• Tensão entre rotina e liberdade
• Período de questionamento sobre estruturas estabelecidas
• Necessidade de encontrar equilíbrio entre segurança e inovação
• Pode haver pressão externa por mudanças

**O que fazer na prática:**
Encontre equilíbrio entre estabilidade e mudança. Se o trânsito afeta seu Sol, não rejeite mudanças necessárias. Se afeta sua Lua, permita evolução emocional. Se afeta Mercúrio, esteja aberto a novas ideias. Se afeta Vênus, não se prenda a relacionamentos antigos. Se afeta Marte, canalize energia de forma inovadora.""",

        ('Urano', 'quadratura'): f"""**O que é uma {aspect_display}?**
Uma quadratura forma um ângulo de 90 graus entre {transit_planet} e seu {natal_point}. Urano cria rupturas e necessidade de adaptação.

**Como isso impacta sua rotina:**
• Você enfrentará mudanças inesperadas que podem perturbar sua rotina
• Necessidade de adaptação rápida a situações novas
• Pode haver rupturas ou interrupções na área relacionada ao seu {natal_point}
• Período de aprendizado sobre flexibilidade
• Necessidade de quebrar padrões antigos

**O que fazer na prática:**
Seja flexível e adaptável. Se o trânsito afeta seu Sol, aceite mudanças pessoais. Se afeta sua Lua, gerencie emoções com flexibilidade. Se afeta Mercúrio, adapte-se a novas formas de comunicação. Se afeta Vênus, esteja aberto a mudanças em relacionamentos. Se afeta Marte, canalize energia de forma inovadora.""",

        ('Urano', 'trígono'): f"""**O que é uma {aspect_display}?**
Um trígono forma um ângulo de 120 graus entre {transit_planet} e seu {natal_point}. Urano facilita mudanças positivas e inovação.

**Como isso impacta sua rotina:**
• Mudanças positivas podem acontecer de forma mais suave
• Período favorável para inovação e experimentação
• Menos tensão e mais facilidade em adaptar-se
• Oportunidades de quebrar padrões antigos de forma positiva
• Crescimento através de liberdade e independência

**O que fazer na prática:**
Aproveite para inovar. Se o trânsito afeta seu Sol, experimente novas formas de expressão. Se afeta sua Lua, permita evolução emocional. Se afeta Mercúrio, explore novas ideias. Se afeta Vênus, esteja aberto a relacionamentos diferentes. Se afeta Marte, canalize energia de forma criativa.""",

        ('Netuno', 'conjunção'): f"""**O que é uma {aspect_display}?**
Uma conjunção acontece quando {transit_planet} se alinha exatamente com seu {natal_point}. Netuno traz inspiração espiritual e criatividade.

**Como isso impacta sua rotina:**
• Você pode sentir maior sensibilidade e intuição na área relacionada ao seu {natal_point}
• Período de inspiração artística e espiritual
• Necessidade de conectar-se com algo maior que você
• Pode haver confusão ou falta de clareza em alguns momentos
• Oportunidades de crescimento através de compaixão e criatividade

**O que fazer na prática:**
Conecte-se com sua intuição. Se o trânsito afeta seu Sol, explore sua espiritualidade. Se afeta sua Lua, cuide de suas emoções com compaixão. Se afeta Mercúrio, use criatividade na comunicação. Se afeta Vênus, invista em arte e relacionamentos compassivos. Se afeta Marte, canalize energia de forma criativa.""",

        ('Netuno', 'oposição'): f"""**O que é uma {aspect_display}?**
Uma oposição acontece quando {transit_planet} está exatamente oposto ao seu {natal_point}. Netuno pode trazer ilusões e necessidade de clareza.

**Como isso impacta sua rotina:**
• Você pode sentir confusão ou falta de clareza na área relacionada ao seu {natal_point}
• Necessidade de discernir entre realidade e ilusão
• Período de aprendizado sobre limites e verdade
• Pode haver idealização excessiva
• Necessidade de encontrar equilíbrio entre sonhos e realidade

**O que fazer na prática:**
Busque clareza e discernimento. Se o trânsito afeta seu Sol, seja realista sobre si mesmo. Se afeta sua Lua, gerencie emoções com clareza. Se afeta Mercúrio, comunique-se de forma clara. Se afeta Vênus, seja realista em relacionamentos. Se afeta Marte, canalize energia de forma consciente.""",

        ('Netuno', 'quadratura'): f"""**O que é uma {aspect_display}?**
Uma quadratura forma um ângulo de 90 graus entre {transit_planet} e seu {natal_point}. Netuno pode trazer desorientação e necessidade de discernimento.

**Como isso impacta sua rotina:**
• Você pode sentir confusão ou falta de direção na área relacionada ao seu {natal_point}
• Necessidade de trabalhar com discernimento e clareza
• Pode haver ilusões ou enganos que precisam ser descobertos
• Período de aprendizado sobre verdade e realidade
• Necessidade de encontrar equilíbrio entre sonhos e ação prática

**O que fazer na prática:**
Seja prático e discernente. Se o trânsito afeta seu Sol, busque clareza sobre seus objetivos. Se afeta sua Lua, gerencie emoções com discernimento. Se afeta Mercúrio, comunique-se claramente. Se afeta Vênus, seja realista em relacionamentos. Se afeta Marte, canalize energia de forma consciente.""",

        ('Netuno', 'trígono'): f"""**O que é uma {aspect_display}?**
Um trígono forma um ângulo de 120 graus entre {transit_planet} e seu {natal_point}. Netuno facilita inspiração artística e conexão espiritual.

**Como isso impacta sua rotina:**
• Você sentirá maior inspiração e criatividade na área relacionada ao seu {natal_point}
• Período favorável para expressão artística e espiritual
• Conexão mais fácil com intuição e compaixão
• Menos confusão e mais clareza espiritual
• Crescimento através de arte e espiritualidade

**O que fazer na prática:**
Aproveite para criar e inspirar-se. Se o trânsito afeta seu Sol, explore sua espiritualidade. Se afeta sua Lua, conecte-se com suas emoções de forma compassiva. Se afeta Mercúrio, use criatividade na comunicação. Se afeta Vênus, invista em arte e relacionamentos. Se afeta Marte, canalize energia de forma criativa.""",

        ('Plutão', 'conjunção'): f"""**O que é uma {aspect_display}?**
Uma conjunção acontece quando {transit_planet} se alinha exatamente com seu {natal_point}. Plutão traz transformação profunda e renascimento.

**Como isso impacta sua rotina:**
• Você passará por transformações profundas na área relacionada ao seu {natal_point}
• Necessidade de deixar ir padrões antigos e renascer
• Período de poder pessoal e transformação
• Pode haver crises que levam a crescimento
• Oportunidades de renovação completa

**O que fazer na prática:**
Aceite transformações necessárias. Se o trânsito afeta seu Sol, permita mudanças profundas em sua identidade. Se afeta sua Lua, transforme padrões emocionais. Se afeta Mercúrio, renove sua forma de pensar. Se afeta Vênus, transforme relacionamentos. Se afeta Marte, canalize poder de forma construtiva.""",

        ('Plutão', 'oposição'): f"""**O que é uma {aspect_display}?**
Uma oposição acontece quando {transit_planet} está exatamente oposto ao seu {natal_point}. Plutão cria confrontos com poder e necessidade de transformação.

**Como isso impacta sua rotina:**
• Você pode enfrentar confrontos ou desafios de poder na área relacionada ao seu {natal_point}
• Necessidade de transformar dinâmicas antigas
• Período de aprendizado sobre poder pessoal
• Pode haver tensões que exigem transformação
• Necessidade de encontrar equilíbrio entre controle e libertação

**O que fazer na prática:**
Transforme dinâmicas antigas. Se o trânsito afeta seu Sol, não tente controlar demais. Se afeta sua Lua, transforme padrões emocionais. Se afeta Mercúrio, renove comunicação. Se afeta Vênus, transforme relacionamentos. Se afeta Marte, canalize poder de forma consciente.""",

        ('Plutão', 'quadratura'): f"""**O que é uma {aspect_display}?**
Uma quadratura forma um ângulo de 90 graus entre {transit_planet} e seu {natal_point}. Plutão cria crises transformadoras.

**Como isso impacta sua rotina:**
• Você enfrentará crises que exigem transformação na área relacionada ao seu {natal_point}
• Necessidade de mudanças profundas e urgentes
• Pode haver tensões ou conflitos que levam a crescimento
• Período de aprendizado através de dificuldades transformadoras
• Necessidade de renascer através de desafios

**O que fazer na prática:**
Encare crises como oportunidades de transformação. Se o trânsito afeta seu Sol, permita mudanças pessoais profundas. Se afeta sua Lua, transforme padrões emocionais. Se afeta Mercúrio, renove pensamento. Se afeta Vênus, transforme relacionamentos. Se afeta Marte, canalize poder de forma construtiva.""",

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

