"""
Testa se há problema de timezone que está causando cálculo em data/hora diferente.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
import ephem
from app.services.best_timing_calculator import calculate_best_timing

# Dados do usuário
birth_date = datetime(1981, 10, 20)
birth_time = "13:30"
latitude = -23.5505
longitude = -46.6333

print("="*80)
print("TESTE DE TIMEZONE E DATA")
print("="*80)
print()

# Verificar qual é a data "hoje" que o sistema está usando
from datetime import datetime
today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
print(f"Data 'hoje' do sistema: {today.strftime('%d/%m/%Y %H:%M:%S')}")
print(f"Data atual real: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
print()

# Testar cálculo para 30 dias à frente
print("Testando cálculo para 30 dias à frente...")
print()

try:
    result = calculate_best_timing(
        action_type='mudanca_carreira',
        birth_date=birth_date,
        birth_time=birth_time,
        latitude=latitude,
        longitude=longitude,
        days_ahead=30
    )
    
    if 'error' in result:
        print(f"Erro: {result['error']}")
    else:
        best_moments = result.get('best_moments', [])
        print(f"Total de momentos encontrados: {len(best_moments)}")
        print()
        
        # Verificar se há momentos em dezembro de 2025
        dec_2025_moments = [
            m for m in best_moments
            if '2025-12' in m['date']
        ]
        
        print(f"Momentos em dezembro de 2025: {len(dec_2025_moments)}")
        
        if dec_2025_moments:
            print("\nPrimeiros 5 momentos de dezembro de 2025:")
            for i, moment in enumerate(dec_2025_moments[:5]):
                print(f"  {i+1}. {moment['date']} - Score: {moment['score']}")
                if 'reasons' in moment:
                    for reason in moment['reasons'][:3]:
                        print(f"      - {reason}")
        
        # Verificar especificamente 24/12/2025
        target_moments = [
            m for m in best_moments
            if m['date'].startswith('2025-12-24')
        ]
        
        print()
        print(f"Momentos em 24/12/2025: {len(target_moments)}")
        
        if target_moments:
            print("\nDetalhes dos momentos em 24/12/2025:")
            for moment in target_moments:
                print(f"\n  Data/Hora: {moment['date']}")
                print(f"  Score: {moment['score']}")
                print(f"  Lua Fora de Curso: {moment.get('is_moon_void', False)}")
                
                if 'aspects' in moment:
                    print(f"  Aspectos ({len(moment['aspects'])}):")
                    for aspect in moment['aspects']:
                        print(f"    - {aspect.get('planet')} em {aspect.get('aspect_type')} com Casa {aspect.get('house')}")
                
                if 'reasons' in moment:
                    print(f"  Razões ({len(moment['reasons'])}):")
                    for reason in moment['reasons']:
                        print(f"    - {reason}")
        else:
            print("  Nenhum momento encontrado para 24/12/2025")
            print("  Isso está CORRETO, pois os aspectos não estão dentro do orbe de 8°")
        
        # Verificar todos os momentos para ver padrões
        print()
        print("Análise de todos os momentos:")
        print(f"  Score mínimo: {min(m['score'] for m in best_moments) if best_moments else 'N/A'}")
        print(f"  Score máximo: {max(m['score'] for m in best_moments) if best_moments else 'N/A'}")
        
        # Contar quantos momentos têm cada score
        score_counts = {}
        for m in best_moments:
            score = m['score']
            score_counts[score] = score_counts.get(score, 0) + 1
        
        print("  Distribuição de scores:")
        for score in sorted(score_counts.keys(), reverse=True)[:10]:
            print(f"    Score {score}: {score_counts[score]} momentos")
        
except Exception as e:
    print(f"Erro: {e}")
    import traceback
    traceback.print_exc()

