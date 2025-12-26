"""
Valida os aspectos reportados para 4 e 13 de dezembro de 2025 (ação: negociação).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
import ephem
from app.services.best_timing_calculator import (
    calculate_house_cusp,
    ACTION_HOUSES,
    calculate_planet_position_swiss
)
from app.services.transits_calculator import calculate_aspect_angle, get_aspect_type

# Dados do usuário
birth_date = datetime(1981, 10, 20)
birth_time = "13:30"
latitude = -23.5505
longitude = -46.6333

# Ação: negociacao
action_id = 'negociacao'
action_config = ACTION_HOUSES[action_id]

print("="*80)
print("VALIDAÇÃO DE ASPECTOS - NEGOCIAÇÃO (4 e 13 DE DEZEMBRO)")
print("="*80)
print()
print(f"Ação: {action_id}")
print(f"Casas primárias: {action_config['primary_houses']}")
print(f"Casas secundárias: {action_config['secondary_houses']}")
print(f"Planetas benéficos: {action_config['beneficial_planets']}")
print(f"Aspectos preferidos: {action_config['preferred_aspects']}")
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

# Datas a validar
test_dates = [
    ("2025-12-04", ["00:00", "06:00", "12:00", "18:00"]),
    ("2025-12-13", ["18:00"]),
]

# Planetas a verificar
planets_to_check = ['mercury', 'venus']
planet_names = {'mercury': 'Mercúrio', 'venus': 'Vênus'}

for date_str, times in test_dates:
    print("="*80)
    print(f"VALIDANDO: {date_str}")
    print("="*80)
    print()
    
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    
    all_day_aspects = []
    max_day_score = 0
    
    for time_str in times:
        time_parts = time_str.split(":")
        check_hour = int(time_parts[0])
        check_minute = int(time_parts[1])
        check_datetime = date_obj.replace(hour=check_hour, minute=check_minute, second=0, microsecond=0)
        
        print(f"📅 {check_datetime.strftime('%d/%m/%Y %H:%M')}")
        print("-" * 80)
        
        aspects_detected = []
        score = 0
        
        for planet_key in planets_to_check:
            planet_display = planet_names[planet_key]
            
            if planet_display not in action_config['beneficial_planets']:
                print(f"  ⚠️ {planet_display} não está na lista de planetas benéficos")
                continue
            
            try:
                planet_longitude = calculate_planet_position_swiss(
                    check_datetime, latitude, longitude, planet_key
                )
                print(f"{planet_display}: {planet_longitude:.6f}°")
                
                # Verificar aspectos com casas primárias e secundárias
                for house_num in sorted(house_cusps.keys()):
                    house_cusp = house_cusps[house_num]
                    is_primary = house_num in action_config['primary_houses']
                    house_type = "PRIMÁRIA" if is_primary else "SECUNDÁRIA"
                    
                    angle = calculate_aspect_angle(planet_longitude, house_cusp)
                    aspect_type = get_aspect_type(angle, orb=8.0)
                    
                    print(f"  → Casa {house_num} ({house_type}): {house_cusp:.6f}°")
                    print(f"    Ângulo: {angle:.6f}°")
                    print(f"    Aspecto (orbe 8°): {aspect_type if aspect_type else 'Nenhum'}")
                    
                    # VALIDAÇÃO RIGOROSA
                    if aspect_type and aspect_type in action_config['preferred_aspects']:
                        aspect_targets = {
                            'conjunção': 0,
                            'sextil': 60,
                            'quadratura': 90,
                            'trígono': 120,
                            'oposição': 180
                        }
                        target_angle = aspect_targets.get(aspect_type)
                        
                        if target_angle is not None:
                            angle_diff = abs(angle - target_angle)
                            print(f"    Diferença do alvo ({target_angle}°): {angle_diff:.6f}°")
                            
                            if angle_diff <= 8.0:
                                # Calcular pontos
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
                                    aspect_str = f"{planet_display} em {aspect_type} com Casa {house_num}"
                                    aspects_detected.append(aspect_str)
                                    all_day_aspects.append(aspect_str)
                                    print(f"    ✅ ASPECTO VÁLIDO! +{points} pontos")
                                else:
                                    print(f"    ⚠️ Aspecto não dá pontos")
                            else:
                                print(f"    ❌ FORA DO ORBE! ({angle_diff:.6f}° > 8.0°)")
                        else:
                            print(f"    ⚠️ Aspecto desconhecido")
                    else:
                        if aspect_type:
                            print(f"    ⚠️ Aspecto '{aspect_type}' não está nos preferidos")
                        else:
                            print(f"    ❌ Nenhum aspecto detectado")
                    print()
                    
            except Exception as e:
                print(f"  ✗ Erro ao calcular {planet_display}: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n  Score para {time_str}: {score}")
        if score > max_day_score:
            max_day_score = score
        print()
    
    # Resumo do dia
    print(f"\n📊 RESUMO DO DIA {date_str}:")
    print(f"   Score máximo: {max_day_score}")
    unique_aspects = list(set(all_day_aspects))
    print(f"   Aspectos únicos encontrados: {len(unique_aspects)}")
    for asp in unique_aspects:
        print(f"     - {asp}")
    print()

print("="*80)
print("VALIDAÇÃO COMPLETA")
print("="*80)

