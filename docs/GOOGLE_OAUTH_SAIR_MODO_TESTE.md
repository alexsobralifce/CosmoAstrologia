# 🔐 Como Sair do Modo de Teste do Google OAuth

## 🚨 Problema

Você está vendo a mensagem:

```
Usando modo de teste. Configure VITE_GOOGLE_CLIENT_ID para usar OAuth real.
```

Isso significa que:

1. A variável `VITE_GOOGLE_CLIENT_ID` não está configurada, OU
2. O app está em modo de teste no Google Cloud Console

## ✅ Solução Completa

### Passo 1: Obter Client ID do Google Cloud Console

1. **Acesse:** https://console.cloud.google.com/
2. **Selecione seu projeto**
3. **Vá em:** APIs & Services → Credentials
4. **Encontre seu OAuth 2.0 Client ID**
5. **Copie o Client ID** (formato: `xxxxx.apps.googleusercontent.com`)

### Passo 2: Configurar no Vercel

1. **Acesse:** https://vercel.com
2. **Selecione seu projeto**
3. **Vá em:** Settings → Environment Variables
4. **Adicione:**
   - **Key:** `VITE_GOOGLE_CLIENT_ID`
   - **Value:** `seu-client-id.apps.googleusercontent.com` (cole o Client ID copiado)
   - **Environment:** Selecione todos (Production, Preview, Development)
5. **Clique em Save**

### Passo 3: Publicar o App no Google (Sair do Modo de Teste)

⚠️ **IMPORTANTE:** Para usar OAuth real, você precisa publicar o app no Google.

1. **Acesse:** https://console.cloud.google.com/
2. **Selecione seu projeto**
3. **Vá em:** APIs & Services → OAuth consent screen
4. **Verifique o status:**

   - Se estiver em "Testing" (Teste), você precisa publicar

5. **Para publicar:**

   - Role até o final da página
   - Clique em **"PUBLISH APP"** ou **"PUBLICAR APP"**
   - Confirme a publicação

6. **Avisos de publicação:**
   - ⚠️ Após publicar, qualquer usuário com conta Google pode usar o app
   - ⚠️ Você não precisa mais adicionar usuários de teste
   - ⚠️ O app ficará público

### Passo 4: Verificar URLs Autorizadas

Certifique-se de que as URLs estão configuradas:

1. **Vá em:** APIs & Services → Credentials
2. **Clique no seu OAuth Client ID**
3. **Verifique "Authorized JavaScript origins":**

   ```
   http://localhost:3000
   http://localhost:5173
   https://seu-app.vercel.app
   ```

4. **Verifique "Authorized redirect URIs":**
   ```
   http://localhost:3000
   http://localhost:5173
   https://seu-app.vercel.app
   ```

### Passo 5: Redeploy no Vercel

**CRÍTICO:** Após configurar a variável, você DEVE fazer redeploy:

1. **Vá em:** Deployments
2. **Clique nos 3 pontos** do último deploy
3. **Selecione:** Redeploy
4. **Aguarde** o build completar

## 🔍 Verificação

### Verificar se está funcionando:

1. **Acesse seu app no Vercel**
2. **Clique no botão "Google"**
3. **Deve abrir o popup oficial do Google** (não modal simulado)
4. **Faça login com sua conta Google**
5. **O sistema deve capturar seu email automaticamente**

### Se ainda aparecer "modo de teste":

1. **Verifique se `VITE_GOOGLE_CLIENT_ID` está configurada no Vercel**
2. **Verifique se fez redeploy após configurar**
3. **Verifique se o app está publicado no Google Cloud Console**
4. **Aguarde alguns minutos** (pode levar tempo para propagar)

## ⚠️ Modo de Teste vs Produção

### Modo de Teste (Testing):

- ✅ Funciona apenas para usuários adicionados como "Test users"
- ✅ Mais seguro para desenvolvimento
- ❌ Limitado a 100 usuários de teste
- ❌ Requer adicionar cada usuário manualmente

### Modo de Produção (Published):

- ✅ Qualquer usuário Google pode usar
- ✅ Sem limite de usuários
- ⚠️ App fica público
- ⚠️ Requer revisão do Google se usar escopos sensíveis

## 📝 Checklist

- [ ] Client ID obtido do Google Cloud Console
- [ ] `VITE_GOOGLE_CLIENT_ID` configurada no Vercel
- [ ] URLs autorizadas configuradas no Google Console
- [ ] App publicado no Google (sair do modo de teste)
- [ ] Redeploy feito no Vercel
- [ ] Testado em produção

## 🆘 Problemas Comuns

### Erro: "redirect_uri_mismatch"

**Solução:**

1. Verifique se a URL do Vercel está em "Authorized JavaScript origins"
2. A URL deve ser exatamente igual (com `https://`, sem barra final)

### Erro: "invalid_client"

**Solução:**

1. Verifique se `VITE_GOOGLE_CLIENT_ID` está correto no Vercel
2. Verifique se fez redeploy após configurar
3. Verifique se não há espaços extras no Client ID

### Ainda aparece "modo de teste"

**Solução:**

1. Verifique se o app está publicado no Google Cloud Console
2. Aguarde alguns minutos após publicar
3. Limpe o cache do navegador
4. Teste em modo anônimo/privado

## 📚 Documentação Relacionada

- `GOOGLE_OAUTH_SETUP.md` - Guia completo de setup
- `GOOGLE_OAUTH_VERCEL_CONFIG.md` - Configuração específica para Vercel
- `GOOGLE_OAUTH_VERCEL.md` - Guia detalhado para Vercel

## 🎯 Resumo Rápido

```bash
1. Google Cloud Console → Credentials → Copiar Client ID
2. Vercel → Settings → Environment Variables → Adicionar VITE_GOOGLE_CLIENT_ID
3. Google Cloud Console → OAuth consent screen → PUBLICAR APP
4. Vercel → Deployments → Redeploy
5. Testar
```
