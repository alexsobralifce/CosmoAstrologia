#!/usr/bin/env python3
"""
Script de teste para verificar configuração do Resend localmente.
"""
import os
import sys
from pathlib import Path

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 80)
print("🧪 TESTE DE CONFIGURAÇÃO DO RESEND")
print("=" * 80)

# Verificar arquivo .env
env_path = Path('.env')
if not env_path.exists():
    print("❌ Arquivo .env não encontrado!")
    print("📝 Crie o arquivo backend/.env com:")
    print("   RESEND_API_KEY=re_sua-api-key-aqui")
    print("   EMAIL_FROM=noreply@cosmoastral.com.br")
    sys.exit(1)

print("✅ Arquivo .env encontrado")

# Verificar configuração
try:
    from app.core.config import settings
    
    print(f"\n📧 Configuração de Email:")
    print(f"   RESEND_API_KEY: {'✅ Configurado' if settings.RESEND_API_KEY else '❌ NÃO CONFIGURADO'}")
    if settings.RESEND_API_KEY:
        if settings.RESEND_API_KEY.startswith('re_'):
            print(f"   ✅ API Key válida (começa com re_): {settings.RESEND_API_KEY[:15]}...")
        else:
            print(f"   ⚠️  API Key pode estar incorreta: {settings.RESEND_API_KEY[:20]}...")
    print(f"   EMAIL_FROM: {settings.EMAIL_FROM}")
    
    if not settings.RESEND_API_KEY:
        print("\n❌ RESEND_API_KEY não está configurado!")
        print("\n📝 Adicione no arquivo backend/.env:")
        print("   RESEND_API_KEY=re_sua-api-key-aqui")
        print("\n🔑 Obtenha a API Key em: https://resend.com/api-keys")
        sys.exit(1)
    
    # Testar importação do Resend
    print("\n📦 Verificando biblioteca Resend...")
    try:
        import resend
        print("✅ Biblioteca resend instalada")
    except ImportError:
        print("❌ Biblioteca resend não instalada")
        print("📝 Execute: pip install resend")
        sys.exit(1)
    
    # Testar envio de email
    print("\n📧 Testando envio de email...")
    from app.services.email_service import send_verification_email
    
    # Pedir email para teste
    test_email = input("\n📮 Digite um email para teste (ou Enter para pular): ").strip()
    
    if test_email:
        print(f"\n🚀 Enviando email de teste para {test_email}...")
        result = send_verification_email(
            email=test_email,
            code="123456",
            name="Teste Local"
        )
        
        if result:
            print("\n✅ Email enviado com sucesso!")
            print("📬 Verifique a caixa de entrada (e pasta de spam)")
        else:
            print("\n❌ Falha ao enviar email")
            print("📋 Verifique os logs acima para mais detalhes")
    else:
        print("\n⏭️  Teste de envio pulado")
        print("✅ Configuração está correta - você pode testar via registro de usuário")
    
except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ Teste concluído!")
print("=" * 80)

