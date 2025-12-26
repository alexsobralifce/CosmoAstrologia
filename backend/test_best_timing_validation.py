"""
Script para validar os cálculos de best timing para uma data específica.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from app.services.best_timing_calculator import calculate_best_timing

# Dados de teste (usar dados reais do usuário se disponíveis)
birth_date = datetime(1990, 1, 1)  # Exemplo
birth_time = "12:00"
latitude = -23.5505  # São Paulo
longitude = -46.6333
action_type = "pedir_aumento"  # Ação padrão

# Data específica para validar
target_date = datetime(2025, 12, 24)

print(f"Validando cálculos para: {target_date.strftime('%d/%m/%Y')}")
print(f"Ação: {action_type}")
print(f"Data de nascimento: {birth_date.strftime('%d/%m/%Y')} às {birth_time}")
print(f"Localização: {latitude}, {longitude}")
print("\n" + "="*60 + "\n")

try:
    result = calculate_best_timing(
        birth_date=birth_date,
        birth_time=birth_time,
        latitude=latitude,
        longitude=longitude,
        action_type=action_type,
        days_ahead=1  # Apenas o dia 24/12/2025
    )
    
    if 'error' in result:
        print(f"ERRO: {result['error']}")
        sys.exit(1)
    
    best_moments = result.get('best_moments', [])
    
    # Filtrar apenas momentos do dia 24/12/2025
    target_moments = [
        m for m in best_moments 
        if m['date'].startswith('2025-12-24')
    ]
    
    if not target_moments:
        print("Nenhum momento encontrado para esta data.")
        print(f"Total de momentos encontrados: {len(best_moments)}")
        if best_moments:
            print(f"Primeiro momento: {best_moments[0]['date']}")
            print(f"Último momento: {best_moments[-1]['date']}")
        sys.exit(1)
    
    print(f"Encontrados {len(target_moments)} momentos para 24/12/2025:\n")
    
    for i, moment in enumerate(target_moments, 1):
        print(f"MOMENTO {i}:")
        print(f"  Data/Hora: {moment['date']}")
        print(f"  Score: {moment['score']}")
        print(f"  Lua Fora de Curso: {moment.get('is_moon_void', False)}")
        print(f"  Aspectos encontrados: {len(moment.get('aspects', []))}")
        
        if 'reasons' in moment:
            print(f"  Razões ({len(moment['reasons'])}):")
            for reason in moment['reasons']:
                print(f"    - {reason}")
        
        if 'aspects' in moment:
            print(f"  Detalhes dos aspectos:")
            for aspect in moment['aspects']:
                is_primary = aspect.get('is_primary', False)
                house_type = "PRIMÁRIA" if is_primary else "SECUNDÁRIA"
                print(f"    - {aspect['planet']} em {aspect['aspect_type']} com Casa {aspect['house']} ({house_type})")
        
        # Calcular score esperado
        expected_score = 0
        if 'aspects' in moment:
            for aspect in moment['aspects']:
                is_primary = aspect.get('is_primary', False)
                aspect_type = aspect['aspect_type']
                
                if is_primary:
                    if aspect_type == 'trígono':
                        expected_score += 10
                    elif aspect_type == 'sextil':
                        expected_score += 7
                    elif aspect_type == 'conjunção':
                        expected_score += 8
                else:
                    if aspect_type == 'trígono':
                        expected_score += 5
                    elif aspect_type == 'sextil':
                        expected_score += 3
                    elif aspect_type == 'conjunção':
                        expected_score += 4
        
        # Verificar penalizações
        if moment.get('is_moon_void', False):
            expected_score -= 3
            print(f"  ⚠️ Penalização Lua Fora de Curso: -3")
        
        # Verificar warnings (aspectos tensos)
        if 'reasons' in moment:
            for reason in moment['reasons']:
                if reason.startswith('⚠️'):
                    expected_score -= 5
                    print(f"  ⚠️ Penalização aspecto tenso: -5")
        
        print(f"  Score calculado: {moment['score']}")
        print(f"  Score esperado: {expected_score}")
        
        if moment['score'] != expected_score:
            print(f"  ⚠️ DISCREPÂNCIA: Score calculado ({moment['score']}) != Score esperado ({expected_score})")
        else:
            print(f"  ✓ Score correto!")
        
        print()
    
    # Encontrar score máximo do dia
    max_score = max(m['score'] for m in target_moments)
    print(f"SCORE MÁXIMO DO DIA: {max_score}")
    print(f"Momentos com score máximo: {[m['date'] for m in target_moments if m['score'] == max_score]}")
    
except Exception as e:
    print(f"ERRO ao calcular: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

