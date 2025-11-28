#!/bin/bash

# Script para configurar variáveis de ambiente localmente
# Uso: ./scripts/setup-env.sh

set -e

echo "🔧 Configurando variáveis de ambiente para desenvolvimento local..."
echo ""

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================
# Backend .env
# ============================================

BACKEND_ENV="backend/.env"
BACKEND_ENV_EXAMPLE="backend/.env.example"

if [ ! -f "$BACKEND_ENV" ]; then
    if [ -f "$BACKEND_ENV_EXAMPLE" ]; then
        echo "📝 Criando $BACKEND_ENV a partir de $BACKEND_ENV_EXAMPLE..."
        cp "$BACKEND_ENV_EXAMPLE" "$BACKEND_ENV"
        
        # Gerar SECRET_KEY se não estiver definida
        if grep -q "your-secret-key-change-in-production" "$BACKEND_ENV"; then
            echo "🔑 Gerando SECRET_KEY..."
            SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || echo "your-secret-key-change-in-production")
            if [ "$SECRET_KEY" != "your-secret-key-change-in-production" ]; then
                # Substituir SECRET_KEY no arquivo (compatível com macOS e Linux)
                if [[ "$OSTYPE" == "darwin"* ]]; then
                    sed -i '' "s/SECRET_KEY=your-secret-key-change-in-production/SECRET_KEY=$SECRET_KEY/" "$BACKEND_ENV"
                else
                    sed -i "s/SECRET_KEY=your-secret-key-change-in-production/SECRET_KEY=$SECRET_KEY/" "$BACKEND_ENV"
                fi
                echo -e "${GREEN}✅ SECRET_KEY gerada automaticamente${NC}"
            fi
        fi
        
        echo -e "${GREEN}✅ $BACKEND_ENV criado!${NC}"
        echo -e "${YELLOW}⚠️  Lembre-se de configurar GROQ_API_KEY se usar interpretações com IA${NC}"
    else
        echo -e "${YELLOW}⚠️  $BACKEND_ENV_EXAMPLE não encontrado. Pulando...${NC}"
    fi
else
    echo -e "${GREEN}✅ $BACKEND_ENV já existe${NC}"
fi

# ============================================
# Frontend .env.local
# ============================================

FRONTEND_ENV=".env.local"
FRONTEND_ENV_EXAMPLE=".env.local.example"

if [ ! -f "$FRONTEND_ENV" ]; then
    if [ -f "$FRONTEND_ENV_EXAMPLE" ]; then
        echo "📝 Criando $FRONTEND_ENV a partir de $FRONTEND_ENV_EXAMPLE..."
        cp "$FRONTEND_ENV_EXAMPLE" "$FRONTEND_ENV"
        echo -e "${GREEN}✅ $FRONTEND_ENV criado!${NC}"
    else
        echo -e "${YELLOW}⚠️  $FRONTEND_ENV_EXAMPLE não encontrado. Pulando...${NC}"
    fi
else
    echo -e "${GREEN}✅ $FRONTEND_ENV já existe${NC}"
fi

echo ""
echo "=========================================="
echo "✅ Configuração concluída!"
echo "=========================================="
echo ""
echo "📋 Próximos passos:"
echo ""
echo "1. Edite backend/.env e configure:"
echo "   - GROQ_API_KEY (se usar interpretações com IA)"
echo ""
echo "2. Edite .env.local e verifique:"
echo "   - VITE_API_URL=http://localhost:8000"
echo ""
echo "3. Inicie o backend:"
echo "   ./scripts/start-backend.sh"
echo ""
echo "4. Inicie o frontend:"
echo "   npm run dev"
echo ""
echo "📚 Documentação completa: docs/CONFIGURACAO_LOCAL.md"
echo ""

