"""
Script para validar os aspectos astrológicos reportados para 24/12/2025.
Valida se o Sol está realmente em conjunção com Casa 1 e trígono com Casa 9.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
import ephem
from app.services.best_timing_calculator import (
    calculate_best_timing,
    calculate_house_cusp,
    ACTION_HOUSES
)
from app.services.astrology_calculator import calculate_planet_position
from app.services.transits_calculator import calculate_aspect_angle, get_aspect_type

# Dados do usuário
birth_date = datetime(1981, 10, 20)
birth_time = "13:30"
latitude = -23.5505  # São Paulo (padrão, ajustar se necessário)
longitude = -46.6333

# Data a validar
target_date = datetime(2025, 12, 24)
target_times = ["06:00", "12:00", "18:00"]

print("="*70)
print("VALIDAÇÃO DE ASPECTOS ASTROLÓGICOS - 24/12/2025")
print("="*70)
print()
print(f"Data de nascimento: {birth_date.strftime('%d/%m/%Y')} às {birth_time}")
print(f"Data a validar: {target_date.strftime('%d/%m/%Y')}")
print(f"Horários: {', '.join(target_times)}")
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

# Calcular cúspides das casas para ações que incluem Casa 1 e Casa 9
actions_to_check = ['apresentacao_publica', 'mudanca_carreira']

for action_id in actions_to_check:
    print(f"\n{'='*70}")
    print(f"AÇÃO: {action_id.upper()}")
    print(f"{'='*70}")
    
    action_config = ACTION_HOUSES[action_id]
    print(f"Casas primárias: {action_config['primary_houses']}")
    print(f"Casas secundárias: {action_config['secondary_houses']}")
    print()
    
    # Calcular cúspides das casas
    house_cusps = {}
    for house_num in action_config['primary_houses'] + action_config['secondary_houses']:
        try:
            cusp = calculate_house_cusp(
                birth_observer,
                house_num,
                birth_date,
                birth_time,
                latitude,
                longitude
            )
            house_cusps[house_num] = cusp
            print(f"Casa {house_num} (cúspide): {cusp:.2f}°")
        except Exception as e:
            print(f"Erro ao calcular Casa {house_num}: {e}")
    
    print()
    print(f"{'-'*70}")
    print("VERIFICAÇÃO DOS ASPECTOS PARA CADA HORÁRIO:")
    print(f"{'-'*70}")
    
    for time_str in target_times:
        time_parts = time_str.split(":")
        check_hour = int(time_parts[0])
        check_minute = int(time_parts[1])
        
        check_datetime = target_date.replace(hour=check_hour, minute=check_minute, second=0, microsecond=0)
        
        print(f"\n📅 {check_datetime.strftime('%d/%m/%Y %H:%M')}")
        print("-" * 50)
        
        # Criar observador para data/hora atual
        transit_observer = ephem.Observer()
        transit_observer.lat = str(latitude)
        transit_observer.lon = str(longitude)
        transit_observer.date = check_datetime.strftime('%Y/%m/%d %H:%M:%S')
        
        # Calcular posição do Sol
        try:
            sun_longitude = calculate_planet_position(transit_observer, 'sun')
            print(f"Sol: {sun_longitude:.2f}°")
            
            # Verificar aspectos com Casa 1
            if 1 in house_cusps:
                house_1_cusp = house_cusps[1]
                angle_1 = calculate_aspect_angle(sun_longitude, house_1_cusp)
                aspect_type_1 = get_aspect_type(angle_1, orb=8.0)
                
                is_primary = 1 in action_config['primary_houses']
                house_type = "PRIMÁRIA" if is_primary else "SECUNDÁRIA"
                
                print(f"  → Casa 1 ({house_type}): {house_1_cusp:.2f}°")
                print(f"    Ângulo: {angle_1:.2f}°")
                print(f"    Aspecto: {aspect_type_1 if aspect_type_1 else 'Nenhum (fora do orbe)'}")
                
                if aspect_type_1 == 'conjunção':
                    if is_primary:
                        print(f"    ✓ CONJUNÇÃO CONFIRMADA! (+8 pontos)")
                    else:
                        print(f"    ✓ CONJUNÇÃO CONFIRMADA! (+4 pontos)")
                elif aspect_type_1:
                    print(f"    ⚠️ Aspecto diferente: {aspect_type_1} (esperado: conjunção)")
            
            # Verificar aspectos com Casa 9
            if 9 in house_cusps:
                house_9_cusp = house_cusps[9]
                angle_9 = calculate_aspect_angle(sun_longitude, house_9_cusp)
                aspect_type_9 = get_aspect_type(angle_9, orb=8.0)
                
                is_primary = 9 in action_config['primary_houses']
                house_type = "PRIMÁRIA" if is_primary else "SECUNDÁRIA"
                
                print(f"  → Casa 9 ({house_type}): {house_9_cusp:.2f}°")
                print(f"    Ângulo: {angle_9:.2f}°")
                print(f"    Aspecto: {aspect_type_9 if aspect_type_9 else 'Nenhum (fora do orbe)'}")
                
                if aspect_type_9 == 'trígono':
                    if is_primary:
                        print(f"    ✓ TRÍGONO CONFIRMADO! (+10 pontos)")
                    else:
                        print(f"    ✓ TRÍGONO CONFIRMADO! (+5 pontos)")
                elif aspect_type_9:
                    print(f"    ⚠️ Aspecto diferente: {aspect_type_9} (esperado: trígono)")
            
            # Calcular score esperado
            score = 0
            if 1 in house_cusps:
                angle_1 = calculate_aspect_angle(sun_longitude, house_cusps[1])
                aspect_type_1 = get_aspect_type(angle_1, orb=8.0)
                if aspect_type_1 == 'conjunção':
                    if 1 in action_config['primary_houses']:
                        score += 8
                    else:
                        score += 4
            
            if 9 in house_cusps:
                angle_9 = calculate_aspect_angle(sun_longitude, house_cusps[9])
                aspect_type_9 = get_aspect_type(angle_9, orb=8.0)
                if aspect_type_9 == 'trígono':
                    if 9 in action_config['primary_houses']:
                        score += 10
                    else:
                        score += 5
            
            print(f"\n  📊 Score calculado para este momento: {score}")
            
        except Exception as e:
            print(f"  ❌ Erro ao calcular: {e}")
            import traceback
            traceback.print_exc()

print()
print("="*70)
print("VALIDAÇÃO COMPLETA")
print("="*70)
print()
print("Verifique se os aspectos reportados correspondem aos calculados acima.")
print("Se houver discrepâncias, pode ser necessário verificar:")
print("  1. A localização exata usada no cálculo")
print("  2. O sistema de casas utilizado")
print("  3. O orbe utilizado (atualmente 8.0°)")

