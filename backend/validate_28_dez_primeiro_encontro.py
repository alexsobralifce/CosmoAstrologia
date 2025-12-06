"""
Valida os aspectos reportados para 28 de dezembro de 2025 (primeiro_encontro).
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

# Ação: primeiro_encontro
action_id = 'primeiro_encontro'
action_config = ACTION_HOUSES[action_id]

print("="*80)
print("VALIDAÇÃO DE ASPECTOS - 28 DE DEZEMBRO DE 2025 (PRIMEIRO ENCONTRO)")
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

# Data e horário a validar
check_datetime = datetime(2025, 12, 28, 18, 0, 0)

print("="*80)
print(f"VALIDANDO: {check_datetime.strftime('%d/%m/%Y %H:%M')}")
print("="*80)
print()

# Planetas a verificar
planets_to_check = ['moon', 'venus']
planet_names = {'moon': 'Lua', 'venus': 'Vênus'}

aspects_detected = []
score = 0

for planet_key in planets_to_check:
    planet_display = planet_names[planet_key]
    
    if planet_display not in action_config['beneficial_planets']:
        print(f"{planet_display} não está na lista de planetas benéficos")
        continue
    
    try:
        # Usar Swiss Ephemeris (biblioteca padrão)
        planet_longitude = calculate_planet_position_swiss(
            check_datetime, latitude, longitude, planet_key
        )
        print(f"\n{planet_display}: {planet_longitude:.6f}°")
        
        # Verificar aspectos com todas as casas (primárias e secundárias)
        for house_num in sorted(house_cusps.keys()):
            house_cusp = house_cusps[house_num]
            is_primary = house_num in action_config['primary_houses']
            house_type = "PRIMÁRIA" if is_primary else "SECUNDÁRIA"
            
            angle = calculate_aspect_angle(planet_longitude, house_cusp)
            aspect_type = get_aspect_type(angle, orb=8.0)
            
            print(f"  → Casa {house_num} ({house_type}): {house_cusp:.6f}°")
            print(f"    Ângulo calculado: {angle:.6f}°")
            print(f"    Aspecto detectado (orbe 8°): {aspect_type if aspect_type else 'Nenhum'}")
            
            # VALIDAÇÃO RIGOROSA
            if aspect_type and aspect_type in action_config['preferred_aspects']:
                # Verificar se está realmente dentro do orbe
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
                        # Calcular pontos baseado se é primária ou secundária
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
                                'planet': planet_display,
                                'house': house_num,
                                'aspect': aspect_type,
                                'angle': angle,
                                'angle_diff': angle_diff,
                                'points': points,
                                'is_primary': is_primary
                            })
                            print(f"    ✅ ASPECTO VÁLIDO! +{points} pontos ({house_type})")
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
        print()

print(f"\n📊 RESULTADO:")
print(f"   Score calculado: {score}")
print(f"   Aspectos detectados: {len(aspects_detected)}")
print(f"   Score esperado (baseado no reportado): 32")
print()

if aspects_detected:
    print(f"   Detalhes dos aspectos válidos:")
    for asp in aspects_detected:
        house_type = "PRIMÁRIA" if asp['is_primary'] else "SECUNDÁRIA"
        print(f"     ✅ {asp['planet']} em {asp['aspect']} com Casa {asp['house']} ({house_type})")
        print(f"        (diferença: {asp['angle_diff']:.6f}°, +{asp['points']} pontos)")

# Aspectos esperados baseados no reportado
expected_aspects = [
    "Lua em conjunção com Casa 5",
    "Vênus em trígono com Casa 5",
    "Lua em sextil com Casa 7",
    "Lua em trígono com Casa 1",
    "Vênus em conjunção com Casa 1",
    "Vênus em sextil com Casa 11"
]

print(f"\n   Aspectos esperados: {len(expected_aspects)}")
detected_aspects_str = [f"{asp['planet']} em {asp['aspect']} com Casa {asp['house']}" for asp in aspects_detected]
missing_aspects = [a for a in expected_aspects if a not in detected_aspects_str]
extra_aspects = [a for a in detected_aspects_str if a not in expected_aspects]

if not missing_aspects and not extra_aspects:
    print(f"   ✅ Todos os aspectos esperados foram detectados!")
else:
    if missing_aspects:
        print(f"   ❌ Aspectos faltando: {missing_aspects}")
    if extra_aspects:
        print(f"   ⚠️ Aspectos extras detectados: {extra_aspects}")

# Calcular score esperado baseado nos aspectos reportados
expected_score = 0
for asp_str in expected_aspects:
    if "Casa 5" in asp_str or "Casa 7" in asp_str:  # Primárias
        if "trígono" in asp_str:
            expected_score += 10
        elif "sextil" in asp_str:
            expected_score += 7
        elif "conjunção" in asp_str:
            expected_score += 8
    else:  # Secundárias (1, 11)
        if "trígono" in asp_str:
            expected_score += 5
        elif "sextil" in asp_str:
            expected_score += 3
        elif "conjunção" in asp_str:
            expected_score += 4

print(f"\n   Score esperado (calculado dos aspectos reportados): {expected_score}")
if score == expected_score:
    print(f"   ✅ Score CORRETO!")
elif score == 32:
    print(f"   ⚠️ Score diferente do esperado, mas igual ao reportado (32)")
else:
    print(f"   ⚠️ Score diferente: {score} (esperado: {expected_score}, reportado: 32)")

print()
print("="*80)

