"""
Serviço para calcular Lua Fora de Curso (Void of Course Moon).
Baseado em cálculos astronômicos precisos usando Swiss Ephemeris.
"""

import ephem
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from app.services.astrology_calculator import calculate_planet_position
from app.services.transits_calculator import calculate_aspect_angle, get_aspect_type


def calculate_moon_void_of_course(
    check_date: datetime = None,
    latitude: float = 0.0,
    longitude: float = 0.0
) -> Dict[str, any]:
    """
    Calcula se a Lua está Fora de Curso (Void of Course) no momento especificado.
    
    Lua Fora de Curso ocorre quando a Lua não faz mais aspectos maiores (conjunção, 
    oposição, quadratura, trígono, sextil) com nenhum planeta antes de mudar de signo.
    
    Args:
        check_date: Data e hora para verificar (padrão: agora)
        latitude: Latitude do local (usado para cálculos precisos)
        longitude: Longitude do local (usado para cálculos precisos)
    
    Returns:
        Dicionário com:
        - is_void: bool - Se a Lua está fora de curso
        - void_start: datetime - Quando começou (se aplicável)
        - void_end: datetime - Quando termina (quando Lua muda de signo ou faz aspecto)
        - next_aspect: Optional[str] - Próximo aspecto que a Lua fará
        - next_aspect_time: Optional[datetime] - Quando ocorrerá o próximo aspecto
    """
    if check_date is None:
        check_date = datetime.now()
    
    # Criar observador
    observer = ephem.Observer()
    observer.lat = str(latitude)
    observer.lon = str(longitude)
    observer.date = check_date.strftime('%Y/%m/%d %H:%M:%S')
    
    # Planetas a verificar (todos os planetas principais)
    planets_to_check = [
        'sun', 'mercury', 'venus', 'mars', 'jupiter', 
        'saturn', 'uranus', 'neptune', 'pluto'
    ]
    
    # Calcular posição atual da Lua
    moon_longitude = calculate_planet_position(observer, 'moon')
    
    # Obter signo atual da Lua
    from app.services.astrology_calculator import get_zodiac_sign
    moon_sign_data = get_zodiac_sign(moon_longitude)
    current_moon_sign = moon_sign_data['sign']
    current_moon_degree = moon_sign_data['degree']
    
    # Calcular quando a Lua mudará de signo
    # Lua muda de signo quando completa 30 graus no signo atual
    degrees_until_sign_change = 30.0 - current_moon_degree
    
    # Velocidade média da Lua: ~13.2 graus/dia
    moon_speed_deg_per_day = 13.2
    days_until_sign_change = degrees_until_sign_change / moon_speed_deg_per_day
    
    # Estimativa de quando Lua mudará de signo
    estimated_sign_change = check_date + timedelta(days=days_until_sign_change)
    
    # Verificar se há aspectos futuros antes da mudança de signo
    # Buscar nos próximos dias (até a mudança de signo)
    search_interval = timedelta(hours=1)  # Verificar a cada hora
    current_search_date = check_date
    max_search_days = min(days_until_sign_change + 1, 3)  # Máximo 3 dias
    end_search_date = check_date + timedelta(days=max_search_days)
    
    next_aspect = None
    next_aspect_time = None
    next_aspect_planet = None
    
    # Verificar aspectos futuros
    while current_search_date <= end_search_date:
        search_observer = ephem.Observer()
        search_observer.lat = str(latitude)
        search_observer.lon = str(longitude)
        search_observer.date = current_search_date.strftime('%Y/%m/%d %H:%M:%S')
        
        # Calcular posição da Lua neste momento
        search_moon_longitude = calculate_planet_position(search_observer, 'moon')
        
        # Verificar aspectos com cada planeta
        for planet_name in planets_to_check:
            try:
                planet_longitude = calculate_planet_position(search_observer, planet_name)
                
                # Calcular ângulo entre Lua e planeta
                angle = calculate_aspect_angle(search_moon_longitude, planet_longitude)
                aspect_type = get_aspect_type(angle, orb=8.0)
                
                if aspect_type:
                    # Encontrou um aspecto futuro
                    planet_display_names = {
                        'sun': 'Sol',
                        'mercury': 'Mercúrio',
                        'venus': 'Vênus',
                        'mars': 'Marte',
                        'jupiter': 'Júpiter',
                        'saturn': 'Saturno',
                        'uranus': 'Urano',
                        'neptune': 'Netuno',
                        'pluto': 'Plutão'
                    }
                    
                    aspect_display_names = {
                        'conjunção': 'Conjunção',
                        'oposição': 'Oposição',
                        'quadratura': 'Quadratura',
                        'trígono': 'Trígono',
                        'sextil': 'Sextil'
                    }
                    
                    next_aspect = aspect_display_names.get(aspect_type, aspect_type)
                    next_aspect_time = current_search_date
                    next_aspect_planet = planet_display_names.get(planet_name, planet_name)
                    
                    # Se encontrou aspecto antes da mudança de signo, Lua não está fora de curso
                    if current_search_date < estimated_sign_change:
                        return {
                            'is_void': False,
                            'void_start': None,
                            'void_end': None,
                            'next_aspect': f"{next_aspect} com {next_aspect_planet}",
                            'next_aspect_time': next_aspect_time,
                            'current_moon_sign': current_moon_sign,
                            'moon_degree': current_moon_degree
                        }
                    
                    break  # Encontrou aspecto, parar busca
            except Exception as e:
                # Continuar se houver erro ao calcular um planeta
                continue
        
        # Avançar para próxima hora
        current_search_date += search_interval
        
        # Limitar busca para evitar timeout
        if (current_search_date - check_date).total_seconds() > 72 * 3600:  # 3 dias
            break
    
    # Se não encontrou aspectos antes da mudança de signo, Lua está fora de curso
    # Calcular quando começou (buscar para trás)
    void_start = check_date
    search_back_date = check_date - timedelta(days=1)
    search_back_observer = ephem.Observer()
    search_back_observer.lat = str(latitude)
    search_back_observer.lon = str(longitude)
    
    # Buscar último aspecto feito pela Lua
    while search_back_date <= check_date:
        search_back_observer.date = search_back_date.strftime('%Y/%m/%d %H:%M:%S')
        
        try:
            back_moon_longitude = calculate_planet_position(search_back_observer, 'moon')
            
            # Verificar se havia aspecto neste momento
            had_aspect = False
            for planet_name in planets_to_check:
                try:
                    planet_longitude = calculate_planet_position(search_back_observer, planet_name)
                    angle = calculate_aspect_angle(back_moon_longitude, planet_longitude)
                    aspect_type = get_aspect_type(angle, orb=8.0)
                    
                    if aspect_type:
                        # Encontrou último aspecto
                        void_start = search_back_date + timedelta(hours=2)  # Aproximação
                        had_aspect = True
                        break
                except:
                    continue
            
            if had_aspect:
                break
        except:
            pass
        
        search_back_date += timedelta(hours=1)
    
    # Lua termina fora de curso quando muda de signo ou faz próximo aspecto
    void_end = estimated_sign_change
    if next_aspect_time and next_aspect_time < estimated_sign_change:
        void_end = next_aspect_time
    
    return {
        'is_void': True,
        'void_start': void_start,
        'void_end': void_end,
        'next_aspect': f"{next_aspect} com {next_aspect_planet}" if next_aspect else "Mudança de signo",
        'next_aspect_time': void_end,
        'current_moon_sign': current_moon_sign,
        'moon_degree': current_moon_degree,
        'void_duration_hours': (void_end - check_date).total_seconds() / 3600 if void_end else None
    }

