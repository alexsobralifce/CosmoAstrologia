# 🚀 Guia de Deploy - CosmoAstrologia

Este guia explica como fazer deploy do sistema para produção mantendo a execução local funcionando.

## 📋 Pré-requisitos

- Conta no GitHub
- Conta no Vercel (para frontend)
- Conta no Railway (para backend) ou outro serviço de hospedagem
- Variáveis de ambiente configuradas

## 🏗️ Arquitetura

- **Frontend**: React + Vite → Deploy no Vercel
- **Backend**: FastAPI + Python → Deploy no Railway
- **Banco de Dados**: PostgreSQL (produção) ou SQLite (local)

## 📦 Estrutura do Projeto

```
CosmoAstrologia/
├── src/                    # Frontend React
├── backend/                # Backend FastAPI
├── .env.example           # Exemplo de variáveis frontend
├── backend/.env.example   # Exemplo de variáveis backend
├── vercel.json            # Configuração Vercel
└── DEPLOY.md             # Este arquivo
```

## 🔧 Configuração Local

### 1. Variáveis de Ambiente Frontend

Crie um arquivo `.env.local` na raiz do projeto:

```bash
cp .env.example .env.local
```

Edite `.env.local`:

```env
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=seu-google-client-id
```

### 2. Variáveis de Ambiente Backend

Crie um arquivo `.env` no diretório `backend/`:

```bash
cd backend
cp .env.example .env
```

Edite `backend/.env`:

```env
DATABASE_URL=sqlite:///./astrologia.db
SECRET_KEY=seu-secret-key-gerado
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
GOOGLE_CLIENT_ID=seu-google-client-id
GOOGLE_CLIENT_SECRET=seu-google-client-secret
GROQ_API_KEY=sua-groq-api-key
```

**Gerar SECRET_KEY seguro:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 🌐 Deploy em Produção

### Frontend (Vercel)

1. **Conectar repositório GitHub ao Vercel:**
   - Acesse [vercel.com](https://vercel.com)
   - Importe o repositório do GitHub
   - Configure o projeto:
     - **Framework Preset**: Vite
     - **Root Directory**: `/` (raiz)
     - **Build Command**: `npm run build`
     - **Output Directory**: `build`

2. **Configurar Variáveis de Ambiente no Vercel:**
   - Vá em Settings → Environment Variables
   - Adicione:
     ```
     VITE_API_URL=https://seu-backend.railway.app
     VITE_GOOGLE_CLIENT_ID=seu-google-client-id
     ```

3. **Deploy:**
   - Push para `main` branch → Deploy automático
   - Ou faça deploy manual no dashboard

### Backend (Railway)

1. **Criar projeto no Railway:**
   - Acesse [railway.app](https://railway.app)
   - New Project → Deploy from GitHub repo
   - Selecione o repositório

2. **Configurar serviço:**
   - Railway detecta automaticamente o `Dockerfile` em `backend/`
   - Ou configure manualmente:
     - **Root Directory**: `backend`
     - **Build Command**: (não necessário com Dockerfile)
     - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Adicionar PostgreSQL:**
   - New → Database → PostgreSQL
   - Railway gera automaticamente `DATABASE_URL`

4. **Configurar Variáveis de Ambiente:**
   - Vá em Variables
   - Adicione todas as variáveis de `backend/.env.example`:
     ```
     SECRET_KEY=seu-secret-key-gerado
     CORS_ORIGINS=https://seu-frontend.vercel.app
     GOOGLE_CLIENT_ID=seu-google-client-id
     GOOGLE_CLIENT_SECRET=seu-google-client-secret
     GROQ_API_KEY=sua-groq-api-key
     ```
   - **NÃO** adicione `DATABASE_URL` manualmente (Railway faz isso automaticamente)

5. **Deploy:**
   - Railway faz deploy automático ao fazer push para `main`
   - Ou faça deploy manual no dashboard

### Atualizar CORS no Backend

Após fazer deploy do frontend, atualize `CORS_ORIGINS` no Railway:

```
CORS_ORIGINS=https://seu-frontend.vercel.app,https://seu-frontend.vercel.app
```

## 🔄 Workflow de Desenvolvimento

### Desenvolvimento Local

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate  # ou venv\Scripts\activate no Windows
python run.py

# Terminal 2 - Frontend
npm run dev
```

### Deploy para Produção

1. **Fazer alterações localmente**
2. **Testar localmente**
3. **Commit e push para GitHub:**
   ```bash
   git add .
   git commit -m "Descrição das mudanças"
   git push origin main
   ```
4. **Vercel e Railway fazem deploy automático**

## ✅ Checklist de Deploy

### Antes do Primeiro Deploy

- [ ] Variáveis de ambiente configuradas no Vercel
- [ ] Variáveis de ambiente configuradas no Railway
- [ ] SECRET_KEY gerado e configurado
- [ ] CORS_ORIGINS atualizado com URL do frontend
- [ ] Google OAuth configurado (frontend e backend)
- [ ] GROQ_API_KEY configurada (opcional, mas recomendado)
- [ ] Banco de dados PostgreSQL criado no Railway
- [ ] Testado localmente

### Após Deploy

- [ ] Frontend acessível e funcionando
- [ ] Backend respondendo em `/`
- [ ] Autenticação funcionando
- [ ] API endpoints funcionando
- [ ] CORS configurado corretamente
- [ ] Logs sem erros críticos

## 🐛 Troubleshooting

### Frontend não conecta ao backend

- Verifique `VITE_API_URL` no Vercel
- Verifique `CORS_ORIGINS` no Railway
- Verifique se o backend está rodando

### Erro de CORS

- Adicione a URL do frontend em `CORS_ORIGINS` no Railway
- Formato: `https://seu-app.vercel.app` (sem trailing slash)

### Backend não inicia

- Verifique logs no Railway
- Verifique se todas as variáveis de ambiente estão configuradas
- Verifique se o `DATABASE_URL` está correto

### Erro de autenticação

- Verifique `SECRET_KEY` configurado
- Verifique Google OAuth configurado corretamente
- Verifique se as URLs de callback estão corretas no Google Console

## 📝 Notas Importantes

1. **Nunca commite arquivos `.env`** - eles estão no `.gitignore`
2. **Use `.env.example`** como referência para outras pessoas
3. **SECRET_KEY deve ser único e seguro** em produção
4. **CORS_ORIGINS** deve incluir todas as URLs do frontend
5. **Banco de dados local** (SQLite) não é commitado - apenas para desenvolvimento

## 🔐 Segurança

- ✅ Variáveis sensíveis não estão no código
- ✅ `.env` está no `.gitignore`
- ✅ SECRET_KEY é gerado aleatoriamente
- ✅ CORS configurado corretamente
- ✅ HTTPS em produção (Vercel e Railway)

## 📚 Recursos

- [Vercel Documentation](https://vercel.com/docs)
- [Railway Documentation](https://docs.railway.app)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Vite Documentation](https://vitejs.dev)

