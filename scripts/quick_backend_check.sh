#!/bin/bash
# Verificação rápida do backend

echo "🔍 Verificando backend..."

# Verificar se está rodando
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ Backend está rodando e respondendo!"
    exit 0
else
    echo "❌ Backend não está respondendo"
    echo ""
    echo "Para iniciar o backend:"
    echo "  cd backend && python3 run.py"
    echo ""
    echo "Ou use o script:"
    echo "  ./start-backend.sh"
    exit 1
fi
