"""
Valida os aspectos reportados para 27-28/12/2025 para verificar se estão corretos.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
import ephem
from app.services.best_timing_calculator import (
    calculate_house_cusp,
    ACTION_HOUSES
)
from app.services.astrology_calculator import calculate_planet_position
from app.services.transits_calculator import calculate_aspect_angle, get_aspect_type

# Dados do usuário
birth_date = datetime(1981, 10, 20)
birth_time = "13:30"
latitude = -23.5505
longitude = -46.6333

# Datas a validar
test_dates = [
    ("2025-12-27T18:00:00", "27/12/2025 18:00"),
    ("2025-12-28T00:00:00", "28/12/2025 00:00"),
    ("2025-12-24T12:00:00", "24/12/2025 12:00"),  # Data problemática
]

action_id = 'mudanca_carreira'
action_config = ACTION_HOUSES[action_id]

print("="*80)
print("VALIDAÇÃO DE ASPECTOS - DATAS ESPECÍFICAS")
print("="*80)
print()

# Criar observador para mapa natal
birth_observer = ephem.Observer()
birth_observer.lat = str(latitude)
birth_observer.lon = str(longitude)
time_parts = birth_time.split(":")
hour = int(time_parts[0])
minute = int(time_parts[1])
birth_datetime = birth_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
birth_observer.date = birth_datetime.strftime('%Y/%m/%d %H:%M:%S')

# Calcular cúspides das casas
print("Cúspides das casas (mapa natal):")
house_cusps = {}
for house_num in action_config['primary_houses'] + action_config['secondary_houses']:
    cusp = calculate_house_cusp(
        birth_observer,
        house_num,
        birth_date,
        birth_time,
        latitude,
        longitude
    )
    house_cusps[house_num] = cusp
    is_primary = house_num in action_config['primary_houses']
    house_type = "PRIMÁRIA" if is_primary else "SECUNDÁRIA"
    print(f"  Casa {house_num} ({house_type}): {cusp:.6f}°")
print()

# Validar cada data
for date_iso, date_display in test_dates:
    print("="*80)
    print(f"VALIDANDO: {date_display}")
    print("="*80)
    print()
    
    # Parse da data
    from dateutil import parser
    check_datetime = parser.parse(date_iso)
    
    # Criar observador para trânsito
    transit_observer = ephem.Observer()
    transit_observer.lat = str(latitude)
    transit_observer.lon = str(longitude)
    transit_observer.date = check_datetime.strftime('%Y/%m/%d %H:%M:%S')
    
    # Calcular posição do Sol
    sun_longitude = calculate_planet_position(transit_observer, 'sun')
    print(f"Sol em trânsito: {sun_longitude:.6f}°")
    print()
    
    # Verificar aspectos
    aspects_detected = []
    score = 0
    
    for house_num in sorted(house_cusps.keys()):
        house_cusp = house_cusps[house_num]
        is_primary = house_num in action_config['primary_houses']
        house_type = "PRIMÁRIA" if is_primary else "SECUNDÁRIA"
        
        angle = calculate_aspect_angle(sun_longitude, house_cusp)
        aspect_type = get_aspect_type(angle, orb=8.0)
        
        print(f"Casa {house_num} ({house_type}): {house_cusp:.6f}°")
        print(f"  Ângulo: {angle:.6f}°")
        print(f"  Aspecto (orbe 8°): {aspect_type if aspect_type else 'Nenhum'}")
        
        if aspect_type and aspect_type in action_config['preferred_aspects']:
            if is_primary:
                if aspect_type == 'trígono':
                    points = 10
                elif aspect_type == 'sextil':
                    points = 7
                elif aspect_type == 'conjunção':
                    points = 8
                else:
                    points = 0
            else:
                if aspect_type == 'trígono':
                    points = 5
                elif aspect_type == 'sextil':
                    points = 3
                elif aspect_type == 'conjunção':
                    points = 4
                else:
                    points = 0
            
            if points > 0:
                score += points
                aspects_detected.append({
                    'house': house_num,
                    'aspect': aspect_type,
                    'points': points,
                    'is_primary': is_primary
                })
                print(f"  ✓ ASPECTO VÁLIDO! +{points} pontos")
            else:
                print(f"  ⚠️ Aspecto não está nos preferidos ou não dá pontos")
        else:
            if aspect_type:
                print(f"  ⚠️ Aspecto '{aspect_type}' não está nos preferidos")
            else:
                print(f"  ✗ Nenhum aspecto detectado")
        print()
    
    print(f"Score total: {score}")
    print(f"Aspectos detectados: {len(aspects_detected)}")
    if aspects_detected:
        print("Detalhes:")
        for asp in aspects_detected:
            print(f"  - Casa {asp['house']} ({'PRIMÁRIA' if asp['is_primary'] else 'SECUNDÁRIA'}): {asp['aspect']} (+{asp['points']} pontos)")
    print()
    print()

