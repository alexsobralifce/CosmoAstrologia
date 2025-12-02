# 🚀 Configuração do Resend no Railway - Guia Rápido

## ✅ **NÃO precisa configurar SMTP!**

O Resend **NÃO usa SMTP**. É uma API simples que funciona via HTTP. Você só precisa de **2 variáveis de ambiente**.

---

## 📋 **Variáveis Necessárias no Railway**

No painel do Railway, vá para **Variables** e adicione apenas estas 2 variáveis:

### 1. **RESEND_API_KEY** (Obrigatório)
```
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Como obter:**
1. Acesse: https://resend.com/
2. Faça login ou crie uma conta
3. Vá para **API Keys** no menu
4. Clique em **Create API Key**
5. Dê um nome (ex: "Railway Production")
6. Copie a chave (começa com `re_`)
7. Cole no Railway

### 2. **EMAIL_FROM** (Obrigatório)
```
EMAIL_FROM=noreply@cosmoastral.com.br
```

**✅ Domínio verificado:**
- `noreply@cosmoastral.com.br` - Domínio verificado no Resend (produção)
- `cosmoastral@resend.dev` - Alternativa para testes (domínio de teste do Resend)

---

## 🎯 **Passo a Passo no Railway**

1. **Acesse seu projeto no Railway**
   - Vá para https://railway.app
   - Selecione seu projeto

2. **Selecione o serviço Backend**
   - Clique no serviço do backend

3. **Vá para Variables**
   - Clique na aba **"Variables"** (Variáveis)

4. **Adicione as variáveis:**
   - Clique em **"New Variable"**
   - Nome: `RESEND_API_KEY`
   - Valor: `re_sua-chave-aqui`
   - Clique em **"Add"**
   
   - Clique em **"New Variable"** novamente
   - Nome: `EMAIL_FROM`
   - Valor: `noreply@cosmoastral.com.br`
   - Clique em **"Add"**

5. **Pronto!**
   - O Railway fará deploy automaticamente
   - Ou clique em **"Redeploy"** se necessário

---

## ✅ **Verificação**

Após o deploy, teste:

1. **Registre um novo usuário**
2. **Verifique os logs do Railway:**
   ```
   [EMAIL] Enviando email de verificação para usuario@exemplo.com via Resend...
   [EMAIL] ✅ Código de verificação enviado para usuario@exemplo.com via Resend
   ```
3. **Verifique a caixa de entrada do email**

---

## 🆘 **Troubleshooting**

### Erro: "RESEND_API_KEY não configurado"
- ✅ Verifique se a variável está no Railway
- ✅ Verifique se o nome está correto (case-sensitive)
- ✅ Verifique se não há espaços extras

### Erro: "Invalid API key"
- ✅ Verifique se a chave começa com `re_`
- ✅ Verifique se copiou a chave completa
- ✅ Gere uma nova chave no Resend se necessário

### Email não chega
- ✅ Verifique a pasta de spam
- ✅ Verifique os logs do Resend no dashboard
- ✅ Confirme que o email está correto

---

## 📊 **Exemplo Completo de Variáveis no Railway**

```
SECRET_KEY=xK9mP2qR7vT4wY8zA1bC3dE5fG6hI0jK2lM4nO6pQ8rS0tU
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
EMAIL_FROM=noreply@cosmoastral.com.br
DATABASE_URL=postgresql://... (automático se usar PostgreSQL)
CORS_ORIGINS=https://seu-frontend.vercel.app
```

---

## 🎉 **Pronto!**

Não precisa configurar nada mais. O Resend funciona automaticamente via API, sem necessidade de SMTP, portas, ou configurações complexas!

---

**Status:** ✅ Configuração simples - apenas 2 variáveis de ambiente!

