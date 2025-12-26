"""
Serviço para calcular informações do dia atual:
- Data formatada
- Fase lunar
- Signo da Lua
- Informações astrológicas do dia

Usa Swiss Ephemeris (biblioteca padrão) para todos os cálculos.
"""

import ephem
from datetime import datetime
from typing import Dict, Optional
from app.services.astrology_calculator import get_zodiac_sign

# Tentar importar Swiss Ephemeris, usar fallback se não disponível
try:
    from app.services.swiss_ephemeris_calculator import create_kr_instance, get_planet_longitude
    HAS_SWISS_EPHEMERIS = True
except ImportError:
    HAS_SWISS_EPHEMERIS = False
    from app.services.astrology_calculator import calculate_planet_position


def calculate_moon_phase(moon_longitude: float, sun_longitude: float) -> str:
    """
    Calcula a fase lunar baseado nas posições do Sol e da Lua.
    
    Args:
        moon_longitude: Longitude eclíptica da Lua
        sun_longitude: Longitude eclíptica do Sol
    
    Returns:
        Nome da fase lunar em português
    """
    # Calcular diferença angular
    angle = (moon_longitude - sun_longitude) % 360
    
    # Determinar fase baseado no ângulo
    if angle < 22.5 or angle >= 337.5:
        return "Lua Nova"
    elif angle < 67.5:
        return "Lua Crescente"
    elif angle < 112.5:
        return "Quarto Crescente"
    elif angle < 157.5:
        return "Lua Crescente Gibosa"
    elif angle < 202.5:
        return "Lua Cheia"
    elif angle < 247.5:
        return "Lua Minguante Gibosa"
    elif angle < 292.5:
        return "Quarto Minguante"
    else:  # angle < 337.5
        return "Lua Minguante"


def get_daily_info(
    latitude: float = -23.5505,  # São Paulo por padrão
    longitude: float = -46.6333,
    target_date: Optional[datetime] = None
) -> Dict[str, any]:
    """
    Calcula informações astrológicas do dia atual.
    
    Args:
        latitude: Latitude do local
        longitude: Longitude do local
        target_date: Data para calcular (padrão: hoje)
    
    Returns:
        Dicionário com:
        - date: Data formatada (ex: "Segunda, 5 de Dezembro de 2025")
        - day_name: Nome do dia da semana
        - day: Dia do mês
        - month: Nome do mês
        - year: Ano
        - moon_phase: Fase lunar (ex: "Lua Crescente")
        - moon_sign: Signo da Lua (ex: "Aquário")
        - moon_phase_description: Descrição da fase (ex: "Lua Crescente em Aquário")
    """
    if target_date is None:
        target_date = datetime.now()
    
    # Formatar data
    days_of_week = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 
                    'Sexta-feira', 'Sábado', 'Domingo']
    months = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
              'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    
    day_name = days_of_week[target_date.weekday()]
    day = target_date.day
    month = months[target_date.month - 1]
    year = target_date.year
    
    date_formatted = f"{day_name}, {day} de {month} de {year}"
    
    # Calcular posições usando Swiss Ephemeris (biblioteca padrão)
    try:
        if HAS_SWISS_EPHEMERIS:
            # Usar função do best_timing_calculator que já tem a lógica correta
            from app.services.best_timing_calculator import calculate_planet_position_swiss
            
            # A função retorna float (longitude) diretamente
            moon_longitude = calculate_planet_position_swiss(
                target_date, latitude, longitude, 'moon'
            )
            sun_longitude = calculate_planet_position_swiss(
                target_date, latitude, longitude, 'sun'
            )
        else:
            # Fallback para PyEphem
            observer = ephem.Observer()
            observer.lat = str(latitude)
            observer.lon = str(longitude)
            observer.date = target_date.strftime('%Y/%m/%d %H:%M:%S')
            
            moon_longitude = calculate_planet_position(observer, 'moon')
            sun_longitude = calculate_planet_position(observer, 'sun')
        
        # Obter signo da Lua
        moon_sign_info = get_zodiac_sign(moon_longitude)
        moon_sign = moon_sign_info['sign']
        
        # Calcular fase lunar
        moon_phase = calculate_moon_phase(moon_longitude, sun_longitude)
        moon_phase_description = f"{moon_phase} em {moon_sign}"
        
    except Exception as e:
        print(f"[ERROR] Erro ao calcular informações lunares: {e}")
        # Fallback
        moon_sign = "N/A"
        moon_phase = "N/A"
        moon_phase_description = "N/A"
    
    return {
        'date': date_formatted,
        'day_name': day_name,
        'day': day,
        'month': month,
        'year': year,
        'moon_phase': moon_phase,
        'moon_sign': moon_sign,
        'moon_phase_description': moon_phase_description,
        'calculated_at': target_date.isoformat()
    }

