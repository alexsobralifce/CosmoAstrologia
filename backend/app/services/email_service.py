"""
Serviço de email para envio de códigos de verificação usando Resend.
"""
import secrets
from datetime import datetime
from app.core.config import settings

try:
    import resend
    RESEND_AVAILABLE = True
except ImportError:
    RESEND_AVAILABLE = False
    print("[WARNING] Biblioteca 'resend' não instalada. Execute: pip install resend")


def generate_verification_code() -> str:
    """Gera um código de verificação de 6 dígitos."""
    return str(secrets.randbelow(900000) + 100000)


def send_verification_email(email: str, code: str, name: str) -> bool:
    """
    Envia email de verificação com código de 6 dígitos usando Resend.
    Esta função é executada em background e não bloqueia a resposta da API.
    
    Args:
        email: Email do destinatário
        code: Código de verificação
        name: Nome do usuário
        
    Returns:
        bool: True se enviado com sucesso, False caso contrário
    """
    # Verificar se Resend está disponível
    if not RESEND_AVAILABLE:
        print(f"[WARNING] Resend não disponível - Código de verificação para {email}: {code}")
        print(f"[WARNING] ⚠️  Instale a biblioteca: pip install resend")
        return True  # Simular sucesso em desenvolvimento
    
    # Verificar se Resend está configurado
    if not settings.RESEND_API_KEY:
        print(f"[WARNING] RESEND_API_KEY não configurado - Código de verificação para {email}: {code}")
        print(f"[WARNING] ⚠️  Configure RESEND_API_KEY no .env ou variáveis de ambiente")
        return True  # Simular sucesso em desenvolvimento
    
    # Verificar se o domínio está verificado (para evitar erros)
    # Se usar domínio não verificado, tentar usar domínio de teste
    email_from = settings.EMAIL_FROM
    if email_from and '@' in email_from:
        domain = email_from.split('@')[1]
        # Se não for domínio de teste do Resend, verificar se pode usar
        if domain not in ['resend.dev']:
            # Tentar usar domínio de teste se o domínio customizado falhar
            # Isso será tratado no try/except abaixo
            pass
    
    try:
        # Configurar API key do Resend
        resend.api_key = settings.RESEND_API_KEY
        
        # Corpo do email em HTML
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
        
        # Enviar email via Resend
        params = {
            "from": settings.EMAIL_FROM,
            "to": email,
            "subject": "Verifique seu email - CosmoAstral",
            "html": html_body
        }
        
        print(f"[EMAIL] Enviando email de verificação para {email} via Resend...")
        r = resend.Emails.send(params)
        
        print(f"[EMAIL] ✅ Código de verificação enviado para {email} via Resend")
        print(f"[EMAIL] Resposta Resend: {r}")
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] ❌ Erro ao enviar email para {email} via Resend: {e}")
        
        # Verificar se é erro de domínio não verificado
        is_domain_error = (
            "domain is not verified" in error_msg.lower() or 
            "domain not verified" in error_msg.lower()
        )
        
        # Verificar se é erro de domínio de teste (só pode enviar para email da conta)
        is_test_domain_error = (
            "testing emails to your own email address" in error_msg.lower() or
            "only send testing emails" in error_msg.lower()
        )
        
        # Se for erro de domínio não verificado OU erro de domínio de teste
        if is_domain_error or is_test_domain_error:
            print(f"[WARNING] ⚠️  Problema com domínio de email:")
            if is_test_domain_error:
                print(f"[WARNING]    O domínio de teste (resend.dev) só permite enviar para o email da conta.")
                print(f"[WARNING]    Tentando enviar para: {email}")
                print(f"[WARNING]    Para enviar para qualquer email, verifique seu domínio em: https://resend.com/domains")
            else:
                print(f"[WARNING]    Domínio não verificado. Verifique em: https://resend.com/domains")
            
            # Se estiver usando domínio de teste e tentando enviar para outro email
            if is_test_domain_error and email_from and '@' in email_from:
                domain = email_from.split('@')[1]
                if domain == 'resend.dev':
                    print(f"[ERROR] ❌ Não é possível enviar para {email} usando domínio de teste.")
                    print(f"[ERROR]    Configure EMAIL_FROM=noreply@cosmoastral.com.br no Railway")
                    print(f"[ERROR]    E verifique o domínio cosmoastral.com.br no Resend")
                    return False
            
            # Tentar com domínio de teste apenas se não for erro de teste domain
            if not is_test_domain_error:
                print(f"[WARNING] Tentando com domínio de teste do Resend...")
                try:
                    params_test = {
                        "from": "cosmoastral@resend.dev",  # Domínio de teste do Resend
                        "to": email,
                        "subject": "Verifique seu email - CosmoAstral",
                        "html": html_body
                    }
                    resend.api_key = settings.RESEND_API_KEY
                    r = resend.Emails.send(params_test)
                    print(f"[EMAIL] ✅ Email enviado usando domínio de teste (cosmoastral@resend.dev)")
                    print(f"[EMAIL] ⚠️  Para produção, verifique o domínio em https://resend.com/domains")
                    return True
                except Exception as e2:
                    print(f"[ERROR] ❌ Erro mesmo com domínio de teste: {e2}")
                    import traceback
                    traceback.print_exc()
                    return False
        
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
