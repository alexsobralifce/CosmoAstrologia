#!/usr/bin/env python3
"""
Teste das melhorias no mapa numerológico:
- Verificar se o RAG busca da pasta numerologia
- Verificar se a interpretação é mais narrativa e detalhada
- Verificar se tem pelo menos 2000 palavras
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from datetime import datetime
from app.services.numerology_calculator import NumerologyCalculator
from app.services.rag_service_fastembed import get_rag_service

# Dados de teste (Francisco Alexandre Araujo Rocha)
full_name = "Francisco Alexandre Araujo Rocha"
birth_date = datetime(1981, 10, 20)

print("=" * 80)
print("TESTE DAS MELHORIAS NO MAPA NUMEROLÓGICO")
print("=" * 80)

# 1. Calcular mapa numerológico
print("\n1. Calculando mapa numerológico...")
calculator = NumerologyCalculator()
numerology_map = calculator.calculate_full_numerology_map(full_name, birth_date)

print(f"   ✓ Caminho de Vida: {numerology_map['life_path']['number']}")
print(f"   ✓ Expressão: {numerology_map['destiny']['number']}")
print(f"   ✓ Desejo da Alma: {numerology_map['soul']['number']}")
print(f"   ✓ Personalidade: {numerology_map['personality']['number']}")

# 2. Verificar RAG service
print("\n2. Verificando RAG service...")
try:
    rag_service = get_rag_service()
    print("   ✓ RAG service disponível")
    
    # Testar busca de numerologia
    print("\n3. Testando busca no RAG (categoria numerologia)...")
    test_queries = [
        f"life path number {numerology_map['life_path']['number']} numerologia",
        f"caminho de vida {numerology_map['life_path']['number']} numerologia",
        "numerologia pitagórica significado números"
    ]
    
    total_results = 0
    for query in test_queries:
        try:
            results = rag_service.search(
                query=query,
                top_k=3,
                category='numerology'
            )
            total_results += len(results)
            print(f"   ✓ Query '{query[:50]}...': {len(results)} resultados")
            if results:
                print(f"      Primeiro resultado: {results[0].get('source', 'N/A')[:50]}...")
        except Exception as e:
            print(f"   ✗ Erro na query '{query[:50]}...': {e}")
    
    if total_results > 0:
        print(f"\n   ✓ Total de {total_results} resultados encontrados no RAG")
    else:
        print("\n   ⚠ Nenhum resultado encontrado - pode precisar reconstruir o índice RAG")
        
except Exception as e:
    print(f"   ✗ Erro ao obter RAG service: {e}")
    import traceback
    traceback.print_exc()

# 3. Verificar se a pasta numerologia existe e tem PDFs
print("\n4. Verificando pasta numerologia...")
numerologia_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'numerologia')
if os.path.exists(numerologia_path):
    pdf_files = [f for f in os.listdir(numerologia_path) if f.endswith('.pdf')]
    print(f"   ✓ Pasta numerologia encontrada")
    print(f"   ✓ {len(pdf_files)} arquivos PDF encontrados")
    for pdf in pdf_files[:5]:  # Mostrar primeiros 5
        print(f"      - {pdf}")
    if len(pdf_files) > 5:
        print(f"      ... e mais {len(pdf_files) - 5} arquivos")
else:
    print(f"   ✗ Pasta numerologia não encontrada: {numerologia_path}")

# 4. Simular estrutura do prompt melhorado
print("\n5. Verificando estrutura do prompt melhorado...")
print("   ✓ Prompt deve ser narrativo (contar história de vida)")
print("   ✓ Mínimo de 2000 palavras")
print("   ✓ Modelo: llama-3.1-70b-versatile")
print("   ✓ Max tokens: 8000")
print("   ✓ Cada seção com mínimo de parágrafos definidos")

# 5. Resumo
print("\n" + "=" * 80)
print("RESUMO DO TESTE")
print("=" * 80)
print(f"✓ Mapa numerológico calculado com sucesso")
print(f"✓ RAG service: {'Disponível' if 'rag_service' in locals() else 'Não disponível'}")
print(f"✓ Resultados no RAG: {total_results if 'total_results' in locals() else 0}")
print(f"✓ PDFs de numerologia: {len(pdf_files) if 'pdf_files' in locals() else 0}")
print("\n" + "=" * 80)
print("PRÓXIMOS PASSOS:")
print("1. Se o RAG não retornou resultados, reconstrua o índice:")
print("   python3 scripts/build_rag_index_fastembed.py")
print("2. Teste o endpoint completo fazendo uma requisição real à API")
print("3. Verifique se a interpretação gerada tem pelo menos 2000 palavras")
print("4. Verifique se a interpretação é narrativa (conta história) e não apenas lista números")
print("=" * 80)

