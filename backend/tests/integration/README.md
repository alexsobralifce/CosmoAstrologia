# Testes de Integração - RAG Service

## Como executar os testes

### Pré-requisitos

1. **Iniciar o RAG service:**
```bash
# Opção 1: Docker Compose (recomendado)
docker-compose up rag-service

# Opção 2: Manualmente
cd rag-service
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

2. **Configurar variável de ambiente:**
```bash
export RAG_SERVICE_URL=http://localhost:8001
```

### Executar testes

```bash
# Todos os testes de integração
pytest backend/tests/integration/ -v

# Teste específico
pytest backend/tests/integration/test_rag_service_integration.py::test_rag_service_health -v

# Testes marcados como integration
pytest -m integration -v

# Com cobertura
pytest backend/tests/integration/ --cov=app --cov-report=html
```

## Testes disponíveis

1. **test_rag_service_health** - Verifica se RAG service está respondendo
2. **test_rag_service_status** - Testa endpoint de status
3. **test_rag_service_search** - Testa busca de documentos
4. **test_rag_service_interpretation** - Testa interpretação
5. **test_backend_rag_status_endpoint** - Testa endpoint do backend que usa RAG
6. **test_backend_interpretation_endpoint_with_rag** - Testa interpretação via backend
7. **test_backend_search_endpoint_with_rag** - Testa busca via backend
8. **test_rag_client_integration** - Testa cliente RAG diretamente
9. **test_full_integration_flow** - Teste completo de integração

## Notas

- Os testes pulam automaticamente se o RAG service não estiver rodando
- Use `pytest.skip()` para pular testes quando necessário
- Testes marcados com `@pytest.mark.integration` requerem serviços externos

