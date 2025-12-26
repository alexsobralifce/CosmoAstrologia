"""
Debug: Por que Casa 3 está aparecendo nos resultados?
"""

from datetime import datetime
from app.services.best_timing_calculator import calculate_best_timing, ACTION_HOUSES
from app.services.astrology_calculator import calculate_ascendant, calculate_midheaven
import ephem

# Dados do usuário
birth_date = datetime(1981, 10, 20)
birth_time = "13:30"
latitude = -23.5505
longitude = -46.6333

# Verificar configuração
action_config = ACTION_HOUSES.get('pedir_aumento')
print("=" * 80)
print("DEBUG: Por que Casa 3 está aparecendo?")
print("=" * 80)
print(f"Casas Primárias: {action_config['primary_houses']}")
print(f"Casas Secundárias: {action_config['secondary_houses']}")
print()

# Criar observador natal
birth_observer = ephem.Observer()
birth_observer.lat = str(latitude)
birth_observer.lon = str(longitude)
time_parts = birth_time.split(":")
hour = int(time_parts[0]) if len(time_parts) > 0 else 0
minute = int(time_parts[1]) if len(time_parts) > 1 else 0
birth_datetime = birth_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
birth_observer.date = birth_datetime.strftime('%Y/%m/%d %H:%M:%S')

# Calcular casas usando a função do best_timing_calculator
from app.services.best_timing_calculator import calculate_house_cusp

print("Cúspides das casas calculadas:")
for house_num in action_config['primary_houses'] + action_config['secondary_houses']:
    cusp = calculate_house_cusp(
        birth_observer,
        house_num,
        birth_date,
        birth_time,
        latitude,
        longitude
    )
    print(f"  Casa {house_num}: {cusp:.2f}°")
print()

# Verificar se há algum problema no cálculo Equal House
ascendant = calculate_ascendant(birth_observer)
mc = calculate_midheaven(birth_observer)

print(f"Ascendente (Casa 1): {ascendant:.2f}°")
print(f"MC (Casa 10): {mc:.2f}°")
print()

# Calcular Casa 3 usando Equal House (se for o caso)
casa_3_equal = (ascendant + 60) % 360  # Casa 1 + 60° = Casa 3
print(f"Casa 3 (Equal House): {casa_3_equal:.2f}°")
print()

# Verificar resultados para 2026-01-04
print("Verificando resultados para 2026-01-04:")
result = calculate_best_timing(
    birth_date=birth_date,
    birth_time=birth_time,
    latitude=latitude,
    longitude=longitude,
    action_type='pedir_aumento',
    days_ahead=60
)

jan_4_moments = [
    m for m in result.get('best_moments', [])
    if m['date'].startswith('2026-01-04')
]

if jan_4_moments:
    print(f"Momentos encontrados: {len(jan_4_moments)}")
    for moment in jan_4_moments:
        print(f"\n  Data: {moment['date']}")
        print(f"  Score: {moment['score']}")
        print(f"  Aspectos ({len(moment.get('aspects', []))}):")
        for aspect in moment.get('aspects', []):
            print(f"    - {aspect['planet']} em {aspect['aspect_type']} com Casa {aspect['house']} (primária: {aspect.get('is_primary', False)})")
            # Verificar se a casa está na lista permitida
            if aspect['house'] not in action_config['primary_houses'] and aspect['house'] not in action_config['secondary_houses']:
                print(f"      ❌ ERRO: Casa {aspect['house']} NÃO está na lista permitida!")
else:
    print("Nenhum momento encontrado para 2026-01-04")

print()
print("=" * 80)

