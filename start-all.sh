#!/bin/bash

# Script para iniciar frontend e backend simultaneamente
# Uso: ./start-all.sh

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Obter o diretório do script (raiz do projeto)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# Criar diretório de logs se não existir
mkdir -p logs

echo -e "${BOLD}${CYAN}============================================================${NC}"
echo -e "${BOLD}${CYAN}  Iniciando CosmoAstrologia (Frontend + Backend)${NC}"
echo -e "${BOLD}${CYAN}============================================================${NC}\n"

# Função para limpar processos ao sair
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Parando servidores...${NC}"
    
    # Parar processos pelos PIDs
    [ ! -z "$BACKEND_PID" ] && kill $BACKEND_PID 2>/dev/null || true
    [ ! -z "$FRONTEND_PID" ] && kill $FRONTEND_PID 2>/dev/null || true
    
    # Matar processos nas portas
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    
    # Salvar PIDs nos arquivos para referência
    [ ! -z "$BACKEND_PID" ] && echo $BACKEND_PID > logs/backend.pid || true
    [ ! -z "$FRONTEND_PID" ] && echo $FRONTEND_PID > logs/frontend.pid || true
    
    echo -e "${GREEN}✅ Servidores parados${NC}"
    exit
}

trap cleanup SIGINT SIGTERM

# Verificar se um serviço está rodando em uma porta
is_port_in_use() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Matar processos antigos nas portas
echo -e "${BLUE}🧹 Limpando processos antigos...${NC}"
if is_port_in_use 8000; then
    echo -e "${YELLOW}⚠️  Porta 8000 em uso, liberando...${NC}"
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

if is_port_in_use 3000; then
    echo -e "${YELLOW}⚠️  Porta 3000 em uso, liberando...${NC}"
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

# Verificar se Python está disponível
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Erro: python3 não encontrado!${NC}"
    echo -e "   Instale Python 3.8+ primeiro."
    exit 1
fi

# ==================== BACKEND ====================
echo -e "\n${BOLD}${CYAN}[1/2] Configurando Backend${NC}"
echo -e "${BLUE}📦 Verificando ambiente virtual do backend...${NC}"

cd "$SCRIPT_DIR/backend" || exit 1

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Criando ambiente virtual...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Erro ao criar ambiente virtual!${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Ambiente virtual criado${NC}"
fi

# Ativar ambiente virtual
source venv/bin/activate

# Verificar e instalar dependências
if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}📥 Instalando dependências do backend...${NC}"
    pip install -q -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Erro ao instalar dependências do backend!${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Dependências do backend instaladas${NC}"
fi

# Verificar bibliotecas críticas
if ! python -c "import kerykeion" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  kerykeion não encontrado, instalando...${NC}"
    pip install -q kerykeion>=5.3.0
fi

if ! python -c "import ephem" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  ephem não encontrado, instalando...${NC}"
    pip install -q ephem
fi

# Criar banco de dados se não existir
if [ ! -f "astrologia.db" ]; then
    echo -e "${YELLOW}🗄️  Criando banco de dados...${NC}"
    python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)" 2>&1 | grep -v "^$" || true
    echo -e "${GREEN}✅ Banco de dados criado${NC}"
fi

# Iniciar backend
echo -e "${GREEN}🚀 Iniciando servidor backend...${NC}"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > "$SCRIPT_DIR/logs/backend.log" 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > "$SCRIPT_DIR/logs/backend.pid"

cd "$SCRIPT_DIR"

# Aguardar backend iniciar
echo -e "${BLUE}⏳ Aguardando backend iniciar...${NC}"
BACKEND_READY=false
for i in {1..20}; do
    if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend iniciado em http://localhost:8000${NC}"
        BACKEND_READY=true
        break
    fi
    sleep 1
    echo -n "."
done
echo ""

# Verificar se backend está rodando
if [ "$BACKEND_READY" = false ]; then
    echo -e "${YELLOW}⚠️  Backend pode não estar rodando. Verifique logs/backend.log${NC}"
    echo -e "${BLUE}📄 Últimas linhas do log:${NC}"
    tail -10 "$SCRIPT_DIR/logs/backend.log" 2>/dev/null || echo "   (log ainda não disponível)"
fi

# ==================== FRONTEND ====================
echo -e "\n${BOLD}${CYAN}[2/2] Configurando Frontend${NC}"

# Verificar se npm está disponível
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ Erro: npm não encontrado!${NC}"
    echo -e "   Instale Node.js e npm primeiro."
    cleanup
    exit 1
fi

# Verificar se é Next.js (package.json deve existir)
if [ ! -f "$SCRIPT_DIR/package.json" ]; then
    echo -e "${RED}❌ Erro: package.json não encontrado na raiz do projeto!${NC}"
    cleanup
    exit 1
fi

# Verificar e instalar dependências do frontend
if [ ! -d "$SCRIPT_DIR/node_modules" ]; then
    echo -e "${YELLOW}📦 Instalando dependências do frontend...${NC}"
    cd "$SCRIPT_DIR" || exit 1
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Erro ao instalar dependências do frontend!${NC}"
        cleanup
        exit 1
    fi
    echo -e "${GREEN}✅ Dependências do frontend instaladas${NC}"
fi

# Iniciar frontend (Next.js)
echo -e "${GREEN}🎨 Iniciando frontend (Next.js)...${NC}"
cd "$SCRIPT_DIR" || exit 1
npm run dev > "$SCRIPT_DIR/logs/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "$SCRIPT_DIR/logs/frontend.pid"

# Aguardar frontend iniciar (Next.js na porta 3000)
echo -e "${BLUE}⏳ Aguardando frontend iniciar...${NC}"
FRONTEND_READY=false
for i in {1..30}; do
    # Next.js pode demorar mais para compilar na primeira vez
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend iniciado em http://localhost:3000${NC}"
        FRONTEND_READY=true
        break
    fi
    sleep 1
    if [ $((i % 5)) -eq 0 ]; then
        echo -n "."
    fi
done
echo ""

# Verificar se frontend está rodando
if [ "$FRONTEND_READY" = false ]; then
    echo -e "${YELLOW}⚠️  Frontend pode não estar rodando. Verifique logs/frontend.log${NC}"
    echo -e "${BLUE}📄 Últimas linhas do log:${NC}"
    tail -10 "$SCRIPT_DIR/logs/frontend.log" 2>/dev/null || echo "   (log ainda não disponível)"
fi

# ==================== RESUMO ====================
echo ""
echo -e "${BOLD}${CYAN}============================================================${NC}"
echo -e "${BOLD}${GREEN}✅ Servidores Iniciados!${NC}"
echo -e "${BOLD}${CYAN}============================================================${NC}\n"

echo -e "${BOLD}🌐 URLs:${NC}"
echo -e "   ${GREEN}Frontend:${NC} http://localhost:3000"
echo -e "   ${GREEN}Backend:${NC}  http://localhost:8000"
echo -e "   ${GREEN}API Docs:${NC}  http://localhost:8000/docs"
echo ""

echo -e "${BOLD}📄 Logs:${NC}"
echo -e "   ${BLUE}Backend:${NC}  tail -f logs/backend.log"
echo -e "   ${BLUE}Frontend:${NC} tail -f logs/frontend.log"
echo ""

echo -e "${BOLD}🛑 Para parar:${NC} Pressione ${YELLOW}Ctrl+C${NC}"
echo ""

# Aguardar processos
wait

