"""
Serviço de email para envio de códigos de verificação.
"""
import smtplib
import secrets
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from app.core.config import settings


def generate_verification_code() -> str:
    """Gera um código de verificação de 6 dígitos."""
    return str(secrets.randbelow(900000) + 100000)


def send_verification_email(email: str, code: str, name: str) -> bool:
    """
    Envia email de verificação com código de 6 dígitos.
    Esta função é executada em background e não bloqueia a resposta da API.
    
    Args:
        email: Email do destinatário
        code: Código de verificação
        name: Nome do usuário
        
    Returns:
        bool: True se enviado com sucesso, False caso contrário
    """
    # Verificar se SMTP está configurado
    if not all([settings.SMTP_HOST, settings.SMTP_PORT, settings.SMTP_USERNAME, settings.SMTP_PASSWORD]):
        print(f"[WARNING] SMTP não configurado - Código de verificação para {email}: {code}")
        return True  # Simular sucesso em desenvolvimento
    
    try:
        # Configurar mensagem
        msg = MIMEMultipart()
        msg['From'] = settings.EMAIL_FROM
        msg['To'] = email
        msg['Subject'] = "Verifique seu email - CosmoAstral"
        
        # Corpo do email em texto simples
        body = f"""
        Olá {name},
        
        Seu código de verificação é: {code}
        
        Este código expira em 1 minuto.
        
        Se você não solicitou este código, ignore este email.
        
        Atenciosamente,
        Equipe CosmoAstral
        """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Enviar email com timeout
        socket.setdefaulttimeout(10)  # 10 segundos de timeout para conexão SMTP
        
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
        
        print(f"[EMAIL] ✅ Código de verificação enviado para {email}")
        return True
        
    except smtplib.SMTPException as e:
        print(f"[ERROR] Erro SMTP ao enviar email para {email}: {e}")
        import traceback
        traceback.print_exc()
        return False
    except socket.timeout:
        print(f"[ERROR] Timeout ao conectar ao servidor SMTP para {email}")
        return False
    except Exception as e:
        print(f"[ERROR] Erro inesperado ao enviar email para {email}: {e}")
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
