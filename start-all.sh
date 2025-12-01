#!/bin/bash

# Script para iniciar frontend e backend simultaneamente
# Uso: ./start-all.sh

# Obter o diretório do script (raiz do projeto)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

echo "🚀 Iniciando Astrologia (Frontend + Backend)..."
echo ""

# Função para limpar processos ao sair
cleanup() {
    echo ""
    echo "🛑 Parando servidores..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    # Matar processos nas portas
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    exit
}

trap cleanup SIGINT SIGTERM

# Matar processos antigos nas portas
echo "🧹 Limpando processos antigos..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
sleep 1

# Verificar se Python está disponível
if ! command -v python3 &> /dev/null; then
    echo "❌ Erro: python3 não encontrado!"
    echo "   Instale Python 3.8+ primeiro."
    exit 1
fi

# Iniciar backend em background
echo "📦 Iniciando backend..."
cd "$SCRIPT_DIR/backend" || exit 1

if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Erro ao criar ambiente virtual!"
        exit 1
    fi
fi

source venv/bin/activate

if ! python -c "import fastapi" 2>/dev/null; then
    echo "📥 Instalando dependências do backend..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Erro ao instalar dependências do backend!"
        exit 1
    fi
    echo "✅ Dependências do backend instaladas!"
fi

if [ ! -f "astrologia.db" ]; then
    echo "🗄️  Criando banco de dados..."
    python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)" 2>&1
fi

echo "🚀 Iniciando servidor backend..."
python run.py > "$SCRIPT_DIR/backend.log" 2>&1 &
BACKEND_PID=$!

cd "$SCRIPT_DIR"

# Aguardar backend iniciar
echo "⏳ Aguardando backend iniciar..."
for i in {1..10}; do
    if curl -s http://localhost:8000 > /dev/null 2>&1; then
        echo "✅ Backend iniciado!"
        break
    fi
    sleep 1
done

# Verificar se backend está rodando
if ! curl -s http://localhost:8000 > /dev/null 2>&1; then
    echo "⚠️  Backend pode não estar rodando. Verifique backend.log"
    echo "📄 Últimas linhas do log:"
    tail -5 "$SCRIPT_DIR/backend.log" 2>/dev/null || echo "   (log ainda não disponível)"
fi

# Verificar se index.html existe
if [ ! -f "$SCRIPT_DIR/index.html" ]; then
    echo "❌ Erro: index.html não encontrado na raiz do projeto!"
    echo "   O Vite precisa de um arquivo index.html na raiz."
    exit 1
fi

# Verificar se node_modules existe (dependências instaladas)
if [ ! -d "$SCRIPT_DIR/node_modules" ]; then
    echo "📦 Instalando dependências do frontend..."
    cd "$SCRIPT_DIR" || exit 1
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Erro ao instalar dependências do frontend!"
        exit 1
    fi
    echo "✅ Dependências do frontend instaladas!"
fi

# Verificar se npm está disponível
if ! command -v npm &> /dev/null; then
    echo "❌ Erro: npm não encontrado!"
    echo "   Instale Node.js e npm primeiro."
    exit 1
fi

# Iniciar frontend
echo "🎨 Iniciando frontend..."
cd "$SCRIPT_DIR" || exit 1
npm run dev > "$SCRIPT_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!

# Aguardar frontend iniciar
echo "⏳ Aguardando frontend iniciar..."
for i in {1..15}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend iniciado!"
        break
    fi
    sleep 1
done

# Verificar se frontend está rodando
if ! curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "⚠️  Frontend pode não estar rodando. Verifique frontend.log"
    echo "📄 Últimas linhas do log:"
    tail -10 "$SCRIPT_DIR/frontend.log" 2>/dev/null || echo "   (log ainda não disponível)"
fi

echo ""
echo "✅ Servidores iniciados!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "📄 Logs:"
echo "   - Backend: tail -f backend.log"
echo "   - Frontend: tail -f frontend.log"
echo ""
echo "Pressione Ctrl+C para parar todos os servidores"
echo ""

# Aguardar processos
wait

