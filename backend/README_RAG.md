# Sistema RAG - Guia Rápido

## Instalação Rápida

```bash
# 1. Instalar dependências
cd backend
pip install -r requirements.txt

# 2. Construir índice (processa todos os PDFs)
python build_rag_index.py

# 3. Testar
python test_rag.py
```

## Uso Básico

### Via API

```bash
# Obter interpretação
curl -X POST http://localhost:8000/api/interpretation \
  -H "Content-Type: application/json" \
  -d '{
    "planet": "Sol",
    "sign": "Libra"
  }'

# Buscar documentos
curl "http://localhost:8000/api/interpretation/search?query=ascendente%20aquário&top_k=3"

# Status
curl http://localhost:8000/api/interpretation/status
```

### Via Python

```python
from app.services.rag_service import get_rag_service

rag = get_rag_service()

# Interpretação
result = rag.get_interpretation(planet="Sol", sign="Libra")
print(result['interpretation'])

# Busca
results = rag.search("ascendente em aquário", top_k=5)
for r in results:
    print(f"{r['source']} p.{r['page']}: {r['text'][:100]}")
```

## Estrutura de Arquivos

- `app/services/rag_service.py` - Serviço RAG principal
- `app/api/interpretation.py` - Endpoints da API
- `build_rag_index.py` - Script para construir índice
- `test_rag.py` - Testes
- `docs/` - PDFs de astrologia
- `rag_index.pkl` - Índice gerado (não versionado)

## Troubleshooting

**Erro: "Dependências não instaladas"**
```bash
pip install sentence-transformers scikit-learn PyPDF2 numpy
```

**Erro: "Índice não encontrado"**
```bash
python build_rag_index.py
```

**PDFs não processados**
- Verifique se estão em `backend/docs/`
- Alguns PDFs podem ser imagens (não têm texto)

