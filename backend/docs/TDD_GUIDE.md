# 🧪 Guia de Test-Driven Development (TDD)

Este documento descreve como seguir TDD no desenvolvimento de código crítico do backend.

## 📋 Índice

1. [O que é TDD?](#o-que-é-tdd)
2. [Estrutura de Testes](#estrutura-de-testes)
3. [Workflow TDD](#workflow-tdd)
4. [Marcadores de Teste](#marcadores-de-teste)
5. [Executando Testes](#executando-testes)
6. [Boas Práticas](#boas-práticas)
7. [Exemplos](#exemplos)

---

## 🎯 O que é TDD?

**Test-Driven Development (TDD)** é uma metodologia onde:

1. **RED** 🔴: Escrevemos o teste ANTES do código
2. **GREEN** 🟢: Escrevemos o código mínimo para passar
3. **REFACTOR** 🔵: Melhoramos o código mantendo os testes passando

### Para Código Crítico

**TODO código crítico DEVE ter testes antes de ser considerado completo.**

Código crítico inclui:
- ✅ Serviços RAG e wrapper
- ✅ API endpoints
- ✅ Cálculos astrológicos/numerológicos
- ✅ Autenticação e segurança
- ✅ Integrações externas (Groq, etc)
- ✅ Tratamento de erros

---

## 📁 Estrutura de Testes

```
backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Fixtures e configurações globais
│   ├── unit/                 # Testes unitários (rápidos, isolados)
│   │   ├── test_rag_service_wrapper.py
│   │   ├── test_api_interpretation.py
│   │   └── test_astrology_calculator.py
│   └── integration/          # Testes de integração
│       └── ...
├── pytest.ini                # Configuração do pytest
└── scripts/
    └── run_tests.sh          # Script para executar testes
```

### Tipos de Teste

- **Unit Tests** (`tests/unit/`): Testam componentes isolados, rápidos
- **Integration Tests** (`tests/integration/`): Testam componentes trabalhando juntos

---

## 🔄 Workflow TDD

### 1. Escrever Teste Primeiro (RED 🔴)

```python
@pytest.mark.critical
@pytest.mark.unit
def test_minha_funcao_lida_com_erro_gracefully():
    """
    TDD: Função deve lidar com erro sem quebrar.
    Código crítico - garante resiliência.
    """
    # Arrange
    invalid_input = None
    
    # Act
    result = minha_funcao(invalid_input)
    
    # Assert
    assert result is not None
    assert result == expected_value
```

### 2. Executar Teste (Deve Falhar)

```bash
cd backend
./scripts/run_tests.sh quick
```

### 3. Escrever Código Mínimo (GREEN 🟢)

```python
def minha_funcao(input_val):
    if input_val is None:
        return expected_value
    # ... resto do código
```

### 4. Refatorar (REFACTOR 🔵)

Melhorar código mantendo testes passando.

### 5. Repetir

Continue o ciclo para cada funcionalidade.

---

## 🏷️ Marcadores de Teste

Use marcadores para organizar e filtrar testes:

### `@pytest.mark.critical`
**SEMPRE use em código crítico!**

```python
@pytest.mark.critical
@pytest.mark.unit
def test_something_critical():
    """Código crítico que deve sempre ter testes."""
    pass
```

### Outros Marcadores

- `@pytest.mark.unit` - Testes unitários
- `@pytest.mark.integration` - Testes de integração
- `@pytest.mark.api` - Testes de API endpoints
- `@pytest.mark.rag` - Testes do sistema RAG
- `@pytest.mark.calculation` - Testes de cálculos
- `@pytest.mark.slow` - Testes lentos (podem ser pulados)

### Executando por Marcador

```bash
# Apenas testes críticos
./scripts/run_tests.sh critical

# Apenas testes de API
pytest -m api

# Testes críticos E unitários
pytest -m "critical and unit"
```

---

## 🚀 Executando Testes

### Opções Rápidas

```bash
cd backend

# Todos os testes
./scripts/run_tests.sh all

# Apenas testes unitários (rápido)
./scripts/run_tests.sh unit

# Apenas código crítico
./scripts/run_tests.sh critical

# Testes com coverage
./scripts/run_tests.sh coverage

# Modo watch (reexecuta ao detectar mudanças)
./scripts/run_tests.sh watch

# Testes rápidos (para no primeiro erro)
./scripts/run_tests.sh quick
```

### Opções Avançadas

```bash
# Testes específicos
pytest tests/unit/test_rag_service_wrapper.py -v

# Apenas um teste específico
pytest tests/unit/test_rag_service_wrapper.py::TestRAGServiceWrapper::test_get_rag_service_returns_none -v

# Com mais detalhes
pytest -vv --tb=long

# Parar no primeiro erro
pytest -x
```

---

## ✅ Boas Práticas

### 1. Nomeie Testes Descritivamente

```python
# ❌ Ruim
def test_function():
    pass

# ✅ Bom
def test_get_rag_service_returns_none_when_llamaindex_unavailable():
    """TDD: Quando LlamaIndex não está disponível, get_rag_service deve retornar None."""
    pass
```

### 2. Use Arrange-Act-Assert

```python
def test_example():
    # Arrange - Preparar dados
    input_data = {"key": "value"}
    
    # Act - Executar ação
    result = process_data(input_data)
    
    # Assert - Verificar resultado
    assert result == expected
```

### 3. Um Conceito por Teste

```python
# ❌ Ruim - Múltiplos conceitos
def test_many_things():
    test_a()
    test_b()
    test_c()

# ✅ Bom - Um conceito
def test_specific_behavior():
    """Testa comportamento específico."""
    pass
```

### 4. Teste Código Crítico Primeiro

**Sempre que criar código crítico, escreva testes primeiro!**

Código crítico inclui:
- Tratamento de erros
- Validações de entrada
- Integrações externas
- Cálculos complexos

### 5. Use Fixtures para Dados Compartilhados

```python
# Em conftest.py
@pytest.fixture
def sample_birth_data():
    return {
        'birth_date': '1990-05-15',
        'birth_time': '10:30:00'
    }

# No teste
def test_calculation(sample_birth_data):
    result = calculate(sample_birth_data)
    assert result is not None
```

### 6. Mock Dependências Externas

```python
@patch('app.services.rag_service_wrapper._get_rag_service')
def test_with_mock(mock_service):
    mock_service.return_value = None
    # Testa comportamento quando serviço não está disponível
```

---

## 📝 Exemplos

### Exemplo 1: Teste de Código Crítico (RAG Service)

```python
@pytest.mark.critical
@pytest.mark.unit
def test_get_rag_service_returns_none_when_llamaindex_unavailable(self, mock_llamaindex_unavailable):
    """
    TDD: Quando LlamaIndex não está disponível, get_rag_service deve retornar None.
    Código crítico - garante que o app não quebra se dependências não estiverem instaladas.
    """
    # Arrange & Act
    service = get_rag_service()
    
    # Assert
    assert service is None, "Service deve ser None quando LlamaIndex não está disponível"
```

### Exemplo 2: Teste de API Endpoint

```python
@pytest.mark.critical
@pytest.mark.api
@pytest.mark.unit
def test_get_interpretation_returns_503_when_rag_service_unavailable(self, client):
    """
    TDD: Endpoint deve retornar 503 quando serviço RAG não está disponível.
    Código crítico - garante resposta apropriada quando serviço está down.
    """
    # Arrange
    with patch('app.api.interpretation.get_rag_service', return_value=None):
        # Act
        response = client.post("/api/interpretation", json={"planet": "Sol"})
        
        # Assert
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
```

### Exemplo 3: Teste de Cálculo

```python
@pytest.mark.critical
@pytest.mark.calculation
@pytest.mark.unit
def test_get_zodiac_sign_returns_correct_sign_for_aries(self):
    """
    TDD: Deve retornar Áries para longitude 0-30 graus.
    Código crítico - garante precisão dos cálculos de signo.
    """
    # Arrange
    longitude = 15.0  # Áries
    
    # Act
    result = get_zodiac_sign(longitude)
    
    # Assert
    assert result["sign"] == "Áries"
    assert result["degree"] == pytest.approx(15.0, abs=0.1)
```

---

## 🎯 Checklist para Código Crítico

Antes de considerar código crítico como completo:

- [ ] Teste escrito ANTES ou junto com o código
- [ ] Teste marcado com `@pytest.mark.critical`
- [ ] Teste cobre caso de sucesso
- [ ] Teste cobre caso de erro
- [ ] Teste cobre casos extremos (edge cases)
- [ ] Testes passam: `./scripts/run_tests.sh critical`
- [ ] Coverage acima de 70% para código crítico
- [ ] Documentação do teste explica o que está sendo testado e por quê

---

## 📊 Coverage

A meta de coverage é:
- **Código Crítico**: 90%+ de coverage
- **Código Geral**: 70%+ de coverage

Para ver coverage:

```bash
./scripts/run_tests.sh coverage
```

Relatório HTML será gerado em `htmlcov/index.html`

---

## 🔗 Referências

- [Pytest Documentation](https://docs.pytest.org/)
- [TDD by Example (Kent Beck)](https://www.amazon.com/Test-Driven-Development-Kent-Beck/dp/0321146530)
- [Python Testing Guide](https://docs.python-guide.org/writing/tests/)

---

## 💡 Lembrete

**TODO código crítico DEVE ter testes!**

Se você está escrevendo código crítico sem testes, você está fazendo errado! 🚨

Testes não são opcionais para código crítico - são obrigatórios! ✅

