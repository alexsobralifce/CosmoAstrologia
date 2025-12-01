#!/bin/bash
# Script para executar todos os testes

set -e

echo "=========================================="
echo "EXECUTANDO TESTES DO SISTEMA"
echo "=========================================="

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. Testes do RAG Service
echo -e "\n${BLUE}1. Testes do RAG Service${NC}"
echo "----------------------------------------"
cd rag-service
if [ -d "tests" ]; then
    python -m pytest tests/ -v
    echo -e "${GREEN}✓ Testes do RAG Service concluídos${NC}"
else
    echo "⚠ Pasta de testes não encontrada"
fi
cd ..

# 2. Testes de Integração
echo -e "\n${BLUE}2. Testes de Integração${NC}"
echo "----------------------------------------"
if [ -d "tests" ]; then
    python -m pytest tests/ -v -m "not slow"
    echo -e "${GREEN}✓ Testes de Integração concluídos${NC}"
else
    echo "⚠ Pasta de testes não encontrada"
fi

# 3. Testes do Backend (se existirem)
echo -e "\n${BLUE}3. Testes do Backend${NC}"
echo "----------------------------------------"
if [ -d "backend/tests" ]; then
    cd backend
    python -m pytest tests/ -v
    echo -e "${GREEN}✓ Testes do Backend concluídos${NC}"
    cd ..
else
    echo "⚠ Pasta de testes do backend não encontrada"
fi

echo -e "\n${GREEN}=========================================="
echo "TODOS OS TESTES CONCLUÍDOS"
echo "==========================================${NC}"

