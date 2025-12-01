#!/bin/bash
# Script para instalar ML dependencies em runtime

echo "[ML-DEPS] Iniciando instalação de dependências ML em background..."

pip install --no-cache-dir \
    --timeout=600 \
    --retries=5 \
    fastembed>=0.2.0 \
    PyPDF2==3.0.1

if [ $? -eq 0 ]; then
    echo "[ML-DEPS] ✅ Dependências ML instaladas com sucesso!"
else
    echo "[ML-DEPS] ⚠️ Erro ao instalar dependências ML. RAG pode não funcionar."
fi

