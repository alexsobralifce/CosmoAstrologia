# 🧪 Testes TDD - Backend

Estrutura de testes seguindo Test-Driven Development para garantir qualidade e confiabilidade do código crítico.

## 🚀 Quick Start

```bash
cd backend

# Instalar dependências de teste
pip install -r requirements.txt

# Executar todos os testes
./scripts/run_tests.sh all

# Executar apenas testes críticos
./scripts/run_tests.sh critical

# Executar apenas testes unitários (rápido)
./scripts/run_tests.sh unit
```

## 📁 Estrutura

```
tests/
├── __init__.py
├── conftest.py              # Fixtures compartilhadas
├── unit/                    # Testes unitários
│   ├── test_rag_service_wrapper.py
│   ├── test_rag_service_llamaindex.py
│   ├── test_api_interpretation.py
│   └── test_astrology_calculator.py
└── integration/             # Testes de integração
```

## 🏷️ Marcadores

- `@pytest.mark.critical` - **Código crítico** (sempre usar!)
- `@pytest.mark.unit` - Testes unitários
- `@pytest.mark.integration` - Testes de integração
- `@pytest.mark.api` - Testes de API
- `@pytest.mark.rag` - Testes RAG
- `@pytest.mark.calculation` - Testes de cálculos

## 📖 Documentação Completa

Veja o [Guia TDD completo](../docs/TDD_GUIDE.md) para:
- Workflow TDD completo
- Boas práticas
- Exemplos detalhados
- Checklist para código crítico

## 🎯 Regra de Ouro

**TODO código crítico DEVE ter testes antes de ser considerado completo!**

Código crítico = código que se quebrar, quebra o sistema!

