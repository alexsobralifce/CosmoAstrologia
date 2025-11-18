#!/bin/bash
# Script para configurar o ambiente do backend

echo "=== Configurando ambiente do Backend ==="

# Criar venv se não existir
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar venv
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Instalar dependências
echo "Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Ambiente configurado com sucesso!"
echo "Para ativar o ambiente virtual:"
echo "  source venv/bin/activate"

