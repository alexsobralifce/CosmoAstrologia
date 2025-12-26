#!/usr/bin/env python3
"""
Script de teste para verificar a conexão com a API do DeepSeek.

Uso:
    python test_deepseek_connection.py

Este script verifica:
1. Se a chave API está configurada
2. Se a chave tem formato válido
3. Se a conexão com a API funciona
4. Se consegue gerar uma resposta de teste
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório backend ao path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def test_deepseek_connection():
    """Testa a conexão com DeepSeek."""
    print("=" * 60)
    print("🔍 Testando conexão com DeepSeek API")
    print("=" * 60)
    print()
    
    # 1. Verificar se a chave está configurada
    print("1️⃣ Verificando configuração da chave API...")
    
    # Tentar importar settings
    try:
        from app.core.config import settings
        deepseek_key = getattr(settings, "DEEPSEEK_API_KEY", None) or os.getenv("DEEPSEEK_API_KEY")
    except Exception as e:
        print(f"   ❌ Erro ao carregar configurações: {e}")
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not deepseek_key or not deepseek_key.strip():
        print("   ❌ DEEPSEEK_API_KEY não configurada!")
        print()
        print("   📝 Para configurar:")
        print("      - Adicione DEEPSEEK_API_KEY=sk-... no arquivo backend/.env")
        print("      - Ou defina a variável de ambiente DEEPSEEK_API_KEY")
        print()
        print("   🔗 Obtenha sua chave em: https://platform.deepseek.com/api_keys")
        return False
    
    deepseek_key = deepseek_key.strip()
    print(f"   ✅ Chave API encontrada (tamanho: {len(deepseek_key)} caracteres)")
    
    # 2. Verificar formato da chave
    print()
    print("2️⃣ Verificando formato da chave...")
    # DeepSeek keys geralmente começam com 'sk-' mas não vamos ser muito restritivos
    if deepseek_key.startswith('sk-'):
        print("   ✅ Formato parece válido (começa com 'sk-')")
    else:
        print(f"   ⚠️  Formato não é o esperado (geralmente começa com 'sk-')")
        print(f"      Mas vamos tentar mesmo assim...")
    
    # 3. Testar inicialização do provider
    print()
    print("3️⃣ Testando inicialização do provedor DeepSeek...")
    try:
        from app.services.ai_provider_service import DeepSeekProvider
        
        provider = DeepSeekProvider()
        
        if not provider.is_available():
            print("   ❌ Provedor DeepSeek não está disponível")
            print("      Verifique se a chave está configurada corretamente")
            return False
        
        print("   ✅ Provedor inicializado com sucesso")
    except Exception as e:
        print(f"   ❌ Erro ao inicializar provedor: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 4. Testar conexão com a API (fazendo uma chamada simples)
    print()
    print("4️⃣ Testando conexão com a API (chamada de teste)...")
    try:
        # Tentar fazer uma chamada simples
        test_response = provider.generate_text(
            system_prompt="Você é um assistente útil.",
            user_prompt="Responda apenas com 'OK' para confirmar que está funcionando.",
            temperature=0.7,
            max_tokens=10,
            model="deepseek-chat"
        )
        
        if test_response:
            print(f"   ✅ Conexão bem-sucedida!")
            print(f"   📝 Resposta de teste: {test_response.strip()[:50]}")
        else:
            print("   ⚠️  Conexão funcionou mas não retornou resposta")
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ Erro ao testar conexão: {error_msg}")
        
        # Diagnosticar tipo de erro
        if "401" in error_msg or "Unauthorized" in error_msg or "invalid" in error_msg.lower():
            print()
            print("   🔑 Problema com autenticação:")
            print("      - A chave API pode estar inválida ou expirada")
            print("      - Verifique se copiou a chave completa")
            print("      - Obtenha uma nova chave em: https://platform.deepseek.com/api_keys")
        elif "timeout" in error_msg.lower() or "connection" in error_msg.lower():
            print()
            print("   🌐 Problema de conexão:")
            print("      - Verifique sua conexão com a internet")
            print("      - A API do DeepSeek pode estar temporariamente indisponível")
        else:
            print()
            print("   ❓ Erro desconhecido:")
            print(f"      - Detalhes: {error_msg}")
            import traceback
            traceback.print_exc()
        
        return False
    
    # 5. Teste completo de geração de texto
    print()
    print("5️⃣ Testando geração completa de texto...")
    try:
        test_prompt = "Em uma frase, explique o que é astrologia."
        
        full_response = provider.generate_text(
            system_prompt="Você é um assistente astrológico experiente.",
            user_prompt=test_prompt,
            temperature=0.7,
            max_tokens=100,
            model="deepseek-chat"
        )
        
        if full_response and len(full_response.strip()) > 10:
            print(f"   ✅ Geração de texto funcionando!")
            print(f"   📝 Resposta: {full_response.strip()[:150]}...")
        else:
            print("   ⚠️  Resposta muito curta ou vazia")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro ao gerar texto completo: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 6. Verificar uso do get_ai_provider (padrão)
    print()
    print("6️⃣ Verificando get_ai_provider (provedor padrão)...")
    try:
        from app.services.ai_provider_service import get_ai_provider
        
        default_provider = get_ai_provider()
        
        if default_provider:
            provider_name = default_provider.get_provider_name() if hasattr(default_provider, 'get_provider_name') else 'unknown'
            print(f"   ✅ Provedor padrão obtido: {provider_name}")
            
            if provider_name == "deepseek":
                print("   ✅ DeepSeek está configurado como provedor padrão!")
            else:
                print(f"   ⚠️  Provedor padrão é {provider_name}, não DeepSeek")
                print("      (Isso é normal se DeepSeek não estiver disponível)")
        else:
            print("   ⚠️  Não foi possível obter provedor padrão")
            
    except Exception as e:
        print(f"   ⚠️  Erro ao obter provedor padrão: {e}")
        # Não é crítico, apenas informativo
    
    # Sucesso!
    print()
    print("=" * 60)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 60)
    print()
    print("🎉 A comunicação com DeepSeek está funcionando corretamente!")
    print()
    return True


if __name__ == "__main__":
    try:
        success = test_deepseek_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print()
        print("\n⚠️  Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

