"""
Validação dos aspectos e score para 8 de Dezembro de 2025
Ação: pedir_aumento
Score reportado: 28
Aspectos reportados:
- Sol em sextil com Casa 2
- Vênus em sextil com Casa 2
- Sol em sextil com Casa 10
- Vênus em sextil com Casa 10
"""

from datetime import datetime
from app.services.best_timing_calculator import calculate_best_timing
from app.services.astrology_calculator import get_zodiac_sign

# Dados do usuário (20/10/1981 às 13:30)
birth_date = datetime(1981, 10, 20)
birth_time = "13:30"
latitude = -23.5505  # São Paulo
longitude = -46.6333

# Data a validar
target_date = datetime(2025, 12, 8)

print("=" * 80)
print("VALIDAÇÃO: 8 de Dezembro de 2025 - Pedir Aumento")
print("=" * 80)
print(f"Data de nascimento: {birth_date.strftime('%d/%m/%Y')} às {birth_time}")
print(f"Data a validar: {target_date.strftime('%d/%m/%Y')}")
print()

# Calcular melhores momentos para o período que inclui 8/12/2025
# Vamos calcular para 30 dias a partir de 8/12/2025 e depois filtrar
from datetime import timedelta

# Calcular melhores momentos (a função calcula a partir de hoje, então vamos calcular para um período maior)
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

# Filtrar momentos do dia 8/12/2025
dec_8_moments = [
    m for m in result.get('best_moments', [])
    if m['date'].startswith('2025-12-08')
]

print(f"Momentos encontrados para 8/12/2025: {len(dec_8_moments)}")
print()

if dec_8_moments:
    # Encontrar score máximo do dia
    max_score = max(m['score'] for m in dec_8_moments)
    print(f"Score máximo do dia: {max_score}")
    print()
    
    # Coletar todos os aspectos únicos do dia
    all_aspects = []
    for moment in dec_8_moments:
        if moment['score'] > 0:
            for aspect in moment.get('aspects', []):
                aspect_str = f"{aspect['planet']} em {aspect['aspect_type']} com Casa {aspect['house']}"
                if aspect_str not in all_aspects:
                    all_aspects.append(aspect_str)
    
    print("Aspectos encontrados no dia:")
    for aspect in all_aspects:
        print(f"  - {aspect}")
    print()
    
    # Verificar aspectos reportados
    reported_aspects = [
        "Sol em sextil com Casa 2",
        "Vênus em sextil com Casa 2",
        "Sol em sextil com Casa 10",
        "Vênus em sextil com Casa 10"
    ]
    
    print("Validação dos aspectos reportados:")
    for reported in reported_aspects:
        found = reported in all_aspects
        status = "✅ VÁLIDO" if found else "❌ NÃO ENCONTRADO"
        print(f"  {status}: {reported}")
    print()
    
    # Mostrar detalhes dos momentos com score > 0
    print("Momentos com score > 0:")
    for moment in dec_8_moments:
        if moment['score'] > 0:
            print(f"\n  Data/Hora: {moment['date']}")
            print(f"  Score: {moment['score']}")
            print(f"  Aspectos ({len(moment.get('aspects', []))}):")
            for aspect in moment.get('aspects', []):
                print(f"    - {aspect['planet']} em {aspect['aspect_type']} com Casa {aspect['house']} (primária: {aspect.get('is_primary', False)})")
            if moment.get('warnings'):
                print(f"  Avisos: {', '.join(moment['warnings'])}")
else:
    print("❌ NENHUM MOMENTO ENCONTRADO PARA 8/12/2025")
    print()
    print("Verificando se há momentos próximos...")
    all_moments = result.get('best_moments', [])
    if all_moments:
        print(f"\nPrimeiros 5 momentos encontrados:")
        for m in all_moments[:5]:
            print(f"  - {m['date']}: score {m['score']}")

print()
print("=" * 80)

