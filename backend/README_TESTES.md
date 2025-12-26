# 🧪 Testes de Serviços - Backend

Script para testar os serviços (Backend + RAG Service) e sua integração.

## 📍 Localização

Este script está localizado em `backend/test_services.py` e deve ser executado a partir do diretório `backend/`.

## 🚀 Como usar

```bash
# Navegar para o diretório backend
cd backend

# Executar testes
python3 test_services.py

# Ou com permissão de execução
./test_services.py
```

## 📋 O que é testado

### RAG Service (`http://localhost:8001`)
- ✅ Health check (`/health`)
- ✅ Status (`/api/rag/status`)
- ✅ Busca (`/api/rag/search`)
- ✅ Interpretação (`/api/rag/interpretation`)

### Backend (`http://localhost:8000`)
- ✅ Root endpoint (`/`)
- ✅ Status do RAG (`/api/interpretation/status`)
- ✅ Busca (`/api/interpretation/search`)
- ✅ Interpretação (`/api/interpretation`)

### Integração
- ✅ Fluxo completo: Backend → RAG Service → Resposta
- ✅ Comunicação HTTP entre serviços
- ✅ Tratamento de erros

### Testes Pytest (Opcional)
- ✅ Testes de integração em `tests/integration/`

## 🔍 Exemplo de Saída

```
============================================================
        Teste de Serviços - CosmoAstrologia
============================================================

============================================================
            Testando RAG Service
============================================================

ℹ️  Verificando health check...
✅ RAG Service está respondendo (status: 200)
...
```

## 🐛 Troubleshooting

### RAG Service não está respondendo
```bash
# Verificar se está rodando
docker-compose ps rag-service

# Iniciar se necessário
docker-compose up rag-service
```

### Backend não está respondendo
```bash
# Iniciar backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### pytest não encontrado
O script tentará instalar automaticamente. Se falhar:
```bash
pip install pytest pytest-asyncio httpx requests
```

## 📚 Links Relacionados

- [Testes de Integração Pytest](./tests/integration/README.md)
- [Script de Início de Serviços](../README_START_SERVICES.md)

