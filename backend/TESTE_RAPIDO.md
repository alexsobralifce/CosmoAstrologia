# ⚡ Teste Rápido do Resend - Local

## ✅ Resend já está instalado!

A biblioteca `resend` foi instalada no seu ambiente virtual.

---

## 🚀 Passos para Testar

### 1. **Configurar o `.env`**

Edite o arquivo `backend/.env` e adicione:

```env
RESEND_API_KEY=re_sua-api-key-aqui
EMAIL_FROM=noreply@cosmoastral.com.br
```

**Como obter a API Key:**
1. Acesse: https://resend.com/api-keys
2. Crie uma nova API Key
3. Copie a chave (começa com `re_`)
4. Cole no `.env`

### 2. **Iniciar o servidor**

```bash
cd backend
source venv/bin/activate
python3 main.py
```

### 3. **Testar**

1. Acesse o frontend: `http://localhost:5173`
2. Registre um novo usuário
3. Verifique os logs:
   ```
   [EMAIL] ✅ Código de verificação enviado...
   ```
4. Verifique a caixa de entrada do email

---

## 📝 Exemplo de `.env` Completo

```env
# Database
DATABASE_URL=sqlite:///./astrologia.db

# Security
SECRET_KEY=chave-local-teste
GROQ_API_KEY=sua-chave-groq

# Email (Resend)
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
EMAIL_FROM=noreply@cosmoastral.com.br

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## ✅ Checklist

- [x] Resend instalado
- [ ] `.env` configurado com `RESEND_API_KEY`
- [ ] Servidor iniciado
- [ ] Teste de registro realizado
- [ ] Email recebido

---

**Pronto para testar!** 🎉

