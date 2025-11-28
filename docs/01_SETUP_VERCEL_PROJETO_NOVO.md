# 🚀 Setup Completo: Adicionar Projeto no Vercel (Passo a Passo)

Guia completo para configurar um projeto novo no Vercel do zero.

## 📋 Checklist de Configuração

### 1️⃣ Conectar Repositório GitHub

1. Acesse: https://vercel.com
2. Clique em **Add New** → **Project**
3. Selecione **Import Git Repository**
4. Escolha: `alexsobralifce/CosmoAstrologia`
5. Clique em **Import**

### 2️⃣ Configurar Build Settings

Na tela de configuração do projeto:

- **Framework Preset:** `Vite` (ou deixe "Other" se não aparecer)
- **Root Directory:** `/` (raiz - deixe vazio)
- **Build Command:** `npm run build`
- **Output Directory:** `build`
- **Install Command:** `npm ci` (ou deixe padrão)

**⚠️ IMPORTANTE:** 
- O Output Directory **DEVE** ser `build` (não `dist`)
- O Build Command **DEVE** ser `npm run build`

### 3️⃣ Configurar Variáveis de Ambiente

**Antes de fazer deploy**, configure as variáveis:

1. Na tela de configuração, role até **Environment Variables**
2. Ou após criar, vá em **Settings** → **Environment Variables**

**Adicione estas variáveis:**

```
VITE_API_URL = https://seu-backend.railway.app
```

**⚠️ CRÍTICO:** 
- **NÃO** use `http://localhost:8000` em produção!
- Use a URL do seu backend em produção (Railway)
- Exemplo: `https://cosmoastrologia-backend.railway.app`

```
VITE_GOOGLE_CLIENT_ID = seu-client-id.apps.googleusercontent.com
```

**Configuração:**
- **Environment:** Selecione todos (Production, Preview, Development)
- Clique em **Add** para cada variável

### 4️⃣ Fazer Primeiro Deploy

1. Após configurar tudo, clique em **Deploy**
2. Aguarde o build completar (pode levar 1-3 minutos)
3. Verifique se o status fica **verde** (sucesso)

**⚠️ IMPORTANTE:** 
- Se você adicionar variáveis de ambiente **DEPOIS** do deploy, faça **Redeploy**
- Variáveis só são aplicadas em novos deploys
- Vá em Deployments → 3 pontos → Redeploy

### 5️⃣ Verificar Deploy

1. Após deploy bem-sucedido, você verá uma URL tipo:
   - `https://cosmoastrologia.vercel.app`
   - Ou `https://cosmoastrologia-xxxxx.vercel.app`

2. **Teste a URL:**
   - Deve carregar o frontend
   - Verifique console do navegador (F12) para erros

### 6️⃣ Configurar Google OAuth no Google Cloud Console

**⚠️ CRÍTICO:** Após ter a URL do Vercel, configure no Google:

1. Acesse: https://console.cloud.google.com/
2. Vá em **APIs & Services** → **Credentials**
3. Clique no seu **OAuth 2.0 Client ID**
4. Em **Authorized JavaScript origins**, adicione:
   ```
   http://localhost:3000
   http://localhost:5173
   https://sua-url.vercel.app
   ```
5. Em **Authorized redirect URIs**, adicione as mesmas URLs
6. Clique em **Save**
7. Aguarde 2-5 minutos para propagar

### 7️⃣ Verificar Configurações Finais

1. **No Vercel:**
   - Settings → General → Verificar Build Settings
   - Settings → Environment Variables → Verificar variáveis
   - Settings → Git → Verificar branch (deve ser `main`)

2. **Testar:**
   - Acesse a URL do Vercel
   - Teste login com Google
   - Verifique se conecta ao backend

## ⚠️ Problemas Comuns

### Erro: "Não foi possível conectar ao backend em http://localhost:8000"

**Causa:** Variável `VITE_API_URL` não configurada ou usando valor padrão (localhost)

**Solução:**
1. Verificar se `VITE_API_URL` está configurada no Vercel
2. Verificar se o valor é URL de produção (não localhost)
3. Fazer **Redeploy** após configurar variável
4. Ver documento `VERCEL_ERRO_BACKEND_CONNECTION.md` para detalhes

### Build falha

**Verificar:**
- Build Command está correto? (`npm run build`)
- Output Directory está correto? (`build`)
- Variáveis de ambiente configuradas?

### Erro de variáveis de ambiente

**Solução:**
- Verificar se `VITE_API_URL` está configurada
- Verificar se `VITE_GOOGLE_CLIENT_ID` está configurada
- Fazer redeploy após adicionar variáveis

### Google OAuth não funciona

**Solução:**
- Verificar se URL do Vercel está no Google Console
- Verificar se `VITE_GOOGLE_CLIENT_ID` está configurada
- Aguardar propagação (2-5 minutos)

## ✅ Checklist Final

- [ ] Repositório conectado ao Vercel
- [ ] Build Settings configurados corretamente
- [ ] `VITE_API_URL` configurada
- [ ] `VITE_GOOGLE_CLIENT_ID` configurada
- [ ] Primeiro deploy bem-sucedido
- [ ] URL do Vercel adicionada no Google Console
- [ ] Testado login com Google
- [ ] Testado conexão com backend

## 📝 Ordem de Execução

1. **Conectar repositório** (Passo 1)
2. **Configurar build** (Passo 2)
3. **Configurar variáveis** (Passo 3) - **ANTES** de fazer deploy
4. **Fazer deploy** (Passo 4)
5. **Obter URL** (Passo 5)
6. **Configurar Google OAuth** (Passo 6) - **DEPOIS** de ter a URL
7. **Verificar tudo** (Passo 7)

## 🎯 Resumo Rápido

```bash
1. Vercel → Add New → Project → Import GitHub
2. Configurar: Build Command = "npm run build", Output = "build"
3. Adicionar: VITE_API_URL e VITE_GOOGLE_CLIENT_ID
4. Deploy
5. Copiar URL do Vercel
6. Google Console → Adicionar URL do Vercel
7. Testar
```

## 📚 Documentos Relacionados

- Ver documento `02_GOOGLE_OAUTH_VERCEL_CONFIG.md` para detalhes do Google OAuth
- Ver documento `03_VERCEL_DEPLOY_TROUBLESHOOTING.md` se tiver problemas

