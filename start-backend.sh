#!/bin/bash

# Script para iniciar o backend do Astrologia
# Uso: ./start-backend.sh

cd "$(dirname "$0")/backend" || exit 1

echo "🚀 Iniciando backend do Astrologia..."
echo ""

# Matar processos antigos na porta 8000
echo "🧹 Limpando processos antigos na porta 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
sleep 1

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "❌ Ambiente virtual não encontrado. Criando..."
    python3 -m venv venv
    echo "✅ Ambiente virtual criado!"
fi

# Ativar ambiente virtual
echo "📦 Ativando ambiente virtual..."
source venv/bin/activate

# Verificar se as dependências estão instaladas
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📥 Instalando dependências..."
    pip install -r requirements.txt
    echo "✅ Dependências instaladas!"
fi

# Verificar se o banco de dados existe, se não, criar
if [ ! -f "astrologia.db" ]; then
    echo "🗄️  Criando banco de dados..."
    python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"
    echo "✅ Banco de dados criado!"
fi

echo ""
echo "✅ Backend pronto!"
echo "🌐 Servidor rodando em: http://localhost:8000"
echo "📚 Documentação da API: http://localhost:8000/docs"
echo ""
echo "Pressione Ctrl+C para parar o servidor"
echo ""

# Iniciar o servidor
python run.py
