"""
Serviço de email para envio de códigos de verificação.
"""
import smtplib
import secrets
import socket
import ssl
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
    
    Tenta múltiplas configurações SMTP:
    1. STARTTLS (porta 587)
    2. SSL direto (porta 465)
    
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
    
    # Tentar diferentes métodos de conexão SMTP
    methods = []
    
    # Método 1: STARTTLS (porta 587) - padrão
    if settings.SMTP_PORT == 587 or settings.SMTP_PORT == 25:
        methods.append(('starttls', settings.SMTP_PORT))
    
    # Método 2: SSL direto (porta 465)
    if settings.SMTP_PORT == 465:
        methods.append(('ssl', 465))
    else:
        # Tentar SSL como fallback se STARTTLS falhar
        methods.append(('ssl', 465))
    
    # Tentar cada método
    for method, port in methods:
        try:
            print(f"[EMAIL] Tentando enviar para {email} via {method.upper()} na porta {port}...")
            
            if method == 'ssl':
                # SSL direto (porta 465)
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(settings.SMTP_HOST, port, timeout=15, context=context) as server:
                    server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                    server.send_message(msg)
            else:
                # STARTTLS (porta 587 ou 25)
                with smtplib.SMTP(settings.SMTP_HOST, port, timeout=15) as server:
                    server.starttls(context=ssl.create_default_context())
                    server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                    server.send_message(msg)
            
            print(f"[EMAIL] ✅ Código de verificação enviado para {email} via {method.upper()}")
            return True
            
        except (socket.gaierror, socket.herror) as e:
            # Erro de DNS ou host não encontrado
            print(f"[ERROR] Erro de rede ao conectar ao SMTP {settings.SMTP_HOST}:{port} - {e}")
            if method == methods[-1][0]:  # Último método, não tentar mais
                break
            continue
            
        except (socket.timeout, TimeoutError) as e:
            print(f"[ERROR] Timeout ao conectar ao SMTP {settings.SMTP_HOST}:{port} - {e}")
            if method == methods[-1][0]:
                break
            continue
            
        except (ConnectionRefusedError, OSError) as e:
            # Erro de conexão (Network unreachable, Connection refused, etc)
            print(f"[ERROR] Erro de conexão ao SMTP {settings.SMTP_HOST}:{port} - {e}")
            if method == methods[-1][0]:
                break
            continue
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"[ERROR] Erro de autenticação SMTP: {e}")
            # Não tentar outros métodos se for erro de autenticação
            return False
            
        except smtplib.SMTPException as e:
            print(f"[ERROR] Erro SMTP ao enviar email para {email}: {e}")
            if method == methods[-1][0]:
                break
            continue
            
        except Exception as e:
            print(f"[ERROR] Erro inesperado ao enviar email para {email} via {method}: {e}")
            import traceback
            traceback.print_exc()
            if method == methods[-1][0]:
                break
            continue
    
    # Se chegou aqui, todos os métodos falharam
    print(f"[ERROR] ❌ Falha ao enviar email para {email} após tentar todos os métodos")
    print(f"[ERROR] Configuração SMTP: HOST={settings.SMTP_HOST}, PORT={settings.SMTP_PORT}")
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
