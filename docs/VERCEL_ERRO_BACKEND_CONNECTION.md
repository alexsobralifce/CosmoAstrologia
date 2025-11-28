# 🔧 Erro: "Não foi possível conectar ao backend" no Vercel

## 🚨 Problema

Erro no Vercel (produção):
```
Não foi possível conectar ao backend em http://localhost:8000.
Verifique se o backend está rodando e acessível.
```

## 🔍 Causa

O frontend no Vercel está tentando se conectar a `http://localhost:8000`, que **não existe em produção**. 

**Causa:** A variável de ambiente `VITE_API_URL` não está configurada no Vercel, então o código usa o valor padrão (`http://localhost:8000`).

## ✅ Solução

### Passo 1: Obter URL do Backend em Produção

Você precisa da URL do seu backend em produção (Railway ou outro serviço).

**Exemplo:**
- `https://seu-backend.railway.app`
- `https://cosmoastrologia-backend.railway.app`

### Passo 2: Configurar Variável no Vercel

1. Acesse: https://vercel.com
2. Selecione seu projeto
3. Vá em **Settings** → **Environment Variables**
4. Clique em **Add New**
5. Configure:
   - **Key:** `VITE_API_URL`
   - **Value:** `https://sua-url-backend.railway.app` (URL do seu backend em produção)
   - **Environment:** Selecione todos (Production, Preview, Development)
6. Clique em **Save**

### Passo 3: Redeploy

**IMPORTANTE:** Após adicionar variável de ambiente, você **DEVE** fazer redeploy:

1. Vá em **Deployments**
2. Clique nos **3 pontos** do último deploy
3. Selecione **Redeploy**
4. Aguarde o build completar

**⚠️ CRÍTICO:** Variáveis de ambiente só são aplicadas em **novos deploys**. Deploys antigos não têm acesso às novas variáveis.

## 🔍 Verificação

### Verificar se Variável Está Configurada

1. No Vercel: **Settings** → **Environment Variables**
2. Procure por `VITE_API_URL`
3. Verifique se o valor está correto (URL do backend em produção)

### Verificar se Está Sendo Usada

1. Após redeploy, acesse seu app no Vercel
2. Abra o console do navegador (F12)
3. Vá em **Network**
4. Faça uma requisição (ex: login)
5. Verifique a URL da requisição - deve ser a URL do backend em produção, não `localhost:8000`

## 🎯 Configuração Completa

### Variáveis Necessárias no Vercel

```
VITE_API_URL = https://seu-backend.railway.app
VITE_GOOGLE_CLIENT_ID = seu-client-id.apps.googleusercontent.com
```

### Variáveis Necessárias no Railway (Backend)

```
DATABASE_URL = postgresql://... (gerado automaticamente pelo Railway)
SECRET_KEY = seu-secret-key-gerado
CORS_ORIGINS = https://seu-app.vercel.app
GOOGLE_CLIENT_ID = seu-client-id
GOOGLE_CLIENT_SECRET = seu-client-secret
GROQ_API_KEY = sua-groq-api-key
```

## ⚠️ Problemas Comuns

### Erro persiste após configurar

**Solução:**
1. Verificar se fez **Redeploy** após adicionar variável
2. Verificar se a URL do backend está correta
3. Verificar se o backend está rodando e acessível
4. Testar a URL do backend diretamente no navegador

### Backend não responde

**Solução:**
1. Verificar se o backend está rodando no Railway
2. Verificar logs do Railway
3. Testar URL do backend: `https://seu-backend.railway.app/`
4. Deve retornar: `{"message":"Astrologia API"}`

### CORS Error

**Solução:**
1. No Railway, verificar variável `CORS_ORIGINS`
2. Deve incluir a URL do Vercel: `https://seu-app.vercel.app`
3. Fazer redeploy do backend após atualizar

## 📝 Checklist

- [ ] URL do backend em produção obtida
- [ ] `VITE_API_URL` configurada no Vercel
- [ ] Valor é URL de produção (não localhost)
- [ ] Redeploy feito após adicionar variável
- [ ] Backend está rodando e acessível
- [ ] `CORS_ORIGINS` no Railway inclui URL do Vercel
- [ ] Testado em produção

## 🎯 Resumo Rápido

```bash
1. Vercel → Settings → Environment Variables
2. Adicionar: VITE_API_URL = https://seu-backend.railway.app
3. Redeploy (IMPORTANTE!)
4. Testar
```

## 🔗 Links Úteis

- **Vercel Dashboard:** https://vercel.com
- **Railway Dashboard:** https://railway.app
- **Documentação Vercel Env Vars:** https://vercel.com/docs/concepts/projects/environment-variables

