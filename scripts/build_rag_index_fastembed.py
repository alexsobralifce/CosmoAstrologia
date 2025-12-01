#!/usr/bin/env python3
"""
Script para processar documentos e criar o índice RAG usando FastEmbed e BGE.
Versão otimizada - mais leve e rápida que LlamaIndex.
"""

import sys
from pathlib import Path

# Adicionar o diretório rag-service ao path
rag_service_path = Path(__file__).parent.parent / "rag-service"
sys.path.insert(0, str(rag_service_path))

from app.services.rag_service import RAGServiceFastEmbed
from app.core.config import settings

def main():
    print("=" * 60)
    print("CONSTRUINDO ÍNDICE RAG COM FASTEMBED E BGE")
    print("=" * 60)
    
    # Determinar caminhos
    backend_path = Path(__file__).parent.parent / "backend"
    docs_path = backend_path / "docs"
    index_path = backend_path / "rag_index_fastembed"
    
    print(f"\nPasta de documentos: {docs_path}")
    print(f"Pasta de índice: {index_path}")
    print()
    
    # Verificar dependências
    try:
        from fastembed import TextEmbedding
        print("✓ Dependências FastEmbed verificadas")
    except ImportError as e:
        print(f"\n✗ ERRO: Dependências não instaladas!")
        print(f"\nInstale as dependências com:")
        print("  pip install fastembed PyPDF2 numpy")
        print(f"\nErro: {e}")
        return 1
    
    # Verificar PyPDF2
    try:
        import PyPDF2
        print("✓ PyPDF2 verificado")
    except ImportError:
        print("⚠ AVISO: PyPDF2 não instalado. PDFs não poderão ser processados.")
        print("  Instale com: pip install PyPDF2")
    
    # Criar serviço RAG
    rag_service = RAGServiceFastEmbed(
        docs_path=str(docs_path),
        index_path=str(index_path),
        bge_model_name=settings.BGE_MODEL_NAME
    )
    
    # Verificar se há documentos
    pdf_files = list(docs_path.glob("*.pdf"))
    md_files = list(docs_path.glob("*.md"))
    numerologia_path = backend_path / "numerologia"
    if numerologia_path.exists():
        pdf_files.extend(list(numerologia_path.glob("*.pdf")))
        md_files.extend(list(numerologia_path.glob("*.md")))
    
    total_files = len(pdf_files) + len(md_files)
    
    if total_files == 0:
        print(f"\n⚠ AVISO: Nenhum documento encontrado em {docs_path}")
        if numerologia_path.exists():
            print(f"  Também verificado: {numerologia_path}")
        response = input("\nDeseja continuar mesmo sem documentos? (s/N): ")
        if response.lower() != 's':
            return 1
    
    print(f"\nEncontrados {len(pdf_files)} PDFs e {len(md_files)} arquivos Markdown")
    
    # Processar documentos
    try:
        print("\n" + "=" * 60)
        print("PROCESSANDO DOCUMENTOS...")
        print("=" * 60)
        num_chunks = rag_service.process_all_documents()
        
        if num_chunks > 0:
            # Salvar índice
            print("\n" + "=" * 60)
            print("SALVANDO ÍNDICE...")
            print("=" * 60)
            rag_service.save_index()
            print("\n" + "=" * 60)
            print("✓ ÍNDICE RAG (FASTEMBED) CRIADO COM SUCESSO!")
            print("=" * 60)
            print(f"\nTotal de chunks processados: {num_chunks}")
            print(f"Índice salvo em: {index_path}")
            print(f"Modelo usado: {settings.BGE_MODEL_NAME}")
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

