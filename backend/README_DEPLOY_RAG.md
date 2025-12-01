# 🚀 Deploy com RAG - Guia Rápido

## 🎯 Objetivo

Garantir que o RAG funcione no deploy, mesmo com timeout no Railway.

---

## ✅ Solução Recomendada: Dockerfile.ml-priority

### Passo 1: Configurar no Railway

1. No Railway Dashboard:
   - Vá para seu projeto → Backend service
   - **Settings** → **Dockerfile Path**
   - Digite: `backend/Dockerfile.ml-priority`
   - Salve

2. Faça deploy

### Por que funciona:
- ✅ Instala ML dependencies **PRIMEIRO** (quando ainda há tempo)
- ✅ Dependências leves instalam depois (rápido)
- ✅ Maior chance de sucesso

---

## ✅ Solução Alternativa: Build Local + Docker Hub (100% Garantido)

Se `ml-priority` ainda der timeout, use esta solução:

### Passo 1: Build Local

```bash
cd backend
docker build -t seu-usuario/cosmoastrologia:latest -f Dockerfile.build-local .
```

**Ou use o script:**
```bash
./scripts/build-and-push.sh seu-usuario/cosmoastrologia latest
```

### Passo 2: Push para Docker Hub

```bash
# Login (primeira vez)
docker login

# Push
docker push seu-usuario/cosmoastrologia:latest
```

### Passo 3: Configurar Railway

1. No Railway:
   - **Settings** → **Deploy**
   - Mude para **"Deploy from Docker Hub"**
   - Configure:
     - **Image:** `seu-usuario/cosmoastrologia:latest`
     - **Registry:** Docker Hub

2. Railway vai baixar a imagem (não fazer build)

### Vantagens:
- ✅ **100% garantido** - não depende de timeout
- ✅ Você controla o build
- ✅ Pode testar localmente antes

---

## ✅ Verificar se RAG Funcionou

Após deploy:

```bash
# Verificar status
curl https://seu-backend.railway.app/api/interpretation/status

# Deve retornar:
# {
#   "available": true,
#   "has_dependencies": true,
#   ...
# }
```

---

## 📚 Documentação Completa

Veja `backend/docs/SOLUCOES_RAG_COMPLETO.md` para todas as soluções e detalhes.

---

**Última atualização:** $(date)

