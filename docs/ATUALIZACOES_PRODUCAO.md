# 🚀 Atualizações Necessárias para Produção

Este documento lista todas as atualizações que precisam ser feitas antes de fazer deploy em produção.

## 📋 Resumo Executivo

### ⚠️ Problemas Críticos Encontrados

1. **URL de debug hardcoded** no `landing-page.tsx`
2. **API_BASE_URL** com fallback para localhost que não funciona bem em produção
3. **Variáveis de ambiente** precisam ser configuradas no Vercel/Railway
4. **CORS** precisa incluir URL de produção

---

## 🔧 Correções de Código Necessárias

### 1. ❌ Remover URL de Debug do `landing-page.tsx`

**Arquivo:** `src/components/landing-page.tsx`

**Problema:** Há uma chamada fetch para um servidor de debug local que não existe em produção.

**Linha 19:**

```typescript
fetch('http://127.0.0.1:7242/ingest/38ee2237-7946-45f5-b6b7-94ee2eaa0c05', ...)
```

**Ação:** Remover ou comentar este código de debug.

---

### 2. ⚠️ Melhorar Fallback do `API_BASE_URL`

**Arquivo:** `src/services/api.ts`

**Problema Atual:**

```typescript
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (typeof window !== "undefined"
    ? window.location.origin.replace(/:\d+$/, ":8000")
    : "http://localhost:8000");
```

**Problema:** O fallback tenta usar `window.location.origin` com porta 8000, mas em produção o frontend e backend estão em domínios diferentes.

**Solução Recomendada:**

```typescript
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  (process.env.NODE_ENV === "production"
    ? "https://seu-backend.railway.app" // URL de produção
    : "http://localhost:8000"); // Desenvolvimento local
```

**OU melhor ainda:** Forçar erro se não estiver configurado em produção:

```typescript
const getApiBaseUrl = () => {
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }

  if (process.env.NODE_ENV === "production") {
    console.error("NEXT_PUBLIC_API_URL não está configurado em produção!");
    throw new Error("API URL não configurada");
  }

  return "http://localhost:8000";
};

const API_BASE_URL = getApiBaseUrl();
```

---

## 🌐 Variáveis de Ambiente - Configuração

### Frontend (Vercel)

#### ✅ Obrigatórias

1. **`NEXT_PUBLIC_API_URL`**

   - **Descrição:** URL do backend em produção
   - **Formato:** `https://seu-backend.railway.app`
   - **Exemplo:** `https://cosmoastral-backend.railway.app`
   - **⚠️ CRÍTICO:** Sem esta variável, o frontend não conseguirá se comunicar com o backend

2. **`NEXT_PUBLIC_GOOGLE_CLIENT_ID`** (se usar OAuth)
   - **Descrição:** Client ID do Google OAuth
   - **Formato:** `xxxxx-xxxxx.apps.googleusercontent.com`
   - **Onde obter:** https://console.cloud.google.com/
   - **⚠️ IMPORTANTE:** Deve ser o mesmo Client ID configurado no backend

#### 📝 Como Configurar no Vercel:

1. Acesse: https://vercel.com/dashboard
2. Selecione seu projeto
3. Vá em **Settings** → **Environment Variables**
4. Adicione cada variável:
   - **Key:** `NEXT_PUBLIC_API_URL`
   - **Value:** `https://seu-backend.railway.app`
   - **Environment:** Production (e Preview se necessário)

---

### Backend (Railway)

#### ✅ Obrigatórias

1. **`SECRET_KEY`**

   - **Descrição:** Chave secreta para assinar tokens JWT
   - **Gerar:** `python -c "import secrets; print(secrets.token_urlsafe(32))"`
   - **⚠️ CRÍTICO:** NUNCA use o valor padrão em produção
   - **⚠️ CRÍTICO:** Deve ser único e secreto

2. **`GROQ_API_KEY`**

   - **Descrição:** Chave da API Groq para interpretações astrológicas
   - **Onde obter:** https://console.groq.com/
   - **Formato:** `gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - **⚠️ IMPORTANTE:** Sem esta chave, as interpretações não funcionarão

3. **`CORS_ORIGINS`**
   - **Descrição:** URLs permitidas para fazer requisições ao backend
   - **Formato:** URLs separadas por vírgula (sem espaços)
   - **Exemplo:** `https://seu-app.vercel.app,https://www.seu-dominio.com`
   - **⚠️ CRÍTICO:** Deve incluir a URL exata do frontend em produção
   - **⚠️ IMPORTANTE:** Não inclua barra final (`/`) nas URLs

#### 🔧 Recomendadas

4. **`DATABASE_URL`**

   - **Descrição:** URL de conexão com PostgreSQL
   - **Railway:** Definida automaticamente ao adicionar serviço PostgreSQL
   - **Formato:** `postgresql://user:password@host:port/database`
   - **⚠️ RECOMENDADO:** Use PostgreSQL em produção (não SQLite)

