#!/usr/bin/env python3
"""
Script para reconstruir o índice RAG incluindo documentos de numerologia.
Execute este script após adicionar novos PDFs de numerologia ou astrologia.
"""

import sys
from pathlib import Path

# Adicionar o diretório backend ao path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.services.rag_service_fastembed import get_rag_service

def rebuild_index():
    """Reconstrói o índice RAG processando todos os documentos."""
    print("=" * 60)
    print("RECONSTRUINDO ÍNDICE RAG")
    print("=" * 60)
    
    try:
        # Obter serviço RAG
        rag_service = get_rag_service()
        
        print("\n[1/3] Processando documentos (PDFs e Markdowns)...")
        print("      - Pasta docs/ (astrologia)")
        print("      - Pasta numerologia/ (numerologia)")
        print("      - Pasta tarot/ (numerologia - conexão tarot-numerologia)")
        
        num_chunks = rag_service.process_all_documents()
        
        if num_chunks == 0:
            print("\n⚠️  Nenhum documento processado!")
            print("   Verifique se há PDFs nas pastas:")
            print(f"   - {backend_path / 'docs'}")
            print(f"   - {backend_path / 'numerologia'}")
            print(f"   - {backend_path / 'tarot'}")
            return False
        
        print(f"\n✅ {num_chunks} chunks processados com sucesso!")
        
        print("\n[2/3] Salvando índice em disco...")
        rag_service.save_index()
        print("✅ Índice salvo com sucesso!")
        
        print("\n[3/3] Verificando índice...")
        
        # Testar busca
        test_queries = [
            ("numerologia", "numerology"),
            ("astrologia", "astrology"),
            ("life path", "caminho de vida"),
        ]
        
        print("\n📊 Testando buscas:")
        for query_pt, query_en in test_queries:
            results_astrology = rag_service.search(query_pt, top_k=3, category='astrology')
            results_numerology = rag_service.search(query_pt, top_k=3, category='numerology')
            
            print(f"   '{query_pt}':")
            print(f"      - Astrologia: {len(results_astrology)} resultados")
            print(f"      - Numerologia: {len(results_numerology)} resultados")
        
        print("\n" + "=" * 60)
        print("✅ ÍNDICE RECONSTRUÍDO COM SUCESSO!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao reconstruir índice: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = rebuild_index()
    sys.exit(0 if success else 1)

