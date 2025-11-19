#!/usr/bin/env python3
"""
Script de teste para o sistema RAG.
Testa se o índice foi criado corretamente e se as consultas funcionam.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.rag_service import get_rag_service

def test_rag():
    print("=" * 60)
    print("TESTE DO SISTEMA RAG")
    print("=" * 60)
    
    try:
        rag = get_rag_service()
        
        # Verificar se o índice está carregado
        if not rag.embeddings or len(rag.documents) == 0:
            print("\n✗ Índice não encontrado!")
            print("Execute: python build_rag_index.py")
            return False
        
        print(f"\n✓ Índice carregado: {len(rag.documents)} documentos")
        
        # Teste 1: Busca simples
        print("\n" + "-" * 60)
        print("TESTE 1: Busca simples")
        print("-" * 60)
        results = rag.search("Sol em Libra", top_k=3)
        print(f"Query: 'Sol em Libra'")
        print(f"Resultados encontrados: {len(results)}")
        for i, r in enumerate(results, 1):
            print(f"\n  {i}. Score: {r['score']:.3f}")
            print(f"     Fonte: {r['source']}, Página {r['page']}")
            print(f"     Texto: {r['text'][:100]}...")
        
        # Teste 2: Interpretação estruturada
        print("\n" + "-" * 60)
        print("TESTE 2: Interpretação estruturada")
        print("-" * 60)
        interpretation = rag.get_interpretation(
            planet="Sol",
            sign="Libra"
        )
        print(f"Query usada: {interpretation['query_used']}")
        print(f"Fontes: {len(interpretation['sources'])}")
        print(f"\nInterpretação (primeiros 300 caracteres):")
        print(interpretation['interpretation'][:300] + "...")
        
        # Teste 3: Query customizada
        print("\n" + "-" * 60)
        print("TESTE 3: Query customizada")
        print("-" * 60)
        interpretation2 = rag.get_interpretation(
            custom_query="ascendente em aquário significado"
        )
        print(f"Query: 'ascendente em aquário significado'")
        print(f"Fontes encontradas: {len(interpretation2['sources'])}")
        for src in interpretation2['sources']:
            print(f"  - {src['source']} (página {src['page']}, relevância: {src['relevance']:.3f})")
        
        print("\n" + "=" * 60)
        print("✓ TODOS OS TESTES PASSARAM!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_rag()
    sys.exit(0 if success else 1)

