#!/usr/bin/env python3
"""
Script de teste para verificar configuração do Brevo (SendinBlue) localmente.

Este script testa:
1. Se a biblioteca sib-api-v3-sdk está instalada
2. Se BREVO_API_KEY está configurado
3. Se consegue enviar um email de teste

Uso:
    python3 test_brevo_local.py

Certifique-se de ter configurado no .env:
    BREVO_API_KEY=xkeysib-sua-api-key-aqui
    EMAIL_FROM=noreply@cosmoastral.com.br
    EMAIL_FROM_NAME=CosmoAstral
"""
import sys
import os
from pathlib import Path

# Adicionar o diretório backend ao path para importar módulos
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

print("=" * 80)
print("🧪 TESTE DE CONFIGURAÇÃO DO BREVO (SENDINBLUE)")
print("=" * 80)

# Verificar configurações
print("\n📋 Verificando configurações...")

try:
    from app.core.config import settings
    print("✅ Módulo de configuração importado com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar configurações: {e}")
    sys.exit(1)

# Verificar BREVO_API_KEY
print(f"\n🔑 Verificando BREVO_API_KEY...")
print(f"   BREVO_API_KEY: {'✅ Configurado' if settings.BREVO_API_KEY else '❌ NÃO CONFIGURADO'}")

if settings.BREVO_API_KEY:
    if settings.BREVO_API_KEY.startswith('xkeysib-'):
        print(f"   ✅ API Key válida (começa com xkeysib-): {settings.BREVO_API_KEY[:20]}...")
    else:
        print(f"   ⚠️  API Key pode estar incorreta: {settings.BREVO_API_KEY[:20]}...")
else:
    print("\n❌ BREVO_API_KEY não está configurado!")
    print("\n📝 Para configurar:")
    print("   1. Crie ou edite o arquivo: backend/.env")
    print("   2. Adicione a linha:")
    print("   BREVO_API_KEY=xkeysib-sua-api-key-aqui")
    print("\n🔑 Obtenha a API Key em: https://app.brevo.com/settings/keys/api")
    sys.exit(1)

# Verificar EMAIL_FROM
print(f"\n📧 Verificando EMAIL_FROM...")
print(f"   EMAIL_FROM: {settings.EMAIL_FROM}")
print(f"   EMAIL_FROM_NAME: {settings.EMAIL_FROM_NAME}")

if not settings.EMAIL_FROM:
    print("\n⚠️  EMAIL_FROM não está configurado!")
    print("   Configure no .env: EMAIL_FROM=noreply@cosmoastral.com.br")

# Verificar biblioteca Brevo
print("\n📦 Verificando biblioteca Brevo...")
try:
    import sib_api_v3_sdk
    from sib_api_v3_sdk.rest import ApiException
    print("✅ Biblioteca sib-api-v3-sdk instalada")
    print(f"   Versão disponível: {sib_api_v3_sdk.__version__ if hasattr(sib_api_v3_sdk, '__version__') else 'N/A'}")
except ImportError as e:
    print("❌ Biblioteca sib-api-v3-sdk não instalada")
    print("📝 Execute: pip install sib-api-v3-sdk")
    sys.exit(1)

# Testar envio de email
print("\n" + "=" * 80)
print("🚀 TESTANDO ENVIO DE EMAIL")
print("=" * 80)

# Solicitar email de teste
test_email = input("\n📧 Digite o email para receber o teste (ou Enter para usar o padrão): ").strip()
if not test_email:
    # Usar o primeiro email verificado ou email padrão
    test_email = input("   Email padrão não configurado. Digite um email: ").strip()
    if not test_email:
        print("❌ Email de teste não fornecido. Abortando teste.")
        sys.exit(1)

test_name = input("👤 Nome do destinatário (ou Enter para 'Usuário Teste'): ").strip()
if not test_name:
    test_name = "Usuário Teste"

print(f"\n📋 Configuração do teste:")
print(f"   Destinatário: {test_name} <{test_email}>")
print(f"   Remetente: {settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>")
print(f"   API Key: {settings.BREVO_API_KEY[:20]}...")

# Confirmar envio
confirm = input("\n❓ Deseja enviar o email de teste? (s/N): ").strip().lower()
if confirm not in ['s', 'sim', 'y', 'yes']:
    print("❌ Teste cancelado pelo usuário.")
    sys.exit(0)

# Importar função de envio
try:
    from app.services.email_service import send_verification_email, generate_verification_code
    print("✅ Função de envio importada com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar função de envio: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Gerar código de teste
test_code = generate_verification_code()
print(f"\n🔢 Código de verificação gerado: {test_code}")

# Enviar email
print("\n📤 Enviando email de teste...")
print("⏳ Aguarde...\n")

try:
    success = send_verification_email(
        email=test_email,
        code=test_code,
        name=test_name
    )
    
    if success:
        print("\n" + "=" * 80)
        print("✅✅✅ TESTE CONCLUÍDO COM SUCESSO! ✅✅✅")
        print("=" * 80)
        print(f"\n📧 Email enviado para: {test_email}")
        print(f"🔢 Código de verificação: {test_code}")
        print("\n💡 Próximos passos:")
        print("   1. Verifique a caixa de entrada (e spam) do email")
        print("   2. Confirme se recebeu o código de verificação")
        print("   3. Verifique os logs do Brevo em: https://app.brevo.com/settings/logs")
    else:
        print("\n" + "=" * 80)
        print("❌❌❌ TESTE FALHOU ❌❌❌")
        print("=" * 80)
        print("\n🔍 Verifique:")
        print("   1. Se a API Key está correta")
        print("   2. Se o EMAIL_FROM está verificado no Brevo")
        print("   3. Se o destinatário é válido")
        print("   4. Os logs de erro acima para mais detalhes")
        sys.exit(1)
        
except Exception as e:
    print("\n" + "=" * 80)
    print("❌❌❌ ERRO DURANTE O TESTE ❌❌❌")
    print("=" * 80)
    print(f"\n🔴 Erro: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("✨ Teste finalizado!")
print("=" * 80)

