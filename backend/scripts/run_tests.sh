#!/bin/bash
# Script para executar testes TDD do backend

set -e  # Parar em caso de erro

echo "🧪 Executando Testes TDD - Backend"
echo "=================================="
echo ""

# Verificar se estamos no diretório correto
if [ ! -f "pytest.ini" ]; then
    echo "❌ Erro: Execute este script a partir do diretório backend/"
    exit 1
fi

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Função para executar testes
run_tests() {
    local test_type=$1
    local marker=$2
    
    echo -e "${YELLOW}Executando testes: ${test_type}${NC}"
    echo "----------------------------------------"
    
    if [ -z "$marker" ]; then
        pytest tests/unit/ -v --tb=short
    else
        pytest tests/unit/ -v --tb=short -m "$marker"
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Testes ${test_type} passaram!${NC}"
        echo ""
        return 0
    else
        echo -e "${RED}❌ Testes ${test_type} falharam!${NC}"
        echo ""
        return 1
    fi
}

# Menu de opções
case "${1:-all}" in
    "all")
        echo "Executando TODOS os testes..."
        echo ""
        pytest tests/ -v --tb=short --cov=app --cov-report=term-missing
        ;;
    
    "unit")
        echo "Executando apenas testes unitários..."
        echo ""
        pytest tests/unit/ -v --tb=short
        ;;
    
    "critical")
        echo "Executando testes CRÍTICOS..."
        echo ""
        pytest tests/ -v --tb=short -m critical
        ;;
    
    "api")
        echo "Executando testes de API..."
        echo ""
        pytest tests/ -v --tb=short -m api
        ;;
    
    "rag")
        echo "Executando testes RAG..."
        echo ""
        pytest tests/ -v --tb=short -m rag
        ;;
    
    "coverage")
        echo "Executando testes com coverage..."
        echo ""
        pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing
        echo ""
        echo "📊 Relatório de coverage gerado em htmlcov/index.html"
        ;;
    
    "watch")
        echo "Modo watch - reexecutando testes ao detectar mudanças..."
        echo "Pressione Ctrl+C para parar"
        echo ""
        pytest-watch tests/unit/ -v
        ;;
    
    "quick")
        echo "Executando testes rápidos (sem coverage)..."
        echo ""
        pytest tests/unit/ -v --tb=line -x  # Parar no primeiro erro
        ;;
    
    *)
        echo "Uso: $0 [all|unit|critical|api|rag|coverage|watch|quick]"
        echo ""
        echo "Opções:"
        echo "  all       - Executa todos os testes (padrão)"
        echo "  unit      - Apenas testes unitários"
        echo "  critical  - Apenas testes críticos"
        echo "  api       - Apenas testes de API"
        echo "  rag       - Apenas testes RAG"
        echo "  coverage  - Testes com relatório de coverage"
        echo "  watch     - Modo watch (reexecuta ao detectar mudanças)"
        echo "  quick     - Testes rápidos (para no primeiro erro)"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✨ Testes concluídos!${NC}"

