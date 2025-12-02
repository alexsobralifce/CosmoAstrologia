# 🧪 Como Testar o Resend Localmente

## 📋 Passo a Passo

### 1. **Instalar a biblioteca Resend**

```bash
cd backend
pip install resend
```

Ou instale todas as dependências:

```bash
pip install -r requirements.txt
```

### 2. **Configurar o arquivo `.env`**

Crie ou edite o arquivo `backend/.env` com:

```env
# Database (local)
DATABASE_URL=sqlite:///./astrologia.db

# Security
SECRET_KEY=chave-local-teste-12345678901234567890
GROQ_API_KEY=sua-chave-groq-aqui

# Email (Resend) - OBRIGATÓRIO
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
EMAIL_FROM=noreply@cosmoastral.com.br

# CORS (para desenvolvimento local)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 3. **Obter a API Key do Resend**

1. Acesse: https://resend.com/
2. Faça login ou crie uma conta (grátis até 3.000 emails/mês)
3. Vá para **API Keys** no dashboard
4. Clique em **Create API Key**
5. Dê um nome (ex: "Local Development")
6. **Copie a chave** (começa com `re_`)
7. Cole no arquivo `.env` como `RESEND_API_KEY`

### 4. **Iniciar o servidor**

```bash
cd backend
python3 main.py
```

Ou com uvicorn:

```bash
uvicorn app.main:app --reload --port 8000
```

### 5. **Testar o envio de email**

**Opção A: Via Frontend**
1. Acesse `http://localhost:5173`
2. Vá para "Criar Conta"
3. Preencha os dados e registre
4. Verifique os logs do backend
5. Verifique a caixa de entrada do email

**Opção B: Teste Direto**
Crie um arquivo `test_email.py`:

```python
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app.services.email_service import send_verification_email

# Teste
result = send_verification_email(
    email="seu-email@exemplo.com",
    code="123456",
    name="Teste Local"
)

print("✅ Email enviado!" if result else "❌ Falha ao enviar")
```

Execute:
```bash
python3 test_email.py
```

---

## ✅ Verificações

### Logs Esperados:

```
[EMAIL] Enviando email de verificação para usuario@exemplo.com via Resend...
[EMAIL] ✅ Código de verificação enviado para usuario@exemplo.com via Resend
```

### Se aparecer erro:

1. **"RESEND_API_KEY não configurado"**
   - Verifique se o `.env` está na pasta `backend/`
   - Verifique se a variável está escrita corretamente
   - Reinicie o servidor

2. **"Invalid API key"**
   - Verifique se a chave começa com `re_`
   - Verifique se copiou a chave completa
   - Gere uma nova chave no Resend

3. **Email não chega**
   - Verifique a pasta de spam
   - Verifique o dashboard do Resend: https://resend.com/emails
   - Confirme que o email está correto

---

## 🎯 Checklist Rápido

- [ ] Biblioteca `resend` instalada (`pip install resend`)
- [ ] Arquivo `.env` criado na pasta `backend/`
- [ ] `RESEND_API_KEY` configurado no `.env`
- [ ] `EMAIL_FROM` configurado no `.env`
- [ ] Servidor iniciado (`python3 main.py`)
- [ ] Teste de registro realizado
- [ ] Email recebido na caixa de entrada

---

**Status:** ✅ Pronto para testar!

