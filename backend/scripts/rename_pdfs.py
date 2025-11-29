#!/usr/bin/env python3
"""
Script para renomear PDFs adicionando prefixos apropriados:
- PDFs em backend/docs/ recebem prefixo 'ast_'
- PDFs em backend/numerologia/ recebem prefixo 'num_'
"""

from pathlib import Path
import sys

def rename_pdfs():
    """Renomeia PDFs adicionando prefixos apropriados."""
    
    # Definir caminhos
    backend_path = Path(__file__).parent.parent
    docs_path = backend_path / "docs"
    numerologia_path = backend_path / "numerologia"
    
    renamed_count = 0
    
    # Renomear PDFs em docs (adicionar ast_)
    if docs_path.exists():
        pdf_files = list(docs_path.glob("*.pdf"))
        print(f"\n[Renomeação] Processando {len(pdf_files)} PDFs em {docs_path}...")
        
        for pdf_file in pdf_files:
            if not pdf_file.name.startswith(('ast_', 'num_')):
                new_name = f"ast_{pdf_file.name}"
                new_path = pdf_file.parent / new_name
                
                # Verificar se já existe arquivo com esse nome
                if new_path.exists() and new_path != pdf_file:
                    print(f"  ⚠️  Arquivo já existe: {new_name} (pulando {pdf_file.name})")
                    continue
                
                pdf_file.rename(new_path)
                print(f"  ✅ Renomeado: {pdf_file.name} → {new_name}")
                renamed_count += 1
            else:
                print(f"  ℹ️  Já tem prefixo: {pdf_file.name}")
    else:
        print(f"  ⚠️  Pasta não encontrada: {docs_path}")
    
    # Renomear PDFs em numerologia (adicionar num_)
    if numerologia_path.exists():
        pdf_files = list(numerologia_path.glob("*.pdf"))
        print(f"\n[Renomeação] Processando {len(pdf_files)} PDFs em {numerologia_path}...")
        
        for pdf_file in pdf_files:
            if not pdf_file.name.startswith(('ast_', 'num_')):
                new_name = f"num_{pdf_file.name}"
                new_path = pdf_file.parent / new_name
                
                # Verificar se já existe arquivo com esse nome
                if new_path.exists() and new_path != pdf_file:
                    print(f"  ⚠️  Arquivo já existe: {new_name} (pulando {pdf_file.name})")
                    continue
                
                pdf_file.rename(new_path)
                print(f"  ✅ Renomeado: {pdf_file.name} → {new_name}")
                renamed_count += 1
            else:
                print(f"  ℹ️  Já tem prefixo: {pdf_file.name}")
    else:
        print(f"  ⚠️  Pasta não encontrada: {numerologia_path}")
        print(f"  💡 Criando pasta {numerologia_path}...")
        numerologia_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Pasta criada!")
    
    print(f"\n✅ Renomeação concluída! {renamed_count} arquivo(s) renomeado(s).")
    return renamed_count

if __name__ == "__main__":
    try:
        rename_pdfs()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro durante renomeação: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

