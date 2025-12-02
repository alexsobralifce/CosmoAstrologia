# 🚀 Como Configurar RESEND_API_KEY no Railway

## ⚠️ Problema Identificado

O sistema está mostrando este aviso em produção:
```
[WARNING] RESEND_API_KEY não configurado - Código de verificação para alexandresobral2004@gmail.com: 487098
[WARNING] ⚠️  Configure RESEND_API_KEY no .env ou variáveis de ambiente
```

Isso significa que a variável `RESEND_API_KEY` **não está configurada no Railway**.

---

## ✅ Solução: Adicionar Variável no Railway

### Passo 1: Acessar o Railway

1. Acesse https://railway.app/
2. Faça login na sua conta
3. Selecione o projeto do **CosmoAstral**
4. Clique no serviço do **Backend**

### Passo 2: Adicionar Variável de Ambiente

1. No painel do serviço, vá para a aba **"Variables"** (Variáveis)
2. Clique em **"New Variable"** (Nova Variável)
3. Preencha:
   - **Nome:** `RESEND_API_KEY`
   - **Valor:** `re_UwnptTx8_8tvgZDv1EUgLrj1UZfvCqavy`
4. Clique em **"Add"** ou **"Save"**

### Passo 3: Adicionar EMAIL_FROM (se ainda não tiver)

Também adicione a variável `EMAIL_FROM`:

1. Clique em **"New Variable"** novamente
2. Preencha:
   - **Nome:** `EMAIL_FROM`
   - **Valor:** `noreply@cosmoastral.com.br` (se o domínio estiver verificado no Resend)
   - **OU:** `cosmoastral@resend.dev` (para testes, se o domínio não estiver verificado)
3. Clique em **"Add"** ou **"Save"**

### Passo 4: Redeploy (se necessário)

Após adicionar as variáveis:

1. O Railway pode fazer um **redeploy automático**
2. Se não fizer, vá para a aba **"Deployments"**
3. Clique em **"Redeploy"** no deploy mais recente

---

## ✅ Verificação

Após o redeploy, verifique os logs do Railway:

**Deve aparecer:**
```
[EMAIL] Enviando email de verificação para alexandresobral2004@gmail.com via Resend...
[EMAIL] ✅ Código de verificação enviado para alexandresobral2004@gmail.com via Resend
```

**NÃO deve aparecer:**
```
[WARNING] RESEND_API_KEY não configurado
```

---

## 📋 Checklist Completo de Variáveis no Railway

Certifique-se de que estas variáveis estão configuradas:

### ⚠️ Obrigatórias:
- [ ] `SECRET_KEY` - Chave secreta para JWT
- [ ] `GROQ_API_KEY` - Chave da API Groq
- [ ] `RESEND_API_KEY` - API Key do Resend ⭐ **ADICIONAR AGORA**
- [ ] `EMAIL_FROM` - Email remetente ⭐ **ADICIONAR AGORA**

### 🔧 Recomendadas:
- [ ] `DATABASE_URL` - Definida automaticamente se usar PostgreSQL
- [ ] `CORS_ORIGINS` - URLs do frontend separadas por vírgula

---

## 🔍 Como Verificar se Está Funcionando

### 1. Teste de Registro

1. Acesse o frontend em produção
2. Tente registrar um novo usuário
3. Verifique se o email foi enviado
4. Verifique os logs do Railway - não deve aparecer o aviso

### 2. Verificar Logs do Railway

1. No Railway, vá para a aba **"Deployments"**
2. Clique no deploy mais recente
3. Clique em **"View Logs"**
4. Procure por mensagens de email:
   - ✅ `[EMAIL] ✅ Código de verificação enviado` = Funcionando
   - ❌ `[WARNING] RESEND_API_KEY não configurado` = Não configurado

---

## 💡 Dica Importante

**O arquivo `.env` local NÃO é usado em produção!**

- ✅ **Local:** Variáveis vêm do arquivo `backend/.env`
- ✅ **Produção (Railway):** Variáveis vêm das **Variables** do Railway

Sempre configure as variáveis diretamente no painel do Railway para produção.

---

## 📚 Documentação Relacionada

- [Variáveis de Ambiente no Railway](./docs/RAILWAY_VARIAVEIS_AMBIENTE.md)
- [Configuração do Resend](./backend/CONFIGURACAO_RESEND.md)
- [Setup Resend no Railway](./backend/RAILWAY_RESEND_SETUP.md)

---

**Última atualização:** 2025-12-02

