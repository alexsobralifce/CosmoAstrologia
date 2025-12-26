#!/usr/bin/env python3
"""
Script para verificar sintaxe Python antes do deploy.
Verifica todos os arquivos Python no diretório app/ para erros de sintaxe.
"""
import ast
import sys
from pathlib import Path

def check_file_syntax(file_path: Path) -> tuple[bool, str]:
    """Verifica a sintaxe de um arquivo Python."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        ast.parse(source, filename=str(file_path))
        return True, ""
    except SyntaxError as e:
        error_msg = f"{file_path}:{e.lineno}:{e.offset}: {e.msg}\n  {e.text}"
        return False, error_msg
    except Exception as e:
        return False, f"{file_path}: Erro inesperado: {e}"

def main():
    """Verifica a sintaxe de todos os arquivos Python no diretório app/."""
    backend_dir = Path(__file__).parent.parent
    app_dir = backend_dir / "app"
    
    if not app_dir.exists():
        print(f"❌ Diretório app/ não encontrado em {backend_dir}")
        sys.exit(1)
    
    python_files = list(app_dir.rglob("*.py"))
    
    if not python_files:
        print("❌ Nenhum arquivo Python encontrado em app/")
        sys.exit(1)
    
    errors = []
    for py_file in python_files:
        # Ignorar arquivos em __pycache__
        if '__pycache__' in str(py_file):
            continue
            
        is_valid, error = check_file_syntax(py_file)
        if not is_valid:
            errors.append(error)
    
    if errors:
        print("❌ Erros de sintaxe encontrados:\n")
        for error in errors:
            print(error)
        print(f"\n❌ Total de erros: {len(errors)}")
        sys.exit(1)
    else:
        print(f"✓ Todos os {len(python_files)} arquivos Python têm sintaxe válida!")
        sys.exit(0)

if __name__ == "__main__":
    main()

