# Microsserviço RAG - Documentação

## ✅ O que foi feito

### 1. Microsserviço RAG criado
- ✅ Estrutura completa em `rag-service/`
- ✅ API FastAPI dedicada
- ✅ Endpoints: `/api/rag/interpretation`, `/api/rag/search`, `/api/rag/status`
- ✅ Dockerfile otimizado para ML

### 2. Backend simplificado
- ✅ Removidos arquivos RAG do backend:
  - `rag_service_wrapper.py`
  - `rag_service_llamaindex.py` (removido - substituído por FastEmbed)
  - `local_knowledge_base.py`
- ✅ Criado cliente HTTP (`rag_client.py`)
- ✅ Dependências RAG removidas do backend
- ✅ Backend agora usa `httpx` para comunicação com RAG service

### 3. Configuração
- ✅ `docker-compose.yml` criado
- ✅ Variável `RAG_SERVICE_URL` adicionada ao backend
- ✅ Requirements atualizados

## 🚀 Como usar

### Desenvolvimento Local

1. **Iniciar serviços:**
```bash
docker-compose up --build
```

2. **Backend estará em:** `http://localhost:8000`
3. **RAG Service estará em:** `http://localhost:8001`

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
GROQ_API_KEY=sua-chave-groq
DATABASE_URL=sqlite:///./astrologia.db
SECRET_KEY=seu-secret-key
RAG_SERVICE_URL=http://rag-service:8001
```

## 📝 Notas Importantes

### Substituições Pendentes

Algumas funções no `backend/app/api/interpretation.py` ainda têm referências diretas a `rag_service.groq_client`. Essas precisam ser ajustadas para usar o RAG client HTTP.

**Funções que ainda precisam de ajuste:**
- Funções que usam `rag_service.groq_client.chat.completions.create()` diretamente
- Essas devem usar `await rag_client.get_interpretation()` ao invés

### Testes

Para testar a integração:

```bash
# Verificar status do RAG service
curl http://localhost:8001/api/rag/status

# Testar interpretação
curl -X POST http://localhost:8000/api/interpretation \
  -H "Content-Type: application/json" \
  -d '{"planet": "Sol", "sign": "Libra"}'
```

## 🔧 Próximos Passos

1. Ajustar funções que ainda usam Groq diretamente
2. Testar todas as funcionalidades
3. Atualizar documentação de deploy
4. Configurar para produção (Railway, etc)

