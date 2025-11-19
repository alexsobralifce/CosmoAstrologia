#!/bin/bash

# Script para iniciar frontend e backend simultaneamente
# Uso: ./start-all.sh

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

# Iniciar backend em background
echo "📦 Iniciando backend..."
cd backend || exit 1

if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

source venv/bin/activate

if ! python -c "import fastapi" 2>/dev/null; then
    echo "📥 Instalando dependências do backend..."
    pip install -r requirements.txt
fi

if [ ! -f "astrologia.db" ]; then
    echo "🗄️  Criando banco de dados..."
    python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)" 2>&1
fi

echo "🚀 Iniciando servidor backend..."
python run.py > ../backend.log 2>&1 &
BACKEND_PID=$!

cd ..

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
    tail -5 backend.log
fi

# Iniciar frontend
echo "🎨 Iniciando frontend..."
npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!

# Aguardar frontend iniciar
echo "⏳ Aguardando frontend iniciar..."
sleep 3

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
