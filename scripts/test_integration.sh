#!/bin/bash
# Script para testar integração do RAG Service

set -e

echo "🧪 Testando integração do RAG Service"
echo ""

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se RAG service está rodando
echo "📡 Verificando se RAG service está rodando..."
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ RAG service está rodando${NC}"
else
    echo -e "${YELLOW}⚠️  RAG service não está rodando${NC}"
    echo "   Inicie com: docker-compose up rag-service"
    echo ""
    read -p "Deseja continuar mesmo assim? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Verificar se backend está rodando
echo "📡 Verificando se backend está rodando..."
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend está rodando${NC}"
else
    echo -e "${YELLOW}⚠️  Backend não está rodando${NC}"
    echo "   Inicie com: docker-compose up backend"
fi

echo ""
echo "🧪 Executando testes de integração..."
echo ""

# Configurar variável de ambiente
export RAG_SERVICE_URL=http://localhost:8001

# Executar testes
cd backend
pytest tests/integration/ -v --tb=short

echo ""
echo -e "${GREEN}✅ Testes concluídos!${NC}"

