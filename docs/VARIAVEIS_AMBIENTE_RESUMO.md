# 📋 Resumo: Variáveis de Ambiente - Local vs Produção

Este documento resume como configurar as variáveis de ambiente para desenvolvimento local e produção.

---

## 🏠 Desenvolvimento Local

### Backend

1. **Criar arquivo `.env`:**
   ```bash
   cd backend
   cp .env.example .env
   ```

2. **Configurar variáveis mínimas:**
   ```env
   SECRET_KEY=sua-chave-secreta-gerada
   GROQ_API_KEY=sua-chave-groq
   ```

3. **Banco de dados:**
   - Usa SQLite por padrão (`sqlite:///./astrologia.db`)
   - Não precisa configurar `DATABASE_URL`

4. **CORS:**
   - Valores padrão já incluem `localhost`
   - Não precisa configurar para desenvolvimento

### Frontend

1. **Criar arquivo `.env.local`:**
   ```bash
   cp .env.local.example .env.local
   ```

2. **Configurar URL do backend:**
   ```env
   VITE_API_URL=http://localhost:8000
   ```

**Documentação completa:** [CONFIGURACAO_LOCAL.md](./CONFIGURACAO_LOCAL.md)

---

## 🚀 Produção

### Backend (Railway)

Configure as variáveis diretamente no painel do Railway:

**Obrigatórias:**
- `SECRET_KEY` - Chave secreta para JWT
- `GROQ_API_KEY` - Chave da API Groq

**Recomendadas:**
- `DATABASE_URL` - Definida automaticamente se usar PostgreSQL
- `CORS_ORIGINS` - URLs do frontend separadas por vírgula

**Documentação completa:** [RAILWAY_VARIAVEIS_AMBIENTE.md](./RAILWAY_VARIAVEIS_AMBIENTE.md)

### Frontend (Vercel)

Configure a variável diretamente no painel do Vercel:

- `VITE_API_URL` - URL do backend (ex: `https://seu-backend.railway.app`)

**Documentação completa:** [VERCEL_FIX_API_URL.md](./VERCEL_FIX_API_URL.md)

---

## 📊 Comparação Rápida

| Variável | Local | Produção |
|----------|-------|----------|
| **Backend** | | |
| `SECRET_KEY` | Arquivo `.env` | Railway Variables |
| `GROQ_API_KEY` | Arquivo `.env` | Railway Variables |
| `DATABASE_URL` | SQLite (padrão) | PostgreSQL (Railway) |
| `CORS_ORIGINS` | localhost (padrão) | Railway Variables |
| **Frontend** | | |
| `VITE_API_URL` | `.env.local` | Vercel Variables |

---

## ✅ Checklist Rápido

### Para rodar localmente:

- [ ] `backend/.env` criado (copie de `.env.example`)
- [ ] `SECRET_KEY` configurada no `.env`
- [ ] `GROQ_API_KEY` configurada no `.env` (se usar IA)
- [ ] `.env.local` criado na raiz (copie de `.env.local.example`)
- [ ] `VITE_API_URL=http://localhost:8000` no `.env.local`

### Para produção:

- [ ] Variáveis configuradas no Railway (backend)
- [ ] Variável `VITE_API_URL` configurada no Vercel (frontend)
- [ ] `CORS_ORIGINS` inclui URL do frontend
- [ ] `SECRET_KEY` diferente da de desenvolvimento

---

## 🔒 Segurança

⚠️ **IMPORTANTE:**

1. **Nunca commite arquivos `.env` ou `.env.local`**
   - Já estão no `.gitignore`
   - Use `.env.example` como template

2. **Use valores diferentes para local e produção**
   - Especialmente `SECRET_KEY`
   - Gere uma chave única para cada ambiente

3. **Não compartilhe credenciais**
   - Use variáveis de ambiente, não código
   - Use serviços de gerenciamento de secrets em produção

---

## 📚 Documentação Completa

- [Configuração Local](./CONFIGURACAO_LOCAL.md) - Guia completo para desenvolvimento local
- [Variáveis Railway](./RAILWAY_VARIAVEIS_AMBIENTE.md) - Configuração do backend em produção
- [Conectar Frontend/Backend](./CONECTAR_FRONTEND_BACKEND.md) - Integração entre serviços
- [Fix API URL Vercel](./VERCEL_FIX_API_URL.md) - Configuração do frontend em produção