5. **`BREVO_API_KEY`**

   - **Descrição:** API Key do Brevo para envio de emails
   - **Onde obter:** https://app.brevo.com/settings/keys/api
   - **Formato:** `xkeysib-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - **⚠️ IMPORTANTE:** Sem esta chave, emails não serão enviados

6. **`EMAIL_FROM`**
   - **Descrição:** Email remetente
   - **Padrão:** `noreply@cosmoastral.com.br`
   - **⚠️ IMPORTANTE:** Deve ser verificado no Brevo

#### 🔐 Opcionais (OAuth Google)

7. **`GOOGLE_CLIENT_ID`**

   - **Descrição:** Client ID do Google OAuth (mesmo do frontend)
   - **Formato:** `xxxxx-xxxxx.apps.googleusercontent.com`

8. **`GOOGLE_CLIENT_SECRET`**
   - **Descrição:** Client Secret do Google OAuth
   - **Onde obter:** https://console.cloud.google.com/
   - **⚠️ SECRETO:** Nunca exponha esta chave

#### 📝 Como Configurar no Railway:

1. Acesse: https://railway.app/dashboard
2. Selecione seu projeto
3. Vá em **Variables**
4. Adicione cada variável clicando em **+ New Variable**

---

## 🔒 Configurações de Segurança

### 1. Verificar `.gitignore`

Certifique-se de que os seguintes arquivos estão no `.gitignore`:

```
.env
.env.local
.env*.local
backend/.env
backend/.env.local
*.db
*.db-shm
*.db-wal
```

### 2. Gerar SECRET_KEY Seguro

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copie o resultado e configure no Railway como `SECRET_KEY`.

### 3. Configurar CORS Corretamente

**Backend (Railway):**

```
CORS_ORIGINS=https://seu-app.vercel.app,https://www.seu-dominio.com
```

**⚠️ IMPORTANTE:**

- Use `https://` (não `http://`) em produção
- Não inclua barra final (`/`)
- Separe múltiplas URLs por vírgula (sem espaços)
- Inclua todas as variantes do domínio (com e sem www)

---

## 🧪 Testes Antes do Deploy

### Frontend

- [ ] `npm run build` executa sem erros
- [ ] Não há erros de TypeScript (`npm run type-check`)
- [ ] Testes passam (`npm test`)
- [ ] Verificar que `NEXT_PUBLIC_API_URL` está sendo usado corretamente

### Backend

- [ ] Backend inicia sem erros
- [ ] Testes passam (`pytest`)
- [ ] CORS está configurado corretamente
- [ ] `SECRET_KEY` não é o valor padrão

### Integração

- [ ] Frontend consegue fazer requisições ao backend
- [ ] Autenticação funciona
- [ ] Google OAuth funciona (se configurado)
- [ ] Emails são enviados (se configurado)

---

## 📦 Checklist de Deploy

### Antes do Deploy

- [ ] Código commitado e pushado para `main`
- [ ] Todas as variáveis de ambiente configuradas no Vercel
- [ ] Todas as variáveis de ambiente configuradas no Railway
- [ ] `SECRET_KEY` gerado e configurado (não é o padrão)
- [ ] `CORS_ORIGINS` inclui URL de produção do frontend
- [ ] `NEXT_PUBLIC_API_URL` aponta para URL de produção do backend
- [ ] Código de debug removido
- [ ] Build do frontend funciona localmente
- [ ] Backend inicia sem erros

### Durante o Deploy

- [ ] Vercel conectado ao repositório GitHub
- [ ] Railway conectado ao repositório GitHub
- [ ] Deploy automático configurado
- [ ] Primeiro deploy bem-sucedido

### Após o Deploy

- [ ] Frontend acessível e funcionando
- [ ] Backend respondendo em `/`
- [ ] Backend API Docs acessível em `/docs`
- [ ] Autenticação funcionando
- [ ] CORS configurado corretamente (sem erros no console)
- [ ] Logs sem erros críticos
- [ ] Teste de registro de usuário
- [ ] Teste de login
- [ ] Teste de Google OAuth (se configurado)
- [ ] Teste de criação de mapa astral

---

## 🔍 Verificações Pós-Deploy

### Frontend (Vercel)

1. Acesse a URL do frontend
2. Abra o Console do navegador (F12)
3. Verifique se não há erros relacionados a:
   - CORS
   - API URL não encontrada
   - Variáveis de ambiente não definidas

### Backend (Railway)

1. Acesse `https://seu-backend.railway.app/docs`
2. Verifique se a documentação da API está acessível
3. Teste um endpoint simples (ex: `GET /`)
4. Verifique os logs no Railway para erros

### Integração

1. Tente fazer login no frontend
2. Verifique se as requisições chegam ao backend
3. Verifique se as respostas retornam corretamente
4. Teste criação de conta e onboarding

---

## 📚 Documentação Adicional

- [DEPLOY_CHECKLIST.md](./DEPLOY_CHECKLIST.md) - Checklist completo
- [VERIFICACAO_PRODUCAO.md](./VERIFICACAO_PRODUCAO.md) - Verificação detalhada
- [RAILWAY_VARIAVEIS_AMBIENTE.md](./RAILWAY_VARIAVEIS_AMBIENTE.md) - Variáveis do Railway
- [GOOGLE_OAUTH_VERCEL.md](./GOOGLE_OAUTH_VERCEL.md) - Configuração OAuth

---

## 🚨 Problemas Comuns

### Frontend não consegue conectar ao backend

- **Causa:** `NEXT_PUBLIC_API_URL` não configurado ou incorreto
- **Solução:** Verificar variável no Vercel e reiniciar deploy

### Erro de CORS

- **Causa:** `CORS_ORIGINS` não inclui URL do frontend
- **Solução:** Adicionar URL exata do frontend no `CORS_ORIGINS` do Railway

### Google OAuth não funciona

- **Causa:** `NEXT_PUBLIC_GOOGLE_CLIENT_ID` não configurado ou diferente do backend
- **Solução:** Verificar que ambos (frontend e backend) usam o mesmo Client ID

### Emails não são enviados

- **Causa:** `BREVO_API_KEY` não configurado ou inválido
- **Solução:** Verificar chave no Brevo e configurar no Railway

---

**Última atualização:** 2024  
**Status:** ✅ Documento completo e atualizado
