#!/bin/bash
# Script shell alternativo para testar serviços

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

check_service() {
    local url=$1
    local name=$2
    
    if curl -s --max-time 5 "$url" > /dev/null 2>&1; then
        print_success "$name está respondendo"
        return 0
    else
        print_error "$name não está acessível em $url"
        return 1
    fi
}

test_rag_service() {
    print_header "Testando RAG Service"
    
    # Health check
    print_info "Verificando health check..."
    if ! check_service "http://localhost:8001/health" "RAG Service"; then
        return 1
    fi
    
    # Status
    print_info "Verificando status..."
    response=$(curl -s --max-time 10 "http://localhost:8001/api/rag/status" 2>/dev/null)
    if [ $? -eq 0 ]; then
        print_success "Status endpoint funcionando"
        echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    else
        print_error "Erro ao verificar status"
        return 1
    fi
    
    # Search
    print_info "Testando busca..."
    response=$(curl -s --max-time 15 -X POST "http://localhost:8001/api/rag/search" \
        -H "Content-Type: application/json" \
        -d '{"query": "Sol em Libra", "top_k": 3}' 2>/dev/null)
    if [ $? -eq 0 ]; then
        count=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('count', 0))" 2>/dev/null || echo "0")
        print_success "Busca funcionando: $count resultados"
    else
        print_warning "Erro na busca"
    fi
    
    return 0
}

test_backend() {
    print_header "Testando Backend"
    
    # Root
    print_info "Verificando root endpoint..."
    if ! check_service "http://localhost:8000/" "Backend"; then
        return 1
    fi
    
    # Status
    print_info "Verificando status do RAG via backend..."
    response=$(curl -s --max-time 10 "http://localhost:8000/api/interpretation/status" 2>/dev/null)
    if [ $? -eq 0 ]; then
        print_success "Status endpoint funcionando"
    else
        print_warning "Erro ao verificar status"
    fi
    
    # Search
    print_info "Testando busca via backend..."
    response=$(curl -s --max-time 15 "http://localhost:8000/api/interpretation/search?query=Sol%20em%20Libra&top_k=3" 2>/dev/null)
    if [ $? -eq 0 ]; then
        count=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('count', 0))" 2>/dev/null || echo "0")
        print_success "Busca via backend funcionando: $count resultados"
    else
        print_warning "Erro na busca"
    fi
    
    return 0
}

test_integration() {
    print_header "Testando Integração"
    
    # Verificar se ambos estão rodando
    if ! curl -s --max-time 5 "http://localhost:8001/health" > /dev/null 2>&1; then
        print_error "RAG Service não está rodando"
        return 1
    fi
    
    if ! curl -s --max-time 5 "http://localhost:8000/" > /dev/null 2>&1; then
        print_error "Backend não está rodando"
        return 1
    fi
    
    print_success "Ambos os serviços estão rodando"
    
    # Testar fluxo completo
    print_info "Testando fluxo completo..."
    response=$(curl -s --max-time 30 -X POST "http://localhost:8000/api/interpretation" \
        -H "Content-Type: application/json" \
        -d '{"planet": "Sol", "sign": "Libra", "use_groq": false}' 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        interpretation=$(echo "$response" | python3 -c "import sys, json; print(len(json.load(sys.stdin).get('interpretation', '')))" 2>/dev/null || echo "0")
        if [ "$interpretation" -gt 0 ]; then
            print_success "Fluxo completo funcionando! ($interpretation chars)"
            return 0
        else
            print_warning "Interpretação retornou vazia"
            return 1
        fi
    else
        print_error "Erro no fluxo completo"
        return 1
    fi
}

main() {
    print_header "Teste de Serviços - CosmoAstrologia"
    
    RAG_OK=false
    BACKEND_OK=false
    INTEGRATION_OK=false
    
    # Testar RAG
    if test_rag_service; then
        RAG_OK=true
    fi
    
    # Testar Backend
    if test_backend; then
        BACKEND_OK=true
    fi
    
    # Testar integração
    if [ "$RAG_OK" = true ] && [ "$BACKEND_OK" = true ]; then
        if test_integration; then
            INTEGRATION_OK=true
        fi
    else
        print_warning "Pulando teste de integração (serviços não estão rodando)"
    fi
    
    # Resumo
    print_header "Resumo"
    
    if [ "$RAG_OK" = true ]; then
        print_success "RAG Service: PASSOU"
    else
        print_error "RAG Service: FALHOU"
    fi
    
    if [ "$BACKEND_OK" = true ]; then
        print_success "Backend: PASSOU"
    else
        print_error "Backend: FALHOU"
    fi
    
    if [ "$INTEGRATION_OK" = true ]; then
        print_success "Integração: PASSOU"
    else
        print_error "Integração: FALHOU"
    fi
    
    echo ""
    if [ "$RAG_OK" = true ] && [ "$BACKEND_OK" = true ] && [ "$INTEGRATION_OK" = true ]; then
        print_success "Todos os testes passaram!"
        exit 0
    else
        print_warning "Alguns testes falharam"
        print_info "Verifique se os serviços estão rodando:"
        print_info "  - RAG Service: docker-compose up rag-service"
        print_info "  - Backend: docker-compose up backend"
        exit 1
    fi
}

main

