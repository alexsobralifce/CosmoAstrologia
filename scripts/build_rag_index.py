#!/usr/bin/env python3
"""
Script para processar PDFs e criar o índice RAG.
Execute este script após instalar as dependências para criar o banco de consultas.
"""

import sys
from pathlib import Path

# Adicionar o diretório backend ao path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.rag_service import RAGService

def main():
    print("=" * 60)
    print("CONSTRUINDO ÍNDICE RAG PARA DOCUMENTOS ASTROLÓGICOS")
    print("=" * 60)
    
    # Determinar caminhos
    backend_path = Path(__file__).parent.parent / "backend"
    docs_path = backend_path / "docs"
    index_path = backend_path / "rag_index.pkl"
    
    print(f"\nPasta de documentos: {docs_path}")
    print(f"Arquivo de índice: {index_path}")
    print()
    
    # Criar serviço RAG
    rag_service = RAGService(
        docs_path=str(docs_path),
        index_path=str(index_path)
    )
    
    # Verificar dependências
    try:
        from fastembed import TextEmbedding
        import PyPDF2
        import numpy as np
        print("✓ Dependências verificadas (FastEmbed, PyPDF2, NumPy)")
    except ImportError as e:
        print(f"\n✗ ERRO: Dependências não instaladas!")
        print(f"\nInstale as dependências com:")
        print("  pip install fastembed PyPDF2 numpy")
        print(f"\nErro: {e}")
        return 1
    
    # Verificar se há documentos
    pdf_files = list(docs_path.glob("*.pdf"))
    md_files = list(docs_path.glob("*.md"))
    total_files = len(pdf_files) + len(md_files)
    
    if total_files == 0:
        print(f"\n⚠ AVISO: Nenhum documento encontrado em {docs_path}")
        print("   Coloque arquivos PDF ou Markdown (.md) na pasta docs/ para processar")
        print("   O índice será criado vazio ou usando apenas a base local de conhecimento.")
        response = input("\nDeseja continuar mesmo sem documentos? (s/N): ")
        if response.lower() != 's':
            return 1
    
    # Processar PDFs
    try:
        num_chunks = rag_service.process_all_pdfs()
        
        if num_chunks > 0:
            # Salvar índice
            rag_service.save_index()
            print("\n" + "=" * 60)
            print("✓ ÍNDICE RAG CRIADO COM SUCESSO!")
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

