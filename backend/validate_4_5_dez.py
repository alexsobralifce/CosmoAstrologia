"""
Valida os aspectos reportados para 4 e 5 de dezembro de 2025.
Verifica se Sol e Vênus estão realmente em sextil com Casas 2 e 10.
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

# Ação: pedir_aumento
action_id = 'pedir_aumento'
action_config = ACTION_HOUSES[action_id]

print("="*80)
print("VALIDAÇÃO DE ASPECTOS - 4 e 5 DE DEZEMBRO DE 2025")
print("="*80)
print()
print(f"Ação: {action_id}")
print(f"Casas primárias: {action_config['primary_houses']}")
print(f"Planetas benéficos: {action_config['beneficial_planets']}")
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
for house_num in action_config['primary_houses']:
    cusp = calculate_house_cusp(
        birth_observer,
        house_num,
        birth_date,
        birth_time,
        latitude,
        longitude
    )
    house_cusps[house_num] = cusp
    print(f"  Casa {house_num} (PRIMÁRIA): {cusp:.6f}°")
print()

# Datas e horários a validar
test_dates = [
    ("2025-12-04", ["00:00", "06:00", "12:00", "18:00"]),
    ("2025-12-05", ["00:00", "06:00", "12:00", "18:00"]),
]

# Planetas a verificar
planets_to_check = ['sun', 'venus']
planet_names = {'sun': 'Sol', 'venus': 'Vênus'}

for date_str, times in test_dates:
    print("="*80)
    print(f"VALIDANDO: {date_str}")
    print("="*80)
    print()
    
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    
    # Coletar todos os aspectos válidos do dia
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
                continue
            
            try:
                planet_longitude = calculate_planet_position_swiss(
                    check_datetime, latitude, longitude, planet_key
                )
                
                for house_num in action_config['primary_houses']:
                    house_cusp = house_cusps[house_num]
                    angle = calculate_aspect_angle(planet_longitude, house_cusp)
                    aspect_type = get_aspect_type(angle, orb=8.0)
                    
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
                            
                            if angle_diff <= 8.0:
                                if aspect_type == 'trígono':
                                    points = 10
                                elif aspect_type == 'sextil':
                                    points = 7
                                elif aspect_type == 'conjunção':
                                    points = 8
                                else:
                                    points = 0
                                
                                if points > 0:
                                    score += points
                                    aspect_str = f"{planet_display} em {aspect_type} com Casa {house_num}"
                                    aspects_detected.append(aspect_str)
                                    all_day_aspects.append(aspect_str)
                                    
                                    print(f"  ✅ {aspect_str} (+{points} pontos, diferença: {angle_diff:.6f}°)")
                            else:
                                print(f"  ❌ {planet_display} vs Casa {house_num}: {angle:.2f}° (fora do orbe, diferença: {angle_diff:.6f}°)")
                        else:
                            print(f"  ⚠️ Aspecto desconhecido: {aspect_type}")
                    else:
                        if aspect_type:
                            print(f"  ⚠️ {planet_display} vs Casa {house_num}: {aspect_type} (não está nos preferidos)")
                        else:
                            # Mostrar apenas se estiver próximo de um aspecto válido
                            aspect_targets = {'sextil': 60, 'trígono': 120, 'conjunção': 0}
                            for target_name, target_angle in aspect_targets.items():
                                diff = abs(angle - target_angle)
                                if diff <= 12:  # Mostrar se estiver próximo (mas fora do orbe)
                                    print(f"  ❌ {planet_display} vs Casa {house_num}: {angle:.2f}° (quase {target_name}, mas {diff:.2f}° > 8.0°)")
                                    break
                                
            except Exception as e:
                print(f"  ✗ Erro ao calcular {planet_display}: {e}")
        
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
    
    # Comparar com aspectos reportados
    expected_aspects = [
        "Sol em sextil com Casa 2",
        "Vênus em sextil com Casa 2",
        "Sol em sextil com Casa 10",
        "Vênus em sextil com Casa 10"
    ]
    
    print(f"\n   Aspectos esperados (reportados): {len(expected_aspects)}")
    missing = [a for a in expected_aspects if a not in unique_aspects]
    extra = [a for a in unique_aspects if a not in expected_aspects]
    
    if not missing and not extra:
        print(f"   ✅ Todos os aspectos esperados foram encontrados!")
    else:
        if missing:
            print(f"   ❌ Aspectos faltando: {missing}")
        if extra:
            print(f"   ⚠️ Aspectos extras: {extra}")
    
    expected_score = 28  # 4 aspectos × 7 pontos cada
    if max_day_score == expected_score:
        print(f"   ✅ Score CORRETO! ({max_day_score})")
    else:
        print(f"   ⚠️ Score diferente: {max_day_score} (esperado: {expected_score})")
    
    print()
    print()

print("="*80)
print("VALIDAÇÃO COMPLETA")
print("="*80)

