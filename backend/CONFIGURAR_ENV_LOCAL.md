# ⚙️ Configurar .env Local para Resend

## ❌ Problema Identificado

O `RESEND_API_KEY` não está configurado no arquivo `.env`.

---

## ✅ Solução Rápida

### 1. **Edite o arquivo `backend/.env`**

Adicione estas linhas:

```env
RESEND_API_KEY=re_sua-api-key-aqui
EMAIL_FROM=noreply@cosmoastral.com.br
```

### 2. **Obter a API Key do Resend**

1. Acesse: https://resend.com/api-keys
2. Faça login ou crie uma conta
3. Clique em **"Create API Key"**
4. Dê um nome (ex: "Local Development")
5. **Copie a chave** (começa com `re_`)
6. Cole no `.env` como `RESEND_API_KEY=re_...`

### 3. **Testar a Configuração**

Execute o script de teste:

```bash
cd backend
source venv/bin/activate
python3 test_resend_local.py
```

Ou teste via registro de usuário:
1. Inicie o servidor: `python3 main.py`
2. Registre um novo usuário no frontend
3. Verifique os logs e a caixa de entrada

---

## 📝 Exemplo Completo de `.env`

```env
# Database
DATABASE_URL=sqlite:///./astrologia.db

# Security
SECRET_KEY=chave-local-teste-12345678901234567890
GROQ_API_KEY=sua-chave-groq-aqui

# Email (Resend) - OBRIGATÓRIO
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
EMAIL_FROM=noreply@cosmoastral.com.br

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## 🔍 Verificar se Está Funcionando

Após configurar, você deve ver nos logs:

```
[EMAIL] Enviando email de verificação para usuario@exemplo.com via Resend...
[EMAIL] ✅ Código de verificação enviado para usuario@exemplo.com via Resend
```

Se aparecer:
```
[WARNING] RESEND_API_KEY não configurado
```
→ Adicione a variável no `.env` e reinicie o servidor.

---

**Status:** ⚠️ Configure `RESEND_API_KEY` no `.env` para testar localmente

