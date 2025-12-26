#!/usr/bin/env python3
"""
Script para processar documentos e criar o índice RAG usando FastEmbed e BGE.
Versão otimizada - mais leve e rápida que LlamaIndex.

Este script processa todos os documentos da pasta backend/docs/ (astrologia)
e backend/numerologia/ (se existir) e cria um índice RAG para busca semântica.
"""

import sys
from pathlib import Path

# Adicionar o diretório backend ao path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.rag_service_fastembed import RAGServiceFastEmbed
from app.core.config import settings

def main():
    print("=" * 70)
    print("🔍 CONSTRUINDO ÍNDICE RAG COM FASTEMBED E BGE")
    print("=" * 70)
    
    # Determinar caminhos (backend_path já definido acima)
    docs_path = backend_path / "docs"
    numerologia_path = backend_path / "numerologia"
    index_path = backend_path / "rag_index_fastembed"
    
    print(f"\n📁 Pastas de documentos:")
    print(f"   • Astrologia: {docs_path}")
    if numerologia_path.exists():
        print(f"   • Numerologia: {numerologia_path}")
    print(f"\n💾 Pasta de índice: {index_path}")
    print()
    
    # Verificar dependências
    print("🔧 Verificando dependências...")
    try:
        from fastembed import TextEmbedding
        print("   ✓ FastEmbed instalado")
    except ImportError as e:
        print(f"\n   ✗ ERRO: FastEmbed não instalado!")
        print(f"\n   Instale as dependências com:")
        print("     cd backend")
        print("     pip install fastembed PyPDF2 numpy")
        print(f"\n   Erro: {e}")
        return 1
    
    # Verificar PyPDF2
    try:
        import PyPDF2
        print("   ✓ PyPDF2 instalado")
    except ImportError:
        print("   ⚠ AVISO: PyPDF2 não instalado. PDFs não poderão ser processados.")
        print("     Instale com: pip install PyPDF2")
    
    # Verificar documentos
    print(f"\n📚 Verificando documentos...")
    pdf_files_astrologia = list(docs_path.glob("*.pdf")) if docs_path.exists() else []
    md_files_astrologia = list(docs_path.glob("*.md")) if docs_path.exists() else []
    
    pdf_files_numerologia = []
    md_files_numerologia = []
    if numerologia_path.exists():
        pdf_files_numerologia = list(numerologia_path.glob("*.pdf"))
        md_files_numerologia = list(numerologia_path.glob("*.md"))
    
    total_pdfs = len(pdf_files_astrologia) + len(pdf_files_numerologia)
    total_mds = len(md_files_astrologia) + len(md_files_numerologia)
    total_files = total_pdfs + total_mds
    
    print(f"   • Astrologia: {len(pdf_files_astrologia)} PDFs, {len(md_files_astrologia)} Markdowns")
    if numerologia_path.exists():
        print(f"   • Numerologia: {len(pdf_files_numerologia)} PDFs, {len(md_files_numerologia)} Markdowns")
    print(f"   • Total: {total_pdfs} PDFs, {total_mds} Markdowns = {total_files} arquivos")
    
    if total_files == 0:
        print(f"\n⚠ AVISO: Nenhum documento encontrado!")
        print(f"   Verifique se há arquivos em:")
        print(f"   • {docs_path}")
        if numerologia_path.exists():
            print(f"   • {numerologia_path}")
        response = input("\n   Deseja continuar mesmo sem documentos? (s/N): ")
        if response.lower() != 's':
            return 1
    
    # Criar serviço RAG
    print(f"\n🤖 Inicializando serviço RAG...")
    print(f"   Modelo: {settings.BGE_MODEL_NAME}")
    rag_service = RAGServiceFastEmbed(
        docs_path=str(docs_path),
        index_path=str(index_path),
        bge_model_name=settings.BGE_MODEL_NAME
    )
    
    # Processar documentos
    try:
        print("\n" + "=" * 70)
        print("🔄 PROCESSANDO DOCUMENTOS...")
        print("=" * 70)
        print("   Isso pode levar alguns minutos dependendo do número de documentos...")
        print()
        
        num_chunks = rag_service.process_all_documents()
        
        if num_chunks > 0:
            # Salvar índice
            print("\n" + "=" * 70)
            print("💾 SALVANDO ÍNDICE...")
            print("=" * 70)
            rag_service.save_index()
            
            print("\n" + "=" * 70)
            print("✅ ÍNDICE RAG (FASTEMBED) CRIADO COM SUCESSO!")
            print("=" * 70)
            print(f"\n📊 Estatísticas:")
            print(f"   • Total de chunks processados: {num_chunks}")
            print(f"   • Índice salvo em: {index_path}")
            print(f"   • Modelo usado: {settings.BGE_MODEL_NAME}")
            print(f"\n✨ O índice está pronto para uso na API!")
            print(f"   As interpretações de planetas nas casas agora usarão este índice.")
            return 0
        else:
            print("\n❌ Nenhum documento processado")
            print("   Verifique se os arquivos estão acessíveis e não estão corrompidos.")
            return 1
            
    except Exception as e:
        print(f"\n❌ ERRO ao processar documentos: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())

