#!/usr/bin/env python3
"""
Script para verificar e carregar o índice RAG.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("🔍 VERIFICAÇÃO DO ÍNDICE RAG")
print("=" * 80)

# Verificar FastEmbed
try:
    import fastembed
    print("✅ FastEmbed está instalado")
except ImportError:
    print("❌ FastEmbed NÃO está instalado")
    print("   Execute: pip install fastembed")
    sys.exit(1)

# Verificar se o índice existe
index_path = Path(__file__).parent / "rag_index_fastembed"
if index_path.exists():
    print(f"✅ Pasta do índice existe: {index_path}")
    
    documents_file = index_path / "documents.json"
    embeddings_file = index_path / "embeddings.npy"
    metadata_file = index_path / "metadata.json"
    
    if documents_file.exists():
        print(f"✅ documents.json existe ({documents_file.stat().st_size / 1024 / 1024:.2f} MB)")
    else:
        print("❌ documents.json NÃO existe")
    
    if embeddings_file.exists():
        print(f"✅ embeddings.npy existe ({embeddings_file.stat().st_size / 1024 / 1024:.2f} MB)")
    else:
        print("❌ embeddings.npy NÃO existe")
    
    if metadata_file.exists():
        print(f"✅ metadata.json existe ({metadata_file.stat().st_size} bytes)")
    else:
        print("❌ metadata.json NÃO existe")
else:
    print(f"❌ Pasta do índice NÃO existe: {index_path}")
    sys.exit(1)

# Tentar carregar o índice
print("\n" + "=" * 80)
print("📦 TENTANDO CARREGAR O ÍNDICE...")
print("=" * 80)

try:
    from app.services.rag_service_fastembed import get_rag_service
    
    rag_service = get_rag_service()
    print("✅ RAG Service criado")
    
    if rag_service:
        print("⏳ Carregando índice...")
        loaded = rag_service.load_index()
        
        if loaded:
            print("✅ Índice carregado com sucesso!")
            
            if hasattr(rag_service, 'documents') and rag_service.documents:
                print(f"✅ Total de documentos: {len(rag_service.documents)}")
                
                # Testar uma busca
                print("\n" + "=" * 80)
                print("🧪 TESTANDO BUSCA...")
                print("=" * 80)
                try:
                    results = rag_service.search("Netuno em Peixes", top_k=3)
                    print(f"✅ Busca funcionou! {len(results)} resultados encontrados")
                    if results:
                        print(f"\nPrimeiro resultado:")
                        print(f"  Score: {results[0].get('score', 0):.3f}")
                        print(f"  Fonte: {results[0].get('source', 'N/A')}")
                        print(f"  Texto: {results[0].get('text', '')[:100]}...")
                except Exception as e:
                    print(f"❌ Erro ao testar busca: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("⚠️ Índice carregado mas sem documentos")
        else:
            print("❌ Falha ao carregar índice")
            print("   Verifique os logs acima para mais detalhes")
    else:
        print("❌ RAG Service não pôde ser criado")
        
except Exception as e:
    print(f"❌ Erro ao carregar índice: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ VERIFICAÇÃO CONCLUÍDA")
print("=" * 80)

