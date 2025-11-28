# 🔐 Configuração do Google OAuth para Vercel

Este guia explica como configurar o Google OAuth no Google Cloud Console para funcionar com o frontend hospedado no Vercel.

## 📋 Pré-requisitos

- Conta no Google Cloud Platform
- Projeto criado no Google Cloud Console
- Credenciais OAuth 2.0 criadas
- Frontend deployado no Vercel (ou URL de produção)

## 🔧 Passo a Passo

### 1. Acessar o Google Cloud Console

1. Acesse: https://console.cloud.google.com/
2. Selecione seu projeto
3. Vá em **APIs & Services** → **Credentials**

### 2. Configurar OAuth Consent Screen (se ainda não fez)

1. Vá em **APIs & Services** → **OAuth consent screen**
2. Escolha **External** (para desenvolvimento) ou **Internal** (para Workspace)
3. Preencha:
   - **App name**: CosmoAstrologia (ou o nome que preferir)
   - **User support email**: Seu email
   - **Developer contact information**: Seu email
4. Clique em **Save and Continue**
5. Em **Scopes**, adicione:
   - `openid`
   - `email`
   - `profile`
6. Clique em **Save and Continue**
7. Em **Test users** (se External), adicione emails de teste
8. Clique em **Save and Continue**

### 3. Configurar Credenciais OAuth 2.0

1. Vá em **APIs & Services** → **Credentials**
2. Clique na credencial OAuth 2.0 Client ID que você criou
3. Ou crie uma nova:
   - Clique em **+ CREATE CREDENTIALS** → **OAuth client ID**
   - **Application type**: Web application
   - **Name**: CosmoAstrologia Web Client

### 4. Configurar Authorized JavaScript origins

Na seção **Authorized JavaScript origins**, adicione:

```
http://localhost:3000
http://localhost:5173
https://seu-app.vercel.app
```

**Importante:**
- ✅ Use `https://` para produção (Vercel)
- ✅ Use `http://` para desenvolvimento local
- ✅ Não inclua trailing slash (`/`)
- ✅ Adicione todas as URLs onde o frontend pode rodar

**Exemplo completo:**
```
http://localhost:3000
http://localhost:5173
http://127.0.0.1:3000
http://127.0.0.1:5173
https://cosmoastrologia.vercel.app
https://cosmoastrologia-git-main.vercel.app
https://cosmoastrologia-*.vercel.app
```

**Nota sobre preview deployments do Vercel:**
- O Vercel cria URLs únicas para cada branch/PR
- Você pode adicionar URLs específicas ou usar wildcard
- Ou adicionar URLs conforme necessário

### 5. Configurar Authorized redirect URIs

Na seção **Authorized redirect URIs**, adicione:

```
http://localhost:3000
http://localhost:5173
https://seu-app.vercel.app
```

**Importante:**
- ✅ Mesmas URLs do JavaScript origins
- ✅ Google Identity Services não usa redirect URI tradicional, mas é bom ter configurado
- ✅ Se usar Google Identity Services (como no nosso caso), o redirect é gerenciado automaticamente

### 6. Obter Client ID e Client Secret

1. Após salvar, você verá:
   - **Client ID**: `xxxxx.apps.googleusercontent.com`
   - **Client Secret**: `xxxxx` (se necessário para backend)

2. **Copie o Client ID** - você precisará dele

### 7. Configurar no Vercel

1. Acesse seu projeto no Vercel
2. Vá em **Settings** → **Environment Variables**
3. Adicione:
   ```
   VITE_GOOGLE_CLIENT_ID=seu-client-id-aqui.apps.googleusercontent.com
   ```
4. Clique em **Save**
5. **Redeploy** o projeto para aplicar as mudanças

### 8. Configurar no Backend (Railway)

Se você também usa Google OAuth no backend:

1. No Google Cloud Console, na mesma credencial:
   - Copie o **Client ID**
   - Copie o **Client Secret**

2. No Railway:
   - Adicione variável: `GOOGLE_CLIENT_ID=seu-client-id`
   - Adicione variável: `GOOGLE_CLIENT_SECRET=seu-client-secret`

## 🔍 Verificação

### Testar Localmente

1. Certifique-se de que `.env.local` tem:
   ```env
   VITE_GOOGLE_CLIENT_ID=seu-client-id.apps.googleusercontent.com
   ```

2. Inicie o frontend:
   ```bash
   npm run dev
   ```

3. Teste o botão de login com Google
4. Deve abrir o popup do Google

### Testar em Produção (Vercel)

1. Certifique-se de que a variável está configurada no Vercel
2. Certifique-se de que a URL do Vercel está em **Authorized JavaScript origins**
3. Acesse seu app no Vercel
4. Teste o botão de login com Google
5. Deve funcionar normalmente

## ⚠️ Problemas Comuns

### Erro: "redirect_uri_mismatch"

**Causa:** URL não está em **Authorized JavaScript origins**

**Solução:**
1. Verifique a URL exata que aparece no erro
2. Adicione ela em **Authorized JavaScript origins** no Google Console
3. Aguarde alguns minutos para propagar
4. Tente novamente

### Erro: "invalid_client"

**Causa:** Client ID incorreto ou não configurado

**Solução:**
1. Verifique se `VITE_GOOGLE_CLIENT_ID` está configurado no Vercel
2. Verifique se o Client ID está correto (sem espaços extras)
3. Redeploy o projeto no Vercel

### Popup bloqueado

**Causa:** Bloqueador de popup do navegador

**Solução:**
1. Permita popups para o domínio do Vercel
2. Teste em modo anônimo/privado
3. Verifique se não há extensões bloqueando

### Não funciona em preview deployments

**Causa:** URLs de preview não estão autorizadas

**Solução:**
1. Adicione a URL específica do preview em **Authorized JavaScript origins**
2. Ou use wildcard: `https://*-seu-app.vercel.app`
3. Ou adicione conforme necessário

## 📝 Checklist

- [ ] OAuth Consent Screen configurado
- [ ] Credenciais OAuth 2.0 criadas
- [ ] **Authorized JavaScript origins** inclui:
  - [ ] `http://localhost:3000`
  - [ ] `http://localhost:5173`
  - [ ] `https://seu-app.vercel.app`
  - [ ] URLs de preview (se necessário)
- [ ] **Authorized redirect URIs** configurado (mesmas URLs)
- [ ] Client ID copiado
- [ ] `VITE_GOOGLE_CLIENT_ID` configurado no Vercel
- [ ] Projeto redeployado no Vercel
- [ ] Testado localmente
- [ ] Testado em produção

## 🔐 Segurança

- ✅ **Nunca commite** o Client Secret no código
- ✅ Use variáveis de ambiente para todas as credenciais
- ✅ Client ID pode ser público (está no frontend)
- ✅ Client Secret deve ser mantido secreto (apenas backend)
- ✅ Revise periodicamente as URLs autorizadas

## 📚 Recursos

- [Google Identity Services Documentation](https://developers.google.com/identity/gsi/web)
- [Google OAuth 2.0 Setup](https://developers.google.com/identity/protocols/oauth2)
- [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)

## 🆘 Suporte

Se ainda tiver problemas:

1. Verifique os logs do console do navegador
2. Verifique os logs do Vercel
3. Verifique se a URL está exatamente como configurada no Google Console
4. Aguarde alguns minutos após mudanças no Google Console (propagação)

