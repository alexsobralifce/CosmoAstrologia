#!/usr/bin/env python3
"""
Script para substituir todas as chamadas ao RAG service por chamadas HTTP.
"""
import re

file_path = "app/api/interpretation.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Substituições
replacements = [
    # Substituir get_rag_service() por get_rag_client()
    (r'get_rag_service\(\)', 'get_rag_client()'),
    
    # Substituir rag_service = por rag_client = (mas não rag_service.)
    (r'rag_service = get_rag_client\(\)', 'rag_client = get_rag_client()'),
    (r'rag_service = ', 'rag_client = '),
    
    # Substituir if not rag_service: por if not rag_client:
    (r'if not rag_service:', 'if not rag_client:'),
    
    # Substituir chamadas síncronas por async
    (r'rag_service\.search\(([^)]+)\)', r'await rag_client.search(\1)'),
    (r'rag_service\.get_interpretation\(([^)]+)\)', r'await rag_client.get_interpretation(\1)'),
    
    # Para Groq, vamos precisar usar o RAG client que já tem Groq integrado
    # Então funções que usam rag_service.groq_client devem usar o RAG client
    # Mas isso é mais complexo, então vamos fazer uma substituição mais simples:
    # remover acesso direto ao groq_client e usar o RAG client
]

# Aplicar substituições
for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

# Salvar
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Substituições aplicadas!")

