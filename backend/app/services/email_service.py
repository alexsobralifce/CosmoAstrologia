"""
Serviço de email para envio de códigos de verificação usando Brevo (SendinBlue).
"""
import secrets
from datetime import datetime
from app.core.config import settings

try:
    import sib_api_v3_sdk
    from sib_api_v3_sdk.rest import ApiException
    BREVO_AVAILABLE = True
except ImportError:
    BREVO_AVAILABLE = False
    print("[WARNING] Biblioteca 'sib_api_v3_sdk' não instalada. Execute: pip install sib-api-v3-sdk")


def generate_verification_code() -> str:
    """Gera um código de verificação de 6 dígitos."""
    return str(secrets.randbelow(900000) + 100000)


def send_verification_email(email: str, code: str, name: str) -> bool:
    """
    Envia email de verificação com código de 6 dígitos usando Brevo (SendinBlue).
    Esta função é executada em background e não bloqueia a resposta da API.
    
    Args:
        email: Email do destinatário
        code: Código de verificação
        name: Nome do usuário
        
    Returns:
        bool: True se enviado com sucesso, False caso contrário
    """
    print("=" * 80)
    print(f"[EMAIL] 📧 INICIANDO ENVIO DE EMAIL DE VERIFICAÇÃO")
    print(f"[EMAIL] Destinatário: {email}")
    print(f"[EMAIL] Nome: {name}")
    print(f"[EMAIL] Código: {code}")
    print(f"[EMAIL] Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)
    
    # Verificar se Brevo está disponível
    if not BREVO_AVAILABLE:
        print(f"[EMAIL] ❌ [WARNING] Brevo não disponível - Código de verificação para {email}: {code}")
        print(f"[EMAIL] ⚠️  Instale a biblioteca: pip install sib-api-v3-sdk")
        return True  # Simular sucesso em desenvolvimento
    
    # Verificar se Brevo está configurado
    if not settings.BREVO_API_KEY:
        print(f"[EMAIL] ❌ [WARNING] BREVO_API_KEY não configurado - Código de verificação para {email}: {code}")
        print(f"[EMAIL] ⚠️  Configure BREVO_API_KEY no .env ou variáveis de ambiente")
        return True  # Simular sucesso em desenvolvimento
    
    # Log de configuração
    print(f"[EMAIL] ✅ Brevo disponível e configurado")
    print(f"[EMAIL] 📋 Configuração:")
    print(f"[EMAIL]    BREVO_API_KEY: {'✅ Configurado' if settings.BREVO_API_KEY else '❌ Não configurado'}")
    if settings.BREVO_API_KEY:
        api_key_preview = settings.BREVO_API_KEY[:10] + "..." + settings.BREVO_API_KEY[-5:] if len(settings.BREVO_API_KEY) > 15 else "***"
        print(f"[EMAIL]    API Key Preview: {api_key_preview}")
    print(f"[EMAIL]    EMAIL_FROM: {settings.EMAIL_FROM}")
    print(f"[EMAIL]    EMAIL_FROM_NAME: {settings.EMAIL_FROM_NAME}")
    
    try:
        # Configurar API key do Brevo
        print(f"[EMAIL] 🔑 Configurando API key do Brevo...")
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = settings.BREVO_API_KEY
        print(f"[EMAIL] ✅ API key configurada")
        
        # Instanciar a API de emails transacionais
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        
        # Corpo do email em HTML
        print(f"[EMAIL] 📝 Gerando corpo do email em HTML...")
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .code {{ font-size: 32px; font-weight: bold; color: #4F46E5; text-align: center; 
                         padding: 20px; background-color: #F3F4F6; border-radius: 8px; 
                         letter-spacing: 5px; margin: 20px 0; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #E5E7EB; 
                          color: #6B7280; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Verifique seu email - CosmoAstral</h1>
                <p>Olá {name},</p>
                <p>Seu código de verificação é:</p>
                <div class="code">{code}</div>
                <p>Este código expira em <strong>1 minuto</strong>.</p>
                <p>Se você não solicitou este código, ignore este email.</p>
                <div class="footer">
                    <p>Atenciosamente,<br>Equipe CosmoAstral</p>
                </div>
            </div>
        </body>
        </html>
        """
        print(f"[EMAIL] ✅ Corpo do email gerado ({len(html_body)} caracteres)")
        
        # Preparar dados do email
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": email, "name": name}],
            sender={"name": settings.EMAIL_FROM_NAME, "email": settings.EMAIL_FROM},
            subject="Verifique seu email - CosmoAstral",
            html_content=html_body
        )
        
        print(f"[EMAIL] 📤 Preparando envio via Brevo...")
        print(f"[EMAIL] 📋 Parâmetros do email:")
        print(f"[EMAIL]    From: {settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>")
        print(f"[EMAIL]    To: {name} <{email}>")
        print(f"[EMAIL]    Subject: Verifique seu email - CosmoAstral")
        print(f"[EMAIL]    HTML Body Length: {len(html_body)} caracteres")
        
        print(f"[EMAIL] 🚀 Enviando email de verificação para {email} via Brevo...")
        print(f"[EMAIL] ⏳ Aguardando resposta do Brevo...")
        
        api_response = api_instance.send_transac_email(send_smtp_email)
        
        print("=" * 80)
        print(f"[EMAIL] ✅✅✅ EMAIL ENVIADO COM SUCESSO! ✅✅✅")
        print(f"[EMAIL] 📧 Destinatário: {email}")
        print(f"[EMAIL] 📝 Código: {code}")
        print(f"[EMAIL] 📨 Resposta Brevo: {api_response}")
        if hasattr(api_response, 'message_id'):
            print(f"[EMAIL] 🆔 Message ID: {api_response.message_id}")
        print(f"[EMAIL] ⏰ Timestamp: {datetime.now().isoformat()}")
        print("=" * 80)
        return True
        
    except ApiException as e:
        error_msg = str(e)
        print("=" * 80)
        print(f"[EMAIL] ❌❌❌ ERRO AO ENVIAR EMAIL ❌❌❌")
        print(f"[EMAIL] 📧 Destinatário: {email}")
        print(f"[EMAIL] 📝 Código: {code}")
        print(f"[EMAIL] 🔴 Erro: {e}")
        print(f"[EMAIL] 📋 Status Code: {e.status}")
        print(f"[EMAIL] 📋 Resposta: {e.body}")
        print(f"[EMAIL] ⏰ Timestamp: {datetime.now().isoformat()}")
        print("=" * 80)
        
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        error_msg = str(e)
        print("=" * 80)
        print(f"[EMAIL] ❌❌❌ ERRO INESPERADO AO ENVIAR EMAIL ❌❌❌")
        print(f"[EMAIL] 📧 Destinatário: {email}")
        print(f"[EMAIL] 📝 Código: {code}")
        print(f"[EMAIL] 🔴 Erro: {e}")
        print(f"[EMAIL] 📋 Tipo de erro: {type(e).__name__}")
        print(f"[EMAIL] ⏰ Timestamp: {datetime.now().isoformat()}")
        print("=" * 80)
        
        import traceback
        traceback.print_exc()
        return False


def is_verification_code_valid(user_code: str, stored_code: str, expires_at: datetime) -> bool:
    """
    Verifica se o código de verificação é válido.
    
    Args:
        user_code: Código digitado pelo usuário
        stored_code: Código armazenado no banco
        expires_at: Data de expiração do código
        
    Returns:
        bool: True se válido, False caso contrário
    """
    if not all([user_code, stored_code, expires_at]):
        return False
    
    if expires_at < datetime.now():
        return False
    
    return user_code == stored_code
