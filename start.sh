#!/usr/bin/env bash
# Script para iniciar/parar frontend e backend do sistema de Astrologia
# Uso: ./start.sh
# Compatível com bash e zsh

set -e

FRONTEND_PORT=3000
BACKEND_PORT=8000
FRONTEND_PID_FILE=".frontend.pid"
BACKEND_PID_FILE=".backend.pid"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para verificar se uma porta está em uso
check_port() {
    local port=$1
    # Tentar lsof primeiro (Mac/Linux)
    if command -v lsof >/dev/null 2>&1; then
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            return 0  # Porta em uso
        fi
    # Fallback para netstat (Linux)
    elif command -v netstat >/dev/null 2>&1; then
        if netstat -tuln 2>/dev/null | grep -q ":$port " || netstat -an 2>/dev/null | grep -q ":$port.*LISTEN"; then
            return 0  # Porta em uso
        fi
    fi
    return 1  # Porta livre
}

# Função para encontrar PID por porta
find_pid_by_port() {
    local port=$1
    local pid=""
    
    # Tentar lsof primeiro
    if command -v lsof >/dev/null 2>&1; then
        pid=$(lsof -ti :$port 2>/dev/null | head -n1)
    # Fallback para netstat (Linux)
    elif command -v netstat >/dev/null 2>&1 && command -v awk >/dev/null 2>&1; then
        pid=$(netstat -tulpn 2>/dev/null | grep ":$port " | grep LISTEN | awk '{print $7}' | cut -d'/' -f1 | head -n1)
    fi
    
    if [ -z "$pid" ] || [ "$pid" = "-" ]; then
        echo ""
    else
        echo "$pid"
    fi
}

# Função para matar processo por PID
kill_process() {
    local pid=$1
    local name=$2
    if [ -n "$pid" ] && [ "$pid" != "" ] && kill -0 "$pid" 2>/dev/null; then
        echo -e "${YELLOW}Matando processo $name (PID: $pid)...${NC}"
        kill "$pid" 2>/dev/null || true
        sleep 1
        # Se ainda estiver rodando, force kill
        if kill -0 "$pid" 2>/dev/null; then
            kill -9 "$pid" 2>/dev/null || true
            sleep 0.5
        fi
        echo -e "${GREEN}Processo $name encerrado${NC}"
    fi
}

# Verificar se frontend está rodando
frontend_running=false
backend_running=false
FRONTEND_PID=""
BACKEND_PID=""

if check_port $FRONTEND_PORT; then
    frontend_running=true
    FRONTEND_PID=$(find_pid_by_port $FRONTEND_PORT)
    if [ -z "$FRONTEND_PID" ]; then
        frontend_running=false
    fi
fi

if check_port $BACKEND_PORT; then
    backend_running=true
    BACKEND_PID=$(find_pid_by_port $BACKEND_PORT)
    if [ -z "$BACKEND_PID" ]; then
        backend_running=false
    fi
fi

# Se ambos estiverem rodando, matar os processos
if [ "$frontend_running" = true ] || [ "$backend_running" = true ]; then
    echo -e "${BLUE}=== Encerrando serviços ===${NC}"
    
    if [ "$frontend_running" = true ]; then
        kill_process "$FRONTEND_PID" "Frontend (porta $FRONTEND_PORT)"
        rm -f $FRONTEND_PID_FILE
    fi
    
    if [ "$backend_running" = true ]; then
        kill_process "$BACKEND_PID" "Backend (porta $BACKEND_PORT)"
        rm -f $BACKEND_PID_FILE
    fi
    
    echo -e "${GREEN}Serviços encerrados!${NC}"
    exit 0
fi

# Se não estiverem rodando, iniciar ambos
echo -e "${BLUE}=== Iniciando serviços ===${NC}"

# Verificar se estamos na raiz do projeto
if [ ! -f "package.json" ] || [ ! -d "backend" ]; then
    echo -e "${RED}Erro: Execute este script na raiz do projeto${NC}"
    exit 1
fi

# Função para limpar ao sair
cleanup() {
    echo -e "\n${YELLOW}=== Encerrando serviços ===${NC}"
    if [ -f "$FRONTEND_PID_FILE" ]; then
        FRONTEND_PID=$(cat $FRONTEND_PID_FILE)
        kill_process "$FRONTEND_PID" "Frontend"
        rm -f $FRONTEND_PID_FILE
    fi
    if [ -f "$BACKEND_PID_FILE" ]; then
        BACKEND_PID=$(cat $BACKEND_PID_FILE)
        kill_process "$BACKEND_PID" "Backend"
        rm -f $BACKEND_PID_FILE
    fi
    exit 0
}

# Capturar Ctrl+C para limpar processos
trap cleanup SIGINT SIGTERM

# Iniciar Backend
echo -e "${BLUE}Iniciando Backend na porta $BACKEND_PORT...${NC}"
cd backend

# Verificar se existe venv, criar se não existir
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Criando ambiente virtual Python...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Erro ao criar ambiente virtual${NC}"
        exit 1
    fi
fi

# Ativar venv
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Verificar se python está disponível
if ! command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1; then
    echo -e "${RED}Erro: Python não encontrado${NC}"
    exit 1
fi

