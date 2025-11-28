# 🔐 Guia Completo: Configurar Google OAuth

Este guia mostra passo a passo como configurar o Google OAuth para usar autenticação real do Google (em vez do modal simulado).

---

## 📋 Pré-requisitos

- Conta Google (Gmail)
- Acesso ao [Google Cloud Console](https://console.cloud.google.com/)

---

## 🎯 Passo 1: Criar Projeto no Google Cloud Console

1. **Acesse o Google Cloud Console:**
   - Vá para: https://console.cloud.google.com/
   - Faça login com sua conta Google

2. **Criar um novo projeto:**
   - Clique no seletor de projeto (topo da página)
   - Clique em **"Novo Projeto"** ou **"New Project"**
   - Nome do projeto: `Cosmos Astral` (ou qualquer nome)
   - Clique em **"Criar"** ou **"Create"**

3. **Selecionar o projeto:**
   - Após criar, selecione o projeto no seletor

---

## 🎯 Passo 2: Configurar Tela de Consentimento OAuth

1. **Acesse a configuração OAuth:**
   - No menu lateral, vá em **"APIs e Serviços"** → **"Tela de consentimento OAuth"**
   - Ou acesse diretamente: https://console.cloud.google.com/apis/credentials/consent

2. **Configurar tipo de usuário:**
   - Selecione **"Externo"** (External) para permitir qualquer usuário Google
   - Clique em **"Criar"** ou **"Create"**

3. **Preencher informações do app:**
   - **Nome do app:** `Cosmos Astral` (ou qualquer nome)
   - **Email de suporte do usuário:** Seu email
   - **Logo do app:** (Opcional - pode pular)
   - **Domínio do app:** (Opcional - pode pular)
   - Clique em **"Salvar e continuar"** ou **"Save and Continue"**

4. **Escopos (Scopes):**
   - Clique em **"Adicionar ou remover escopos"**
   - Selecione:
     - ✅ `email`
     - ✅ `profile`
     - ✅ `openid`
   - Clique em **"Atualizar"** ou **"Update"**
   - Clique em **"Salvar e continuar"**

5. **Usuários de teste (se necessário):**
   - Se o app estiver em modo "Teste", adicione emails de teste
   - Ou publique o app (para produção)
   - Clique em **"Salvar e continuar"**

6. **Resumo:**
   - Revise as informações
   - Clique em **"Voltar ao painel"** ou **"Back to Dashboard"**

---

## 🎯 Passo 3: Criar Credenciais OAuth 2.0

1. **Acesse Credenciais:**
   - No menu lateral, vá em **"APIs e Serviços"** → **"Credenciais"**
   - Ou acesse diretamente: https://console.cloud.google.com/apis/credentials

2. **Criar credencial:**
   - Clique em **"+ CRIAR CREDENCIAIS"** ou **"+ CREATE CREDENTIALS"**
   - Selecione **"ID do cliente OAuth 2.0"** ou **"OAuth 2.0 Client ID"**

3. **Configurar ID do cliente:**
   - **Tipo de aplicativo:** Selecione **"Aplicativo da Web"** ou **"Web application"**
   - **Nome:** `Cosmos Astral Web Client` (ou qualquer nome)

4. **Origens JavaScript autorizadas:**
   - Clique em **"+ ADICIONAR URI"** ou **"+ ADD URI"**
   - Adicione as URLs do seu frontend:
     - Para desenvolvimento local: `http://localhost:3000`
     - Para desenvolvimento local (Vite): `http://localhost:5173`
     - Para produção (Vercel): `https://seu-app.vercel.app`
     - ⚠️ **Adicione todas as URLs que você vai usar!**

5. **URIs de redirecionamento autorizados:**
   - Clique em **"+ ADICIONAR URI"** ou **"+ ADD URI"**
   - Adicione as mesmas URLs do passo anterior:
     - `http://localhost:3000`
     - `http://localhost:5173`
     - `https://seu-app.vercel.app`
     - ⚠️ **Adicione todas as URLs que você vai usar!**

6. **Criar:**
   - Clique em **"Criar"** ou **"Create"**

7. **Copiar credenciais:**
   - Uma janela vai abrir com suas credenciais
   - **ID do cliente (Client ID):** Copie este valor! (formato: `xxxxx.apps.googleusercontent.com`)
   - **Segredo do cliente (Client Secret):** Copie este valor também!
   - ⚠️ **IMPORTANTE:** Anote esses valores! Você não vai conseguir ver o Client Secret novamente.

---

## 🎯 Passo 4: Configurar Variáveis de Ambiente

### 4.1. Desenvolvimento Local (Frontend)

1. **Criar arquivo `.env.local` na raiz do projeto:**
   ```bash
   cd /Users/alexandrerocha/CosmoAstrologia
   cp .env.local.example .env.local
   ```

2. **Editar `.env.local`:**
   ```env
   # URL do Backend
   VITE_API_URL=http://localhost:8000

   # Google OAuth Client ID
   VITE_GOOGLE_CLIENT_ID=seu-client-id-aqui.apps.googleusercontent.com
   ```
   - ⚠️ **Substitua** `seu-client-id-aqui.apps.googleusercontent.com` pelo Client ID que você copiou!

3. **Salvar o arquivo**

### 4.2. Desenvolvimento Local (Backend)

1. **Criar/editar arquivo `backend/.env`:**
   ```bash
   cd backend
   ```

2. **Adicionar ao `.env`:**
   ```env
   # Google OAuth
   GOOGLE_CLIENT_ID=seu-client-id-aqui.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=seu-client-secret-aqui
   ```
   - ⚠️ **Substitua** pelos valores que você copiou!

3. **Salvar o arquivo**

### 4.3. Produção (Vercel - Frontend)

1. **No Vercel Dashboard:**
   - Acesse: https://vercel.com
   - Selecione seu projeto
   - Vá em **Settings** → **Environment Variables**

2. **Adicionar variável:**
   - **Key:** `VITE_GOOGLE_CLIENT_ID`
   - **Value:** `seu-client-id-aqui.apps.googleusercontent.com`
   - **Environment:** Selecione todos (Production, Preview, Development)
   - Clique em **Save**

3. **Fazer redeploy:**
   - Vá em **Deployments**
   - Clique nos três pontos do último deploy
   - Clique em **Redeploy**

### 4.4. Produção (Railway - Backend)

1. **No Railway Dashboard:**
   - Acesse: https://railway.app
   - Selecione seu projeto
   - Vá em **Variables**

2. **Adicionar variáveis:**
   - **GOOGLE_CLIENT_ID:** `seu-client-id-aqui.apps.googleusercontent.com`
   - **GOOGLE_CLIENT_SECRET:** `seu-client-secret-aqui`
   - Clique em **Add** para cada uma

3. **Redeploy automático:**
   - O Railway vai fazer redeploy automaticamente quando você adicionar variáveis

---

## 🎯 Passo 5: Atualizar Origens JavaScript no Google Cloud

⚠️ **IMPORTANTE:** Sempre que você adicionar uma nova URL (ex: novo deploy no Vercel), você precisa adicionar ela no Google Cloud Console!

1. **Acesse Credenciais:**
   - https://console.cloud.google.com/apis/credentials

2. **Editar o OAuth Client:**
   - Clique no nome do seu OAuth Client ID

3. **Adicionar novas URLs:**
   - Em **"Origens JavaScript autorizadas"**, adicione a nova URL
   - Em **"URIs de redirecionamento autorizados"**, adicione a nova URL
   - Clique em **"Salvar"** ou **"Save"**

---

## ✅ Testar

1. **Reiniciar servidores:**
   ```bash
   # Parar servidores (Ctrl+C)
   # Reiniciar frontend
   npm run dev

   # Reiniciar backend (em outro terminal)
   cd backend
   python3 run.py
   ```

2. **Abrir o frontend:**
   - Acesse: http://localhost:3000 ou http://localhost:5173

3. **Testar login Google:**
   - Clique no botão **"Google"**
   - Deve abrir popup do Google (não modal simulado)
   - Faça login com sua conta Google
   - O sistema deve capturar seu email automaticamente

---

## 🔍 Troubleshooting

### Problema: "Modal simulado ainda aparece"

**Solução:**
- Verifique se `VITE_GOOGLE_CLIENT_ID` está configurado no `.env.local`
- Reinicie o servidor de desenvolvimento (`npm run dev`)
- Verifique no console do navegador se há erros

### Problema: "Erro 400: redirect_uri_mismatch"

**Solução:**
- Verifique se a URL do frontend está adicionada em **"URIs de redirecionamento autorizados"** no Google Cloud Console
- A URL deve ser exatamente igual (com ou sem barra final, http vs https, etc.)

### Problema: "Erro ao verificar token"

**Solução:**
- Verifique se `GOOGLE_CLIENT_ID` está configurado no backend
- Verifique se o Client ID do frontend e backend são iguais (ou use IDs diferentes se configurado assim)
- Verifique os logs do backend para mais detalhes

### Problema: "Google Identity Services não disponível"

**Solução:**
- Verifique se o script do Google está carregando (veja Network tab no DevTools)
- Verifique se não há bloqueadores de popup
- Tente em modo anônimo/privado

---

## 📚 Referências

- [Google Identity Services Documentation](https://developers.google.com/identity/gsi/web)
- [Google Cloud Console](https://console.cloud.google.com/)
- [OAuth 2.0 Setup Guide](https://developers.google.com/identity/protocols/oauth2/web-server)

---

## ✅ Checklist

- [ ] Projeto criado no Google Cloud Console
- [ ] Tela de consentimento OAuth configurada
- [ ] OAuth Client ID criado
- [ ] URLs adicionadas em "Origens JavaScript autorizadas"
- [ ] URLs adicionadas em "URIs de redirecionamento autorizados"
- [ ] Client ID e Client Secret copiados
- [ ] `.env.local` criado com `VITE_GOOGLE_CLIENT_ID`
- [ ] `backend/.env` atualizado com `GOOGLE_CLIENT_ID` e `GOOGLE_CLIENT_SECRET`
- [ ] Variáveis configuradas no Vercel (produção)
- [ ] Variáveis configuradas no Railway (produção)
- [ ] Teste local funcionando
- [ ] Teste em produção funcionando

---

## 💡 Dicas

1. **Use IDs diferentes para desenvolvimento e produção:**
   - Crie dois OAuth Client IDs no Google Cloud Console
   - Um para desenvolvimento (localhost)
   - Um para produção (Vercel)

2. **Mantenha segredo:**
   - Nunca commite `.env.local` ou `backend/.env` no Git
   - Esses arquivos já estão no `.gitignore`

3. **Teste em diferentes ambientes:**
   - Teste localmente primeiro
   - Depois teste em produção

4. **Monitore logs:**
   - Console do navegador (frontend)
   - Terminal do backend
   - Google Cloud Console → Logs

