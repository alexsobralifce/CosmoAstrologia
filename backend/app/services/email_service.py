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
    print("=" * 80)
    print(f"[EMAIL] 📧 INICIANDO ENVIO DE EMAIL DE VERIFICAÇÃO")
    print(f"[EMAIL] Destinatário: {email}")
    print(f"[EMAIL] Nome: {name}")
    print(f"[EMAIL] Código: {code}")
    print(f"[EMAIL] Timestamp: {datetime.now().isoformat()}")
    print("=" * 80)
    
    # Verificar se Resend está disponível
    if not RESEND_AVAILABLE:
        print(f"[EMAIL] ❌ [WARNING] Resend não disponível - Código de verificação para {email}: {code}")
        print(f"[EMAIL] ⚠️  Instale a biblioteca: pip install resend")
        return True  # Simular sucesso em desenvolvimento
    
    # Verificar se Resend está configurado
    if not settings.RESEND_API_KEY:
        print(f"[EMAIL] ❌ [WARNING] RESEND_API_KEY não configurado - Código de verificação para {email}: {code}")
        print(f"[EMAIL] ⚠️  Configure RESEND_API_KEY no .env ou variáveis de ambiente")
        return True  # Simular sucesso em desenvolvimento
    
    # Log de configuração
    print(f"[EMAIL] ✅ Resend disponível e configurado")
    print(f"[EMAIL] 📋 Configuração:")
    print(f"[EMAIL]    RESEND_API_KEY: {'✅ Configurado' if settings.RESEND_API_KEY else '❌ Não configurado'}")
    if settings.RESEND_API_KEY:
        api_key_preview = settings.RESEND_API_KEY[:10] + "..." + settings.RESEND_API_KEY[-5:] if len(settings.RESEND_API_KEY) > 15 else "***"
        print(f"[EMAIL]    API Key Preview: {api_key_preview}")
    print(f"[EMAIL]    EMAIL_FROM: {settings.EMAIL_FROM}")
    
    # Verificar se está usando domínio de teste em produção
    email_from = settings.EMAIL_FROM
    is_test_domain = email_from and '@' in email_from and email_from.split('@')[1] == 'resend.dev'
    
    if is_test_domain:
        print(f"[EMAIL] ⚠️  ATENÇÃO: Usando domínio de teste (resend.dev)")
        print(f"[EMAIL] ⚠️  O domínio de teste só permite enviar para: plribeirorocha@gmail.com")
        print(f"[EMAIL] ⚠️  Tentando enviar para: {email}")
        
        # Se não for o email da conta, avisar e retornar False
        if email.lower() != 'plribeirorocha@gmail.com':
            print("=" * 80)
            print(f"[EMAIL] ❌❌❌ NÃO É POSSÍVEL ENVIAR PARA ESTE EMAIL ❌❌❌")
            print(f"[EMAIL] 📧 Email solicitado: {email}")
            print(f"[EMAIL] ⚠️  O domínio de teste (resend.dev) só permite enviar para: plribeirorocha@gmail.com")
            print(f"[EMAIL]")
            print(f"[EMAIL] 🔧 SOLUÇÃO:")
            print(f"[EMAIL]    1. Verifique o domínio 'cosmoastral.com.br' no Resend:")
            print(f"[EMAIL]       https://resend.com/domains")
            print(f"[EMAIL]    2. Configure os registros DNS conforme instruções")
            print(f"[EMAIL]    3. Aguarde a verificação do domínio")
            print(f"[EMAIL]    4. No Railway, configure:")
            print(f"[EMAIL]       EMAIL_FROM=noreply@cosmoastral.com.br")
            print(f"[EMAIL]    5. Faça redeploy")
            print(f"[EMAIL]")
            print(f"[EMAIL] 📚 Documentação: VERIFICAR_DOMINIO_RESEND.md")
            print("=" * 80)
            return False
    
    # Verificar se está usando domínio de teste
    # O domínio de teste (resend.dev) só permite enviar para o email da conta Resend
    email_from = settings.EMAIL_FROM
    is_test_domain = email_from and '@' in email_from and email_from.split('@')[1] == 'resend.dev'
    
    if is_test_domain:
        # Domínio de teste só permite enviar para plribeirorocha@gmail.com
        allowed_test_email = 'plribeirorocha@gmail.com'
        if email.lower() != allowed_test_email.lower():
            print("=" * 80)
            print(f"[EMAIL] ❌❌❌ NÃO É POSSÍVEL ENVIAR PARA ESTE EMAIL ❌❌❌")
            print(f"[EMAIL] 📧 Email solicitado: {email}")
            print(f"[EMAIL] ⚠️  Você está usando domínio de teste (resend.dev)")
            print(f"[EMAIL] ⚠️  O domínio de teste só permite enviar para: {allowed_test_email}")
            print(f"[EMAIL]")
            print(f"[EMAIL] 🔧 SOLUÇÃO PARA ENVIAR PARA QUALQUER EMAIL:")
            print(f"[EMAIL]    1. Acesse: https://resend.com/domains")
            print(f"[EMAIL]    2. Adicione o domínio: cosmoastral.com.br")
            print(f"[EMAIL]    3. Configure os registros DNS conforme instruções")
            print(f"[EMAIL]    4. Aguarde a verificação do domínio (pode levar alguns minutos)")
            print(f"[EMAIL]    5. No Railway, configure a variável:")
            print(f"[EMAIL]       EMAIL_FROM=noreply@cosmoastral.com.br")
            print(f"[EMAIL]    6. Faça redeploy do serviço")
            print(f"[EMAIL]")
            print(f"[EMAIL] 📚 Documentação completa: VERIFICAR_DOMINIO_RESEND.md")
            print("=" * 80)
            return False
        else:
            print(f"[EMAIL] ✅ Usando domínio de teste - Email permitido: {email}")
    else:
        print(f"[EMAIL] ✅ Usando domínio verificado: {email_from}")
    
    try:
        # Configurar API key do Resend
        print(f"[EMAIL] 🔑 Configurando API key do Resend...")
        resend.api_key = settings.RESEND_API_KEY
        print(f"[EMAIL] ✅ API key configurada")
        
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
        
        # Enviar email via Resend
        params = {
            "from": settings.EMAIL_FROM,
            "to": email,
            "subject": "Verifique seu email - CosmoAstral",
            "html": html_body
        }
        
        print(f"[EMAIL] 📤 Preparando envio via Resend...")
        print(f"[EMAIL] 📋 Parâmetros do email:")
        print(f"[EMAIL]    From: {params['from']}")
        print(f"[EMAIL]    To: {params['to']}")
        print(f"[EMAIL]    Subject: {params['subject']}")
        print(f"[EMAIL]    HTML Body Length: {len(params['html'])} caracteres")
        
        print(f"[EMAIL] 🚀 Enviando email de verificação para {email} via Resend...")
        print(f"[EMAIL] ⏳ Aguardando resposta do Resend...")
        
        r = resend.Emails.send(params)
        
        print("=" * 80)
        print(f"[EMAIL] ✅✅✅ EMAIL ENVIADO COM SUCESSO! ✅✅✅")
        print(f"[EMAIL] 📧 Destinatário: {email}")
        print(f"[EMAIL] 📝 Código: {code}")
        print(f"[EMAIL] 📨 Resposta Resend: {r}")
        if isinstance(r, dict):
            if 'id' in r:
                print(f"[EMAIL] 🆔 Email ID: {r['id']}")
            print(f"[EMAIL] 📊 Resposta completa: {r}")
        print(f"[EMAIL] ⏰ Timestamp: {datetime.now().isoformat()}")
        print("=" * 80)
        return True
        
    except Exception as e:
        error_msg = str(e)
        print("=" * 80)
        print(f"[EMAIL] ❌❌❌ ERRO AO ENVIAR EMAIL ❌❌❌")
        print(f"[EMAIL] 📧 Destinatário: {email}")
        print(f"[EMAIL] 📝 Código: {code}")
        print(f"[EMAIL] 🔴 Erro: {e}")
        print(f"[EMAIL] 📋 Tipo de erro: {type(e).__name__}")
        print(f"[EMAIL] ⏰ Timestamp: {datetime.now().isoformat()}")
        print("=" * 80)
        
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
            
            # Se for erro de domínio de teste, já foi tratado antes (não deveria chegar aqui)
            # Mas se chegou, significa que houve algum problema inesperado
            if is_test_domain_error:
                print(f"[EMAIL] ❌ Erro confirmado: domínio de teste não permite enviar para {email}")
                print(f"[EMAIL] 🔧 Verifique o domínio em: https://resend.com/domains")
                return False
            
            # Se for erro de domínio não verificado, informar sobre verificação
            if is_domain_error:
                print(f"[EMAIL] ❌ Domínio não verificado: {email_from}")
                print(f"[EMAIL] 🔧 Verifique o domínio em: https://resend.com/domains")
                print(f"[EMAIL] 🔧 Configure os registros DNS e aguarde a verificação")
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
