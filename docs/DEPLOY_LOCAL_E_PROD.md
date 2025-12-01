# 🚀 Guia de Deploy: Local e Produção

## ✅ Melhorias Implementadas

### 1. Dockerfile Otimizado para Produção

#### Dependências de Compilação
- ✅ Adicionado `swig` para compilar `pyswisseph` (requerido pelo `kerykeion`)
- ✅ Adicionado `libc6-dev` para compilação de extensões C
- ✅ Mantidas dependências essenciais: `build-essential`, `gcc`, `g++`

#### Runtime Otimizado
- ✅ Multi-stage build para reduzir tamanho da imagem
- ✅ Apenas dependências runtime no stage final
- ✅ Variável `PORT` configurada (padrão: 8000)

#### CMD Robusto
```dockerfile
CMD sh -c 'uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --loop asyncio'
```
- ✅ Funciona mesmo se `PORT` não estiver definido
- ✅ Compatível com Railway, Render, Heroku, etc.

### 2. Requirements Corrigidos

#### requirements-prod.txt
- ✅ `httpx>=0.27.0` adicionado (necessário para alguns serviços)
- ✅ Todas as dependências RAG consolidadas
- ✅ Versões fixas para estabilidade

#### requirements.txt
- ✅ Removida duplicação de `httpx`
- ✅ Mantidas dependências de teste separadas

### 3. Configuração de Ambiente

#### Variáveis Necessárias

**Desenvolvimento Local:**
```bash
DATABASE_URL=sqlite:///./astrologia.db
SECRET_KEY=sua-chave-secreta-local
GROQ_API_KEY=opcional-para-testes
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

**Produção (Railway/Render/etc):**
```bash
DATABASE_URL=postgresql://...  # Fornecido pela plataforma
SECRET_KEY=chave-secreta-forte-gerada
GROQ_API_KEY=sua-chave-groq
GOOGLE_CLIENT_ID=seu-client-id
GOOGLE_CLIENT_SECRET=seu-client-secret
DOCS_PATH=docs
INDEX_PATH=rag_index_fastembed
BGE_MODEL_NAME=BAAI/bge-small-en-v1.5
CORS_ORIGINS=https://seu-frontend.vercel.app
PORT=8000  # Geralmente definido automaticamente pela plataforma
```

## 🏃 Execução Local

### Opção 1: Scripts Automáticos (Recomendado)

**Linux/Mac:**
```bash
# Backend apenas
./scripts/start-backend.sh

# Frontend + Backend
./start-all.sh
```

**Windows:**
```powershell
# Backend apenas
.\scripts\start-backend.ps1

# Frontend + Backend
.\start-all.ps1
```

### Opção 2: Manual

```bash
cd backend

# Criar ambiente virtual (primeira vez)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Iniciar servidor
python run.py
```

### Opção 3: Docker Compose

```bash
# Na raiz do projeto
docker-compose up --build
```

## 🚢 Deploy em Produção

### Railway

1. **Conectar Repositório**
   - Vá para Railway Dashboard
   - New Project → Deploy from GitHub
   - Selecione o repositório

2. **Configurar Root Directory**
   - Settings → Root Directory: `backend`

3. **Configurar Variáveis de Ambiente**
   - Variables → Adicione todas as variáveis necessárias
   - `PORT` é definido automaticamente pelo Railway

4. **Deploy Automático**
   - Railway detecta `Dockerfile` automaticamente
   - Build inicia automaticamente após push

### Render

1. **Criar Web Service**
   - New → Web Service
   - Conecte o repositório
   - Root Directory: `backend`

2. **Configurações**
   - Build Command: (deixar vazio, usa Dockerfile)
   - Start Command: (deixar vazio, usa CMD do Dockerfile)

3. **Variáveis de Ambiente**
   - Adicione todas as variáveis necessárias

### Outras Plataformas

O Dockerfile é compatível com qualquer plataforma que suporte Docker:
- ✅ Heroku (com `heroku.yml`)
- ✅ Google Cloud Run
- ✅ AWS ECS/Fargate
- ✅ DigitalOcean App Platform
- ✅ Fly.io

## 🔍 Verificação de Build

### Testar Build Localmente

```bash
cd backend

# Build da imagem
docker build -t astrologia-backend .

# Testar execução
docker run -p 8000:8000 \
  -e DATABASE_URL=sqlite:///./astrologia.db \
  -e SECRET_KEY=test-key \
  astrologia-backend
```

### Verificar Logs

```bash
# Docker Compose
docker-compose logs -f backend

# Docker direto
docker logs <container-id>
```

## ⚠️ Problemas Comuns

### 1. Erro de Compilação do kerykeion

**Sintoma:** `error: command 'gcc' failed` ou `swig: command not found`

**Solução:** O Dockerfile já inclui todas as dependências necessárias. Se ainda ocorrer:
- Verifique se está usando a imagem `python:3.11-slim` (não `alpine`)
- Certifique-se de que `swig` está instalado no stage de build

### 2. PORT não definido

**Sintoma:** `ValueError: invalid literal for int() with base 10: ''`

**Solução:** O CMD já usa `${PORT:-8000}`, mas se ainda ocorrer:
- Defina `PORT=8000` nas variáveis de ambiente
- Ou use `CMD uvicorn app.main:app --host 0.0.0.0 --port 8000 --loop asyncio`

### 3. Dependências faltando

**Sintoma:** `ModuleNotFoundError: No module named 'X'`

**Solução:**
- Verifique se `requirements-prod.txt` inclui todas as dependências
- Rebuild a imagem: `docker build --no-cache -t astrologia-backend .`

### 4. RAG Index não encontrado

**Sintoma:** `FileNotFoundError: rag_index_fastembed`

**Solução:**
- Certifique-se de que o diretório `rag_index_fastembed` existe
- Adicione volume no `docker-compose.yml` ou copie no Dockerfile

## 📋 Checklist de Deploy

### Antes do Deploy

- [ ] Todas as variáveis de ambiente configuradas
- [ ] `SECRET_KEY` forte gerada
- [ ] `GROQ_API_KEY` configurada (se usar IA)
- [ ] `CORS_ORIGINS` inclui domínio do frontend
- [ ] Banco de dados configurado (PostgreSQL em produção)
- [ ] RAG index gerado (se necessário)

### Após o Deploy

- [ ] Verificar logs de inicialização
- [ ] Testar endpoint `/` (deve retornar `{"message": "Astrologia API"}`)
- [ ] Testar endpoint `/docs` (documentação Swagger)
- [ ] Verificar se RAG service inicializou corretamente
- [ ] Testar autenticação
- [ ] Testar cálculo de mapa astral

## 🎯 Performance

### Otimizações Implementadas

1. **Multi-stage Build**
   - Reduz tamanho da imagem final
   - Remove dependências de compilação do runtime

2. **Batch Installation**
   - Instala dependências em batches para evitar timeout
   - Timeout maior (600s) para dependências ML

3. **Cache de Layers**
   - Dependências instaladas em ordem de menor para maior mudança
   - Aplicação copiada por último

### Tamanho Esperado da Imagem

- **Builder stage:** ~2-3GB (temporário, descartado)
- **Final image:** ~500-800MB (apenas runtime)

## 📚 Referências

- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Railway Documentation](https://docs.railway.app/)
- [Kerykeion Documentation](https://github.com/giorgiobrizi/kerykeion)

