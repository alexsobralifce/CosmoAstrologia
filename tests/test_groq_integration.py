#!/usr/bin/env python3
"""
Script de teste para verificar a integração do Groq com o sistema RAG.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.rag_service_wrapper import get_rag_service
from app.core.config import settings

def test_groq_integration():
    print("=" * 60)
    print("TESTE DE INTEGRAÇÃO GROQ + RAG")
    print("=" * 60)
    
    # Verificar se a chave está configurada
    if not settings.GROQ_API_KEY:
        print("\n✗ GROQ_API_KEY não encontrada no .env")
        print("Adicione GROQ_API_KEY=suachave no arquivo .env")
        return False
    
    print(f"\n✓ GROQ_API_KEY encontrada: {settings.GROQ_API_KEY[:10]}...")
    
    # Obter serviço RAG
    try:
        rag = get_rag_service()
        
        # Verificar se o índice está carregado
        if not rag.embeddings or len(rag.documents) == 0:
            print("\n✗ Índice RAG não encontrado!")
            print("Execute: python build_rag_index.py")
            return False
        
        print(f"✓ Índice RAG carregado: {len(rag.documents)} documentos")
        
        # Verificar se Groq está disponível
        if not rag.groq_client:
            print("\n✗ Cliente Groq não disponível")
            return False
        
        print("✓ Cliente Groq inicializado")
        
        # Teste 1: Interpretação com Groq
        print("\n" + "-" * 60)
        print("TESTE 1: Interpretação com Groq")
        print("-" * 60)
        
        interpretation = rag.get_interpretation(
            planet="Sol",
            sign="Libra",
            use_groq=True
        )
        
        print(f"Query: {interpretation['query_used']}")
        print(f"Gerado por: {interpretation.get('generated_by', 'unknown')}")
        print(f"Fontes: {len(interpretation['sources'])}")
        print(f"\nInterpretação (primeiros 500 caracteres):")
        print(interpretation['interpretation'][:500] + "...")
        
        # Teste 2: Comparar com e sem Groq
        print("\n" + "-" * 60)
        print("TESTE 2: Comparação RAG vs Groq")
        print("-" * 60)
        
        print("\nSem Groq (apenas RAG):")
        interpretation_rag = rag.get_interpretation(
            planet="Lua",
            sign="Câncer",
            use_groq=False
        )
        print(f"Tamanho: {len(interpretation_rag['interpretation'])} caracteres")
        print(f"Primeiros 200 chars: {interpretation_rag['interpretation'][:200]}...")
        
        print("\nCom Groq:")
        interpretation_groq = rag.get_interpretation(
            planet="Lua",
            sign="Câncer",
            use_groq=True
        )
        print(f"Tamanho: {len(interpretation_groq['interpretation'])} caracteres")
        print(f"Primeiros 200 chars: {interpretation_groq['interpretation'][:200]}...")
        
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
    success = test_groq_integration()
    sys.exit(0 if success else 1)

