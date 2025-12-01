# 🧪 Guia de Testes

Este documento descreve como executar os testes do sistema RAG otimizado com FastEmbed.

## 📋 Estrutura de Testes

```
CosmoAstrologia/
├── rag-service/
│   └── tests/
│       ├── test_rag_service.py      # Testes unitários do RAG service
│       └── test_integration.py      # Testes de integração do RAG service
├── tests/
│   └── test_rag_integration.py      # Testes de integração entre serviços
└── scripts/
    └── run_tests.sh                 # Script para executar todos os testes
```

## 🚀 Executando os Testes

### 1. Instalar Dependências de Teste

```bash
# No diretório rag-service
cd rag-service
pip install -r requirements.txt

# Ou instalar apenas dependências de teste
pip install pytest pytest-asyncio httpx
```

### 2. Executar Testes do RAG Service

```bash
cd rag-service
pytest tests/ -v
```

### 3. Executar Testes de Integração

```bash
# Na raiz do projeto
pytest tests/ -v
```

### 4. Executar Todos os Testes

```bash
# Usar o script automatizado
./scripts/run_tests.sh
```

## 📝 Tipos de Testes

### Testes Unitários (`test_rag_service.py`)

- ✅ Testes de chunking de texto
- ✅ Testes de inicialização do serviço
- ✅ Testes de limpeza de texto
- ✅ Testes de detecção de categoria
- ✅ Testes de similaridade cosseno
- ✅ Testes de salvamento/carregamento de índice

### Testes de Integração (`test_integration.py`)

- ✅ Testes de inicialização com configuração
- ✅ Testes de workflow completo (processar → salvar → carregar)
- ✅ Testes de endpoints da API
- ✅ Testes end-to-end

### Testes de Integração entre Serviços (`test_rag_integration.py`)

- ✅ Testes de comunicação HTTP entre backend e RAG service
- ✅ Testes de endpoints do RAG service
- ✅ Testes de RAG client no backend
- ✅ Testes de fluxo completo de interpretação

## ⚙️ Configuração

### Variáveis de Ambiente para Testes

Os testes podem precisar das seguintes variáveis:

```bash
export RAG_SERVICE_URL=http://localhost:8001
export BACKEND_URL=http://localhost:8000
```

### Serviços em Execução

Alguns testes de integração requerem que os serviços estejam rodando:

```bash
# Terminal 1: RAG Service
cd rag-service
uvicorn app.main:app --host 0.0.0.0 --port 8001

# Terminal 2: Backend
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🎯 Exemplos de Uso

### Executar Testes Específicos

```bash
# Apenas testes unitários
pytest rag-service/tests/test_rag_service.py -v

# Apenas testes de integração
pytest rag-service/tests/test_integration.py -v

# Teste específico
pytest rag-service/tests/test_rag_service.py::TestChunking::test_chunk_small_text -v
```

### Executar com Cobertura

```bash
pytest --cov=app --cov-report=html
```

### Executar Testes Assíncronos

```bash
pytest -v --asyncio-mode=auto
```

## 📊 Resultados Esperados

### Testes Unitários

- ✅ Todos os testes de chunking devem passar
- ✅ Testes de inicialização devem passar
- ✅ Testes de similaridade devem passar

### Testes de Integração

- ⚠️ Alguns testes podem ser pulados se FastEmbed não estiver instalado
- ⚠️ Alguns testes podem ser pulados se serviços não estiverem rodando

## 🔧 Troubleshooting

### Erro: "FastEmbed não instalado"

```bash
pip install fastembed
```

### Erro: "Serviço não está rodando"

Inicie os serviços antes de executar os testes de integração.

### Erro: "ModuleNotFoundError"

Certifique-se de que está no diretório correto e que os paths estão configurados.

## 📚 Próximos Passos

1. Adicionar mais testes de edge cases
2. Adicionar testes de performance
3. Adicionar testes de carga
4. Configurar CI/CD para executar testes automaticamente