# Verificar se dependências estão instaladas
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}Instalando dependências do backend...${NC}"
    pip install --upgrade pip >/dev/null 2>&1
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}Erro ao instalar dependências${NC}"
        echo -e "${YELLOW}Tente executar manualmente: cd backend && pip install -r requirements.txt${NC}"
        exit 1
    fi
fi

# Usar python3 se disponível, senão python
PYTHON_CMD=$(command -v python3 2>/dev/null || command -v python 2>/dev/null)

# Iniciar backend em background
"$PYTHON_CMD" run.py > ../.backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > "../$BACKEND_PID_FILE"
cd ..

echo -e "${GREEN}Backend iniciado - PID: $BACKEND_PID${NC}"
echo -e "${BLUE}Logs do Backend: ${NC}tail -f .backend.log"
echo ""

# Aguardar backend iniciar
echo -e "${YELLOW}Aguardando backend iniciar...${NC}"
sleep 3

# Verificar se backend está rodando
if [ -z "$BACKEND_PID" ] || ! kill -0 "$BACKEND_PID" 2>/dev/null; then
    echo -e "${RED}Erro: Backend não iniciou corretamente${NC}"
    echo -e "${YELLOW}Verifique os logs: cat .backend.log${NC}"
    if [ -f "$BACKEND_PID_FILE" ]; then
        rm -f "$BACKEND_PID_FILE"
    fi
    exit 1
fi

# Iniciar Frontend
echo -e "${BLUE}Iniciando Frontend na porta $FRONTEND_PORT...${NC}"

# Verificar se node_modules existe e se package.json existe
if [ ! -d "node_modules" ] || [ ! -f "package.json" ]; then
    echo -e "${YELLOW}Instalando dependências do frontend...${NC}"
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}Erro ao instalar dependências do frontend${NC}"
        echo -e "${YELLOW}Tente executar manualmente: npm install${NC}"
        if [ -n "$BACKEND_PID" ]; then
            kill_process "$BACKEND_PID" "Backend"
        fi
        if [ -f "$BACKEND_PID_FILE" ]; then
            rm -f "$BACKEND_PID_FILE"
        fi
        exit 1
    fi
fi

# Verificar se npm está disponível
if ! command -v npm >/dev/null 2>&1; then
    echo -e "${RED}Erro: npm não encontrado${NC}"
    if [ -n "$BACKEND_PID" ]; then
        kill_process "$BACKEND_PID" "Backend"
    fi
    if [ -f "$BACKEND_PID_FILE" ]; then
        rm -f "$BACKEND_PID_FILE"
    fi
    exit 1
fi

# Iniciar frontend em background
npm run dev > .frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > $FRONTEND_PID_FILE

echo -e "${GREEN}Frontend iniciado - PID: $FRONTEND_PID${NC}"
echo -e "${BLUE}Logs do Frontend: ${NC}tail -f .frontend.log"
echo ""

# Aguardar frontend iniciar
echo -e "${YELLOW}Aguardando frontend iniciar...${NC}"
sleep 3

# Verificar se frontend está rodando
if [ -z "$FRONTEND_PID" ] || ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
    echo -e "${RED}Erro: Frontend não iniciou corretamente${NC}"
    echo -e "${YELLOW}Verifique os logs: cat .frontend.log${NC}"
    if [ -f "$FRONTEND_PID_FILE" ]; then
        rm -f "$FRONTEND_PID_FILE"
    fi
    if [ -n "$BACKEND_PID" ]; then
        kill_process "$BACKEND_PID" "Backend"
    fi
    if [ -f "$BACKEND_PID_FILE" ]; then
        rm -f "$BACKEND_PID_FILE"
    fi
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✅ Serviços iniciados com sucesso!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Frontend:${NC} http://localhost:$FRONTEND_PORT (PID: $FRONTEND_PID)"
echo -e "${BLUE}Backend:${NC}  http://localhost:$BACKEND_PORT (PID: $BACKEND_PID)"
echo ""
echo -e "${YELLOW}Ver logs em tempo real:${NC}"
echo -e "  ${BLUE}Backend:${NC}  tail -f .backend.log"
echo -e "  ${BLUE}Frontend:${NC} tail -f .frontend.log"
echo -e "  ${BLUE}Ambos:${NC}    tail -f .backend.log .frontend.log"
echo ""
echo -e "${YELLOW}Pressione Ctrl+C para encerrar os serviços${NC}"
echo ""

# Monitorar processos e mostrar logs
if command -v tail >/dev/null 2>&1; then
    tail -f .backend.log .frontend.log 2>/dev/null &
    TAIL_PID=$!
else
    echo -e "${YELLOW}tail não encontrado. Use 'cat .backend.log' ou 'cat .frontend.log' para ver logs${NC}"
    TAIL_PID=""
fi

# Função para monitorar processos
monitor_processes() {
    while true; do
        # Verificar se processos ainda estão rodando
        if [ -n "$BACKEND_PID" ] && ! kill -0 "$BACKEND_PID" 2>/dev/null; then
            echo -e "${YELLOW}Backend encerrou inesperadamente${NC}"
            break
        fi
        if [ -n "$FRONTEND_PID" ] && ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
            echo -e "${YELLOW}Frontend encerrou inesperadamente${NC}"
            break
        fi
        sleep 2
    done
}

# Aguardar até que os processos terminem ou Ctrl+C
if [ -n "$TAIL_PID" ]; then
    wait "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || monitor_processes
else
    monitor_processes
fi

# Limpar ao sair
cleanup

