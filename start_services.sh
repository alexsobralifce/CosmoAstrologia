#!/bin/bash
# Script para iniciar todos os serviços (Backend, RAG Service, Frontend)

set -e

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

print_header() {
    echo -e "\n${BOLD}${CYAN}============================================================${NC}"
    echo -e "${BOLD}${CYAN}$(printf '%*s' $(((${#1}+60)/2)) "$1")${NC}"
    echo -e "${BOLD}${CYAN}============================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Verificar se docker-compose está disponível
check_docker_compose() {
    if command -v docker-compose &> /dev/null || docker compose version &> /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Verificar se um serviço está rodando
is_service_running() {
    local port=$1
    local name=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Iniciar serviços com Docker Compose
start_with_docker() {
    print_header "Iniciando Serviços com Docker Compose"
    
    # Verificar se docker-compose.yml existe
    if [ ! -f "docker-compose.yml" ]; then
        print_error "docker-compose.yml não encontrado"
        return 1
    fi
    
    print_info "Iniciando serviços..."
    
    # Iniciar em background
    if docker compose up -d 2>/dev/null || docker-compose up -d 2>/dev/null; then
        print_success "Serviços iniciados com Docker Compose"
        
        # Aguardar serviços iniciarem
        print_info "Aguardando serviços iniciarem..."
        sleep 5
        
        # Verificar status
        check_services_status
        return 0
    else
        print_error "Erro ao iniciar serviços com Docker Compose"
        return 1
    fi
}

# Iniciar serviços manualmente
start_manually() {
    print_header "Iniciando Serviços Manualmente"
    
    # Criar diretório para logs
    mkdir -p logs
    
    # Verificar se serviços já estão rodando
    if is_service_running 8001 "RAG Service"; then
        print_warning "RAG Service já está rodando na porta 8001"
    else
        print_info "Iniciando RAG Service na porta 8001..."
        cd rag-service
        nohup uvicorn app.main:app --host 0.0.0.0 --port 8001 > ../logs/rag-service.log 2>&1 &
        RAG_PID=$!
        echo $RAG_PID > ../logs/rag-service.pid
        cd ..
        print_success "RAG Service iniciado (PID: $RAG_PID)"
    fi
    
    if is_service_running 8000 "Backend"; then
        print_warning "Backend já está rodando na porta 8000"
    else
        print_info "Iniciando Backend na porta 8000..."
        cd backend
        nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
        BACKEND_PID=$!
        echo $BACKEND_PID > ../logs/backend.pid
        cd ..
        print_success "Backend iniciado (PID: $BACKEND_PID)"
    fi
    
    if is_service_running 5173 "Frontend"; then
        print_warning "Frontend já está rodando na porta 5173"
    else
        print_info "Iniciando Frontend na porta 5173..."
        # Verificar se é Vite
        if [ -f "package.json" ]; then
            nohup npm run dev > logs/frontend.log 2>&1 &
            FRONTEND_PID=$!
            echo $FRONTEND_PID > logs/frontend.pid
            print_success "Frontend iniciado (PID: $FRONTEND_PID)"
        else
            print_warning "Frontend não encontrado (package.json não existe)"
        fi
    fi
    
    # Aguardar serviços iniciarem
    print_info "Aguardando serviços iniciarem..."
    sleep 3
    
    # Verificar status
    check_services_status
}

# Verificar status dos serviços
check_services_status() {
    print_header "Status dos Serviços"
    
    # RAG Service
    if is_service_running 8001 "RAG Service"; then
        if curl -s http://localhost:8001/health > /dev/null 2>&1; then
            print_success "RAG Service: Rodando em http://localhost:8001"
        else
            print_warning "RAG Service: Porta 8001 em uso mas não responde"
        fi
    else
        print_error "RAG Service: Não está rodando"
    fi
    
    # Backend
    if is_service_running 8000 "Backend"; then
        if curl -s http://localhost:8000/ > /dev/null 2>&1; then
            print_success "Backend: Rodando em http://localhost:8000"
        else
            print_warning "Backend: Porta 8000 em uso mas não responde"
        fi
    else
        print_error "Backend: Não está rodando"
    fi
    
    # Frontend
    if is_service_running 5173 "Frontend"; then
        print_success "Frontend: Rodando em http://localhost:5173"
    else
        print_warning "Frontend: Não está rodando"
    fi
}

# Parar serviços
stop_services() {
    print_header "Parando Serviços"
    
    # Tentar parar com Docker Compose primeiro
    if [ -f "docker-compose.yml" ] && check_docker_compose; then
        print_info "Parando serviços com Docker Compose..."
        docker compose down 2>/dev/null || docker-compose down 2>/dev/null
        print_success "Serviços parados"
        return 0
    fi
    
    # Parar processos manualmente
    if [ -f "logs/rag-service.pid" ]; then
        RAG_PID=$(cat logs/rag-service.pid)
        if kill -0 $RAG_PID 2>/dev/null; then
            kill $RAG_PID
            print_success "RAG Service parado (PID: $RAG_PID)"
        fi
        rm -f logs/rag-service.pid
    fi
    
    if [ -f "logs/backend.pid" ]; then
        BACKEND_PID=$(cat logs/backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            print_success "Backend parado (PID: $BACKEND_PID)"
        fi
        rm -f logs/backend.pid
    fi
    
    if [ -f "logs/frontend.pid" ]; then
        FRONTEND_PID=$(cat logs/frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            print_success "Frontend parado (PID: $FRONTEND_PID)"
        fi
        rm -f logs/frontend.pid
    fi
    
    # Parar processos nas portas
    for port in 8001 8000 5173; do
        PID=$(lsof -ti:$port 2>/dev/null || true)
        if [ ! -z "$PID" ]; then
            kill $PID 2>/dev/null || true
        fi
    done
}

# Mostrar logs
show_logs() {
    local service=$1
    
    if [ -z "$service" ]; then
        print_error "Especifique o serviço: rag-service, backend ou frontend"
        return 1
    fi
    
    if [ -f "docker-compose.yml" ] && check_docker_compose; then
        print_info "Mostrando logs do $service (Docker Compose)..."
        docker compose logs -f $service 2>/dev/null || docker-compose logs -f $service 2>/dev/null
    elif [ -f "logs/$service.log" ]; then
        print_info "Mostrando logs do $service..."
        tail -f logs/$service.log
    else
        print_error "Logs não encontrados para $service"
    fi
}

# Menu principal
main() {
    case "${1:-start}" in
        start)
            print_header "Iniciando Serviços - CosmoAstrologia"
            
            # Verificar se Docker Compose está disponível
            if check_docker_compose && [ -f "docker-compose.yml" ]; then
                read -p "Usar Docker Compose? (s/n) [s]: " use_docker
                use_docker=${use_docker:-s}
                
                if [ "$use_docker" = "s" ]; then
                    start_with_docker
                else
                    start_manually
                fi
            else
                print_info "Docker Compose não disponível, iniciando manualmente..."
                start_manually
            fi
            
            echo ""
            print_success "Serviços iniciados!"
            print_info "URLs:"
            print_info "  - RAG Service: http://localhost:8001"
            print_info "  - Backend: http://localhost:8000"
            print_info "  - Frontend: http://localhost:5173"
            ;;
        
        stop)
            stop_services
            ;;
        
        restart)
            stop_services
            sleep 2
            main start
            ;;
        
        status)
            check_services_status
            ;;
        
        logs)
            show_logs "$2"
            ;;
        
        *)
            echo "Uso: $0 {start|stop|restart|status|logs [service]}"
            echo ""
            echo "Comandos:"
            echo "  start   - Inicia todos os serviços"
            echo "  stop    - Para todos os serviços"
            echo "  restart - Reinicia todos os serviços"
            echo "  status  - Mostra status dos serviços"
            echo "  logs    - Mostra logs de um serviço (rag-service, backend, frontend)"
            exit 1
            ;;
    esac
}

main "$@"

