"""
Validação: Por que Mercúrio está gerando aspectos para "pedir_aumento"?
Mercúrio NÃO está na lista de planetas benéficos!
"""

from datetime import datetime
from app.services.best_timing_calculator import calculate_best_timing, ACTION_HOUSES

# Dados do usuário
birth_date = datetime(1981, 10, 20)
birth_time = "13:30"
latitude = -23.5505
longitude = -46.6333

# Verificar configuração
action_config = ACTION_HOUSES.get('pedir_aumento')
print("=" * 80)
print("VALIDAÇÃO: Planetas Benéficos para 'pedir_aumento'")
print("=" * 80)
print(f"Planetas Benéficos: {action_config['beneficial_planets']}")
print(f"Mercúrio está na lista? {'Mercúrio' in action_config['beneficial_planets']}")
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

# Verificar se há aspectos com Mercúrio
mercury_aspects = []
for moment in result.get('best_moments', []):
    for aspect in moment.get('aspects', []):
        if aspect.get('planet') == 'Mercúrio':
            mercury_aspects.append({
                'date': moment['date'],
                'aspect': aspect,
                'score': moment['score']
            })

if mercury_aspects:
    print(f"❌ ERRO: {len(mercury_aspects)} aspectos com Mercúrio encontrados!")
    print()
    print("Aspectos com Mercúrio (primeiros 10):")
    for item in mercury_aspects[:10]:
        print(f"  - {item['date']}: {item['aspect']['planet']} em {item['aspect']['aspect_type']} com Casa {item['aspect']['house']} (score: {item['score']})")
    print()
    print("Mercúrio NÃO está na lista de planetas benéficos e não deveria gerar aspectos!")
else:
    print("✅ Nenhum aspecto com Mercúrio encontrado (correto)")

print()
print("=" * 80)

