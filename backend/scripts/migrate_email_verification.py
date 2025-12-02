#!/usr/bin/env python3
"""
Script de migração para adicionar colunas de verificação de email ao banco de dados.
Execute este script após fazer deploy no Railway para adicionar as novas colunas.
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório backend ao path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import engine
from sqlalchemy import text

def migrate_email_verification():
    """Adiciona colunas de verificação de email ao banco de dados."""
    
    print("🔄 Iniciando migração de verificação de email...")
    
    migrations = [
        ("Adicionando coluna email_verified", 
         "ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE"),
        
        ("Adicionando coluna verification_code", 
         "ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_code TEXT"),
        
        ("Adicionando coluna verification_code_expires", 
         "ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_code_expires TIMESTAMP"),
        
        ("Atualizando default de is_active", 
         "ALTER TABLE users ALTER COLUMN is_active SET DEFAULT FALSE"),
        
        ("Atualizando usuários existentes", 
         "UPDATE users SET email_verified = TRUE WHERE is_active = TRUE AND email_verified IS NULL"),
    ]
    
    try:
        with engine.connect() as conn:
            for description, sql in migrations:
                print(f"  ⏳ {description}...")
                conn.execute(text(sql))
                conn.commit()
                print(f"  ✅ {description} - Concluído")
            
            # Verificar se as colunas foram criadas
            print("\n🔍 Verificando colunas criadas...")
            result = conn.execute(text("""
                SELECT column_name, data_type, column_default 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name IN ('email_verified', 'verification_code', 'verification_code_expires')
                ORDER BY column_name
            """))
            
            columns = result.fetchall()
            if columns:
                print("\n✅ Colunas encontradas:")
                for col in columns:
                    print(f"   - {col[0]}: {col[1]} (default: {col[2]})")
            else:
                print("⚠️  Nenhuma coluna encontrada (pode ser SQLite)")
        
        print("\n✅ Migração concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro na migração: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = migrate_email_verification()
    sys.exit(0 if success else 1)

