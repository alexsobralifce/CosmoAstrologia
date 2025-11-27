# ✅ Checklist de Deploy no Railway

## 🎯 Situação Atual

✅ **Root Directory configurado como `backend`** - Correto!

Agora vamos garantir que tudo está configurado para o deploy funcionar.

---

## 📋 Checklist Completo

### 1. ✅ Root Directory
- [x] Configurado como `backend` no Settings
- ✅ **Status:** Configurado corretamente!

### 2. 📦 Arquivos Necessários no Repositório

Verifique se estes arquivos estão commitados no repositório:

- [ ] `backend/Dockerfile` existe
- [ ] `backend/.dockerignore` existe
- [ ] `backend/requirements.txt` existe
- [ ] `backend/railway.json` existe
- [ ] `backend/app/` (pasta com o código)
- [ ] `backend/docs/` (pasta com PDFs do RAG - 617MB)
- [ ] `backend/rag_index.pkl` (índice do RAG - 21MB)

### 3. 🔐 Variáveis de Ambiente

Vá para a aba **"Variables"** no Railway e verifique:

**Obrigatórias:**
- [ ] `SECRET_KEY` - Chave secreta para JWT
- [ ] `GROQ_API_KEY` - Chave da API Groq

**Recomendadas:**
- [ ] `CORS_ORIGINS` - URLs do frontend (separadas por vírgula)
- [ ] `DATABASE_URL` - Se usar PostgreSQL, será automático

### 4. 🗄️ PostgreSQL (Opcional mas Recomendado)

- [ ] Serviço PostgreSQL criado no Railway
- [ ] PostgreSQL conectado ao serviço Backend
- [ ] `DATABASE_URL` aparece automaticamente nas Variables

### 5. 🚀 Deploy

- [ ] Commit e push dos arquivos para o GitHub
- [ ] Railway detecta o novo commit
- [ ] Build inicia automaticamente
- [ ] Build completa com sucesso

---

## 🔍 Como Verificar se Está Funcionando

### 1. Verificar Build

Vá para a aba **"Deployments"** e clique no deploy mais recente:

**Deve ver:**
```
Building Docker image...
Step 1/8 : FROM python:3.11-slim
...
Successfully built [image-id]
```

**NÃO deve ver:**
```
Dockerfile `Dockerfile` does not exist
```

### 2. Verificar Logs do Backend

Após o build, verifique os logs:

**Deve ver:**
```
INFO:     Started server process
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
[RAG] Índice carregado: X documentos
```

**NÃO deve ver:**
- Erros de conexão ao banco
- Erros de módulos não encontrados
- Erros do Caddy (proxy reverso)

### 3. Testar Endpoint

Após o deploy, teste o endpoint:

```bash
curl https://seu-backend.railway.app/
```

**Deve retornar:**
```json
{"message": "Astrologia API"}
```

---

## 🆘 Problemas Comuns e Soluções

### Problema: Build falha com "Dockerfile not found"

**Solução:**
- ✅ Já resolvido! Root Directory está configurado como `backend`
- Verifique se o arquivo `backend/Dockerfile` está no repositório
- Faça commit e push se necessário

### Problema: Build falha ao instalar dependências

**Solução:**
- Verifique se `backend/requirements.txt` existe
- Verifique se `psycopg2-binary` está na lista (necessário para PostgreSQL)
- Veja os logs do build para ver qual dependência está falhando

### Problema: Backend não inicia

**Solução:**
- Verifique as variáveis de ambiente (`SECRET_KEY`, `GROQ_API_KEY`)
- Veja os logs para identificar o erro específico
- Verifique se `DATABASE_URL` está configurada (se usar PostgreSQL)

### Problema: Erro de conexão ao banco

**Solução:**
- Se usar PostgreSQL: verifique se os serviços estão conectados
- A `DATABASE_URL` deve aparecer automaticamente nas Variables
- Se não aparecer, conecte o PostgreSQL ao Backend manualmente

---

## 📝 Próximos Passos Após Deploy Bem-Sucedido

1. ✅ Teste o endpoint raiz: `https://seu-backend.railway.app/`
2. ✅ Teste a documentação: `https://seu-backend.railway.app/docs`
3. ✅ Configure o domínio customizado (opcional)
4. ✅ Atualize o frontend para apontar para a nova URL do backend

---

## 🎉 Tudo Pronto!

Se todos os itens do checklist estiverem marcados:
- ✅ Backend está configurado
- ✅ Root Directory está correto
- ✅ Arquivos estão no repositório
- ✅ Variáveis de ambiente configuradas
- ✅ Build deve funcionar!

**Agora é só fazer commit e push, e o Railway vai fazer o deploy automaticamente!** 🚀

