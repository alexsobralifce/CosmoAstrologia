"""
Validação: Verificar se aspectos de casas incorretas estão sendo retornados
Para "pedir_aumento", apenas casas [2, 10] (primárias) e [6, 11] (secundárias) devem aparecer
"""

from datetime import datetime
from app.services.best_timing_calculator import calculate_best_timing, ACTION_HOUSES

# Dados do usuário
birth_date = datetime(1981, 10, 20)
birth_time = "13:30"
latitude = -23.5505
longitude = -46.6333

# Verificar configuração da ação
action_config = ACTION_HOUSES.get('pedir_aumento')
print("=" * 80)
print("VALIDAÇÃO: Casas Permitidas para 'pedir_aumento'")
print("=" * 80)
print(f"Casas Primárias: {action_config['primary_houses']}")
print(f"Casas Secundárias: {action_config['secondary_houses']}")
print(f"Planetas Benéficos: {action_config['beneficial_planets']}")
print()

# Calcular melhores momentos
result = calculate_best_timing(
    birth_date=birth_date,
    birth_time=birth_time,
    latitude=latitude,
    longitude=longitude,
    action_type='pedir_aumento',
    days_ahead=30
)

print(f"Total de momentos encontrados: {len(result.get('best_moments', []))}")
print()

# Verificar TODOS os aspectos retornados e identificar casas incorretas
all_houses_found = set()
invalid_aspects = []

for moment in result.get('best_moments', []):
    for aspect in moment.get('aspects', []):
        house_num = aspect.get('house')
        all_houses_found.add(house_num)
        
        # Verificar se a casa está na lista permitida
        if house_num not in action_config['primary_houses'] and house_num not in action_config['secondary_houses']:
            invalid_aspects.append({
                'date': moment['date'],
                'aspect': aspect,
                'house': house_num,
                'planet': aspect.get('planet'),
                'aspect_type': aspect.get('aspect_type')
            })

print(f"Casas encontradas nos aspectos: {sorted(all_houses_found)}")
print()

if invalid_aspects:
    print(f"❌ ERRO: {len(invalid_aspects)} aspectos com casas INVÁLIDAS encontrados!")
    print()
    print("Aspectos inválidos:")
    for invalid in invalid_aspects[:10]:  # Mostrar primeiros 10
        print(f"  - {invalid['date']}: {invalid['planet']} em {invalid['aspect_type']} com Casa {invalid['house']}")
    print()
    print(f"Casas permitidas: {action_config['primary_houses']} (primárias) e {action_config['secondary_houses']} (secundárias)")
else:
    print("✅ Todos os aspectos estão usando apenas casas permitidas!")

print()
print("=" * 80)

