#!/usr/bin/env python3
"""
Script para processar documentos e criar o índice RAG usando LlamaIndex e BGE.
Nova implementação que substituirá a estrutura antiga após validação.
"""

import sys
from pathlib import Path

# Adicionar o diretório backend ao path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.rag_service_llamaindex import RAGServiceLlamaIndex

def main():
    print("=" * 60)
    print("CONSTRUINDO ÍNDICE RAG COM LLAMAINDEX E BGE")
    print("=" * 60)
    
    # Determinar caminhos
    backend_path = Path(__file__).parent.parent / "backend"
    docs_path = backend_path / "docs"
    index_path = backend_path / "rag_index_llamaindex"
    
    print(f"\nPasta de documentos: {docs_path}")
    print(f"Pasta de índice: {index_path}")
    print()
    
    # Verificar dependências
    try:
        from llama_index.core import VectorStoreIndex
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        print("✓ Dependências LlamaIndex verificadas")
    except ImportError as e:
        print(f"\n✗ ERRO: Dependências não instaladas!")
        print(f"\nInstale as dependências com:")
        print("  pip install llama-index llama-index-embeddings-huggingface")
        print(f"\nErro: {e}")
        return 1
    
    # Criar serviço RAG
    rag_service = RAGServiceLlamaIndex(
        docs_path=str(docs_path),
        index_path=str(index_path)
    )
    
    # Verificar se há documentos
    pdf_files = list(docs_path.glob("*.pdf"))
    md_files = list(docs_path.glob("*.md"))
    total_files = len(pdf_files) + len(md_files)
    
    if total_files == 0:
        print(f"\n⚠ AVISO: Nenhum documento encontrado em {docs_path}")
        response = input("\nDeseja continuar mesmo sem documentos? (s/N): ")
        if response.lower() != 's':
            return 1
    
    # Processar documentos
    try:
        num_chunks = rag_service.process_all_documents()
        
        if num_chunks > 0:
            # Salvar índice
            rag_service.save_index()
            print("\n" + "=" * 60)
            print("✓ ÍNDICE RAG (LLAMAINDEX) CRIADO COM SUCESSO!")
            print("=" * 60)
            print(f"\nTotal de chunks processados: {num_chunks}")
            print(f"Índice salvo em: {index_path}")
            print("\nO índice está pronto para uso na API.")
            return 0
        else:
            print("\n✗ Nenhum documento processado")
            return 1
            
    except Exception as e:
        print(f"\n✗ ERRO ao processar documentos: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())

