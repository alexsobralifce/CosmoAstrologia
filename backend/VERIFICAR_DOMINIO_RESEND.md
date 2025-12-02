# 🔍 Verificar Domínio no Resend

## ❌ Problema Identificado

O domínio `cosmoastral.com.br` **não está verificado** no Resend.

**Erro:**
```
The cosmoastral.com.br domain is not verified. 
Please, add and verify your domain on https://resend.com/domains
```

---

## ✅ Soluções

### **Opção 1: Verificar o Domínio no Resend (Recomendado para Produção)**

1. **Acesse o dashboard do Resend:**
   - https://resend.com/domains

2. **Adicione o domínio:**
   - Clique em **"Add Domain"**
   - Digite: `cosmoastral.com.br`
   - Clique em **"Add"**

3. **Configure os registros DNS:**
   - O Resend fornecerá registros DNS para adicionar
   - Exemplo:
     ```
     Tipo: TXT
     Nome: @
     Valor: resend-verification=xxxxx
     ```

4. **Aguarde a verificação:**
   - Pode levar alguns minutos
   - Status mudará para "Verified"

5. **Atualize o `.env`:**
   ```env
   EMAIL_FROM=noreply@cosmoastral.com.br
   ```

### **Opção 2: Usar Domínio de Teste (Para Desenvolvimento Local)**

Para testar localmente sem verificar domínio:

1. **Atualize o `.env`:**
   ```env
   EMAIL_FROM=cosmoastral@resend.dev
   ```

2. **Limitação:**
   - ⚠️ Só pode enviar para o email da sua conta do Resend
   - Para testar, use o email que você usou para criar a conta

3. **Para produção:**
   - Você **DEVE** verificar o domínio
   - Use `noreply@cosmoastral.com.br`

---

## 🧪 Teste Local (Com Domínio de Teste)

Se você configurou `EMAIL_FROM=cosmoastral@resend.dev`:

1. **Use o email da sua conta Resend para teste:**
   - O email que você usou para criar a conta no Resend
   - Exemplo: `plribeirorocha@gmail.com` (conforme erro)

2. **Teste:**
   ```bash
   cd backend
   source venv/bin/activate
   python3 -c "
   from app.services.email_service import send_verification_email
   send_verification_email('plribeirorocha@gmail.com', '123456', 'Teste')
   "
   ```

---

## 🚀 Produção (Railway)

Para produção, você **DEVE** verificar o domínio:

1. **Verifique o domínio no Resend**
2. **Configure no Railway:**
   ```env
   RESEND_API_KEY=re_sua-api-key
   EMAIL_FROM=noreply@cosmoastral.com.br
   ```

---

## 📋 Checklist

### Para Desenvolvimento Local:
- [ ] `EMAIL_FROM=cosmoastral@resend.dev` no `.env`
- [ ] Testar apenas com email da conta Resend
- [ ] Funciona para testes locais

### Para Produção:
- [ ] Domínio `cosmoastral.com.br` verificado no Resend
- [ ] `EMAIL_FROM=noreply@cosmoastral.com.br` no Railway
- [ ] Pode enviar para qualquer email

---

**Status:** ⚠️ Domínio precisa ser verificado no Resend para produção

