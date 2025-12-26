#!/usr/bin/env python3
"""
Script rápido para testar se a GROQ_API_KEY está configurada e válida.
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório backend ao path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from groq import Groq

def test_groq_key():
    print("=" * 60)
    print("TESTE DE GROQ_API_KEY")
    print("=" * 60)
    print()
    
    # Verificar se a chave está configurada
    groq_key = settings.GROQ_API_KEY
    
    if not groq_key or not groq_key.strip():
        print("❌ GROQ_API_KEY não encontrada!")
        print()
        print("Como configurar:")
        print("1. Crie ou edite o arquivo: backend/.env")
        print("2. Adicione a linha: GROQ_API_KEY=sua_chave_aqui")
        print("3. Para obter uma chave: https://console.groq.com/")
        print("4. Reinicie o servidor após adicionar a chave")
        return False
    
    print(f"✓ Chave encontrada: {groq_key[:10]}...{groq_key[-4:]}")
    print(f"  Tamanho: {len(groq_key)} caracteres")
    
    # Verificar formato
    if not groq_key.strip().startswith('gsk_'):
        print("⚠️  AVISO: A chave não começa com 'gsk_' - pode não ser válida")
    else:
        print("✓ Formato parece válido (começa com 'gsk_')")
    
    print()
    print("Testando conexão com Groq...")
    
    # Tentar criar cliente e fazer uma chamada de teste
    try:
        client = Groq(api_key=groq_key.strip())
        
        # Fazer uma chamada simples para validar
        print("  Fazendo chamada de teste...")
        models = client.models.list()
        print(f"✓ Conexão bem-sucedida!")
        print(f"  Modelos disponíveis: {len(list(models))}")
        print()
        print("✅ GROQ_API_KEY está configurada e válida!")
        return True
        
    except Exception as e:
        error_str = str(e)
        print(f"❌ Erro ao validar chave: {error_str}")
        print()
        
        if "401" in error_str or "Invalid API Key" in error_str or "invalid_api_key" in error_str:
            print("🔴 A chave está configurada mas é INVÁLIDA ou EXPIRADA")
            print()
            print("Soluções:")
            print("1. Verifique se copiou a chave completa (sem espaços extras)")
            print("2. Obtenha uma nova chave em: https://console.groq.com/")
            print("3. Atualize o arquivo backend/.env com a nova chave")
            print("4. Reinicie o servidor")
        else:
            print("⚠️  Erro desconhecido. Verifique:")
            print("1. Sua conexão com a internet")
            print("2. Se o serviço Groq está disponível")
            print("3. Os logs acima para mais detalhes")
        
        return False

if __name__ == "__main__":
    success = test_groq_key()
    sys.exit(0 if success else 1)

