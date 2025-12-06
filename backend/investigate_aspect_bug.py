"""
Investigação profunda do bug de detecção de aspectos incorretos.
Testa com dados reais do usuário e rastreia cada passo do cálculo.
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

# Dados reais do usuário
birth_date = datetime(1981, 10, 20)
birth_time = "13:30"
latitude = -23.5505  # Ajustar se necessário
longitude = -46.6333

# Data problemática
target_date = datetime(2025, 12, 24)
target_time = "12:00"

print("="*80)
print("INVESTIGAÇÃO PROFUNDA - BUG DE DETECÇÃO DE ASPECTOS")
print("="*80)
print()
print(f"Data de nascimento: {birth_date.strftime('%d/%m/%Y')} às {birth_time}")
print(f"Localização: {latitude}, {longitude}")
print(f"Data a investigar: {target_date.strftime('%d/%m/%Y')} às {target_time}")
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

# Criar observador para data/hora de trânsito
transit_observer = ephem.Observer()
transit_observer.lat = str(latitude)
transit_observer.lon = str(longitude)
time_parts = target_time.split(":")
check_hour = int(time_parts[0])
check_minute = int(time_parts[1])
check_datetime = target_date.replace(hour=check_hour, minute=check_minute, second=0, microsecond=0)
transit_observer.date = check_datetime.strftime('%Y/%m/%d %H:%M:%S')

print("="*80)
print("PASSO 1: CÁLCULO DE POSIÇÕES PLANETÁRIAS")
print("="*80)
print()

# Calcular posição do Sol
try:
    sun_longitude = calculate_planet_position(transit_observer, 'sun')
    print(f"✓ Sol em trânsito: {sun_longitude:.6f}°")
except Exception as e:
    print(f"✗ Erro ao calcular Sol: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Testar todas as ações que incluem Casa 1 e Casa 9
actions_to_test = ['apresentacao_publica', 'mudanca_carreira', 'iniciar_projeto']

for action_id in actions_to_test:
    print("="*80)
    print(f"TESTANDO AÇÃO: {action_id.upper()}")
    print("="*80)
    print()
    
    action_config = ACTION_HOUSES[action_id]
    print(f"Configuração da ação:")
    print(f"  Casas primárias: {action_config['primary_houses']}")
    print(f"  Casas secundárias: {action_config['secondary_houses']}")
    print(f"  Planetas benéficos: {action_config['beneficial_planets']}")
    print(f"  Aspectos preferidos: {action_config['preferred_aspects']}")
    print()
    
    # Calcular cúspides das casas
    print("PASSO 2: CÁLCULO DE CÚSPIDES DAS CASAS")
    print("-" * 80)
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
            is_primary = house_num in action_config['primary_houses']
            house_type = "PRIMÁRIA" if is_primary else "SECUNDÁRIA"
            print(f"  Casa {house_num} ({house_type}): {cusp:.6f}°")
        except Exception as e:
            print(f"  ✗ Erro ao calcular Casa {house_num}: {e}")
            import traceback
            traceback.print_exc()
    
    print()
    
    # Verificar aspectos do Sol com cada casa
    print("PASSO 3: VERIFICAÇÃO DE ASPECTOS DO SOL")
    print("-" * 80)
    
    if 'Sol' in action_config['beneficial_planets']:
        print(f"Sol está na lista de planetas benéficos: ✓")
        print()
        
        for house_num in sorted(house_cusps.keys()):
            house_cusp = house_cusps[house_num]
            is_primary = house_num in action_config['primary_houses']
            house_type = "PRIMÁRIA" if is_primary else "SECUNDÁRIA"
            
            print(f"Verificando Sol vs Casa {house_num} ({house_type}):")
            print(f"  Sol: {sun_longitude:.6f}°")
            print(f"  Casa {house_num}: {house_cusp:.6f}°")
            
            # Calcular ângulo
            angle = calculate_aspect_angle(sun_longitude, house_cusp)
            print(f"  Ângulo calculado: {angle:.6f}°")
            
            # Verificar diferença absoluta
            diff_abs = abs(sun_longitude - house_cusp)
            diff_circular = min(diff_abs, 360 - diff_abs)
            print(f"  Diferença absoluta: {diff_abs:.6f}°")
            print(f"  Diferença circular: {diff_circular:.6f}°")
            
            # Testar com diferentes orbes
            for orb in [5.0, 8.0, 10.0, 12.0, 15.0]:
                aspect_type = get_aspect_type(angle, orb=orb)
                if aspect_type:
                    print(f"  Orbe {orb:4.1f}°: {aspect_type:12s} ✓")
                else:
                    print(f"  Orbe {orb:4.1f}°: {'Nenhum':12s}")
            
            # Verificar se está nos aspectos preferidos
            aspect_type_8 = get_aspect_type(angle, orb=8.0)
            if aspect_type_8 and aspect_type_8 in action_config['preferred_aspects']:
                print(f"  ✓ Aspecto '{aspect_type_8}' está nos preferidos")
                
                # Calcular score esperado
                if is_primary:
                    if aspect_type_8 == 'trígono':
                        score = 10
                    elif aspect_type_8 == 'sextil':
                        score = 7
                    elif aspect_type_8 == 'conjunção':
                        score = 8
                    else:
                        score = 0
                else:
                    if aspect_type_8 == 'trígono':
                        score = 5
                    elif aspect_type_8 == 'sextil':
                        score = 3
                    elif aspect_type_8 == 'conjunção':
                        score = 4
                    else:
                        score = 0
                
                print(f"  Score esperado: +{score} pontos")
            else:
                if aspect_type_8:
                    print(f"  ⚠️ Aspecto '{aspect_type_8}' NÃO está nos preferidos")
                else:
                    print(f"  ✗ Nenhum aspecto detectado com orbe 8°")
            
            print()
    
    print()
    
    # Executar o cálculo completo do best_timing
    print("PASSO 4: EXECUTAR CÁLCULO COMPLETO")
    print("-" * 80)
    try:
        result = calculate_best_timing(
            action_type=action_id,
            birth_date=birth_date,
            birth_time=birth_time,
            latitude=latitude,
            longitude=longitude,
            days_ahead=1
        )
        
        if 'error' in result:
            print(f"✗ Erro: {result['error']}")
        else:
            # Procurar momentos do dia 24/12/2025
            target_moments = [
                m for m in result.get('best_moments', [])
                if m['date'].startswith('2025-12-24')
            ]
            
            print(f"Total de momentos encontrados: {len(result.get('best_moments', []))}")
            print(f"Momentos em 24/12/2025: {len(target_moments)}")
            print()
            
            for moment in target_moments:
                print(f"MOMENTO: {moment['date']}")
                print(f"  Score: {moment['score']}")
                print(f"  Aspectos: {len(moment.get('aspects', []))}")
                print(f"  Razões: {len(moment.get('reasons', []))}")
                
                if 'aspects' in moment:
                    for aspect in moment['aspects']:
                        print(f"    - {aspect.get('planet')} em {aspect.get('aspect_type')} com Casa {aspect.get('house')} ({'PRIMÁRIA' if aspect.get('is_primary') else 'SECUNDÁRIA'})")
                
                if 'reasons' in moment:
                    print(f"  Razões reportadas:")
                    for reason in moment['reasons']:
                        print(f"    - {reason}")
                
                print()
    except Exception as e:
        print(f"✗ Erro ao executar cálculo completo: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print()

print("="*80)
print("INVESTIGAÇÃO COMPLETA")
print("="*80)

