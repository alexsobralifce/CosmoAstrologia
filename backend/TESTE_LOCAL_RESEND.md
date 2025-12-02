# 🧪 Teste Local do Resend

## 📋 Configuração Rápida

### 1. **Instalar a biblioteca Resend**

```bash
cd backend
pip install resend
# ou
pip install -r requirements.txt
```

### 2. **Configurar o arquivo `.env`**

Crie ou edite o arquivo `backend/.env`:

```env
# Database (local)
DATABASE_URL=sqlite:///./astrologia.db

# Security
SECRET_KEY=sua-chave-secreta-local
GROQ_API_KEY=sua-chave-groq

# Email (Resend) - OBRIGATÓRIO para testar envio de email
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
EMAIL_FROM=noreply@cosmoastral.com.br
# OU para testes rápidos:
# EMAIL_FROM=cosmoastral@resend.dev

# CORS (para desenvolvimento local)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 3. **Como obter a API Key do Resend**

1. Acesse: https://resend.com/
2. Faça login ou crie uma conta (grátis)
3. Vá para **API Keys** no dashboard
4. Clique em **Create API Key**
5. Dê um nome (ex: "Local Development")
6. Copie a chave (começa com `re_`)
7. Cole no arquivo `.env`

---

## 🚀 Como Testar

### Opção 1: Teste via Registro de Usuário

1. **Inicie o servidor:**
   ```bash
   cd backend
   python3 main.py
   # ou
   uvicorn app.main:app --reload --port 8000
   ```

2. **Registre um novo usuário:**
   - Acesse o frontend em `http://localhost:5173`
   - Vá para "Criar Conta"
   - Preencha os dados
   - Clique em "Cadastrar"

3. **Verifique os logs:**
   ```
   [EMAIL] Enviando email de verificação para usuario@exemplo.com via Resend...
   [EMAIL] ✅ Código de verificação enviado para usuario@exemplo.com via Resend
   ```

4. **Verifique a caixa de entrada:**
   - O email deve chegar em alguns segundos
   - Verifique também a pasta de spam

### Opção 2: Teste Direto via Python

Crie um script de teste `test_resend.py`:

```python
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app.core.config import settings
from app.services.email_service import send_verification_email

# Testar envio de email
email = "seu-email@exemplo.com"
code = "123456"
name = "Teste"

print(f"Enviando email de teste para {email}...")
result = send_verification_email(email, code, name)

if result:
    print("✅ Email enviado com sucesso!")
else:
    print("❌ Falha ao enviar email")
```

Execute:
```bash
cd backend
python3 test_resend.py
```

---

## ✅ Verificações

### Se o email não for enviado:

1. **Verifique se a API Key está correta:**
   ```bash
   # No .env, confirme que RESEND_API_KEY começa com "re_"
   ```

2. **Verifique os logs:**
   - Deve aparecer: `[EMAIL] Enviando email...`
   - Se aparecer erro, verifique a mensagem

3. **Verifique o dashboard do Resend:**
   - Acesse: https://resend.com/emails
   - Veja se o email aparece na lista
   - Verifique se há erros

4. **Teste com domínio de teste:**
   - Se `noreply@cosmoastral.com.br` não funcionar, use:
   - `EMAIL_FROM=cosmoastral@resend.dev` (domínio de teste)

---

## 🆘 Troubleshooting

### Erro: "RESEND_API_KEY não configurado"
- ✅ Verifique se o arquivo `.env` está na pasta `backend/`
- ✅ Verifique se a variável está escrita corretamente
- ✅ Reinicie o servidor após alterar o `.env`

### Erro: "Invalid API key"
- ✅ Verifique se a chave começa com `re_`
- ✅ Verifique se copiou a chave completa
- ✅ Gere uma nova chave no Resend

### Erro: "Domain not verified"
- ✅ Use `cosmoastral@resend.dev` temporariamente
- ✅ Ou verifique o domínio no dashboard do Resend

### Email não chega
- ✅ Verifique a pasta de spam
- ✅ Verifique o dashboard do Resend (https://resend.com/emails)
- ✅ Confirme que o email está correto

---

## 📝 Exemplo Completo de `.env` Local

```env
# Database
DATABASE_URL=sqlite:///./astrologia.db

# Security
SECRET_KEY=chave-local-teste-12345678901234567890
GROQ_API_KEY=gsk_sua-chave-groq-aqui

# Email (Resend)
RESEND_API_KEY=re_sua-api-key-do-resend-aqui
EMAIL_FROM=noreply@cosmoastral.com.br

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173
```

---

## 🎯 Próximos Passos

1. ✅ Configure o `.env` com `RESEND_API_KEY`
2. ✅ Instale a biblioteca: `pip install resend`
3. ✅ Inicie o servidor
4. ✅ Teste o registro de usuário
5. ✅ Verifique o email na caixa de entrada

---

**Status:** ✅ Pronto para testar localmente!

